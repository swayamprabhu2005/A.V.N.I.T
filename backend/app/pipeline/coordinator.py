import cv2
import os
import base64
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from .vehicle_detector import VehicleDetector
from .tracker import VehicleTracker
from .plate_detector import PlateDetector
from .color_classifier import VehicleColorClassifier
from .ocr_engine import PlateTemporalAggregator, normalize_indian_plate
from .risk_engine import evaluate_identity_risk
from ..database import log_event

SNAPSHOTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

class PipelineCoordinator:
    """
    Main AVNIT Computer Vision Pipeline Engine.
    Orchestrates vehicle detection, tracking, anatomical plate localization,
    OCR character recognition, color classification, explainable Bayesian risk evaluation,
    and Best-Frame Vehicle Snapshot extraction for continuous multi-vehicle traffic.
    """
    def __init__(self):
        print("[AVNIT] Initializing Pipeline Coordinator...")
        self.vehicle_detector = VehicleDetector()
        self.tracker = VehicleTracker()
        self.plate_detector = PlateDetector()
        self.color_classifier = VehicleColorClassifier()
        self.temporal_ocr = PlateTemporalAggregator()

        # Track metadata cache: track_id -> dict(locked, best_conf, snapshot_base64, risk_result)
        self.track_cache: Dict[int, Dict[str, Any]] = {}

    def _encode_image_base64(self, img: np.ndarray, max_dim: int = 400) -> str:
        """Converts an OpenCV image crop to a compact base64 JPEG string for the UI."""
        if img is None or img.size == 0:
            return ""
        try:
            h, w = img.shape[:2]
            if max(h, w) > max_dim:
                scale = max_dim / float(max(h, w))
                img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            _, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
            encoded = base64.b64encode(buffer).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
        except Exception as e:
            print(f"[AVNIT] Base64 encoding warning: {e}")
            return ""

    def process_frame(self, frame: np.ndarray, simulated_plate: Optional[str] = None) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Processes a single video frame with Best-Frame Vehicle Snapshot extraction.
        Returns: (annotated_frame, list_of_vehicle_telemetry)
        """
        if frame is None or frame.size == 0:
            return frame, []

        annotated_frame = frame.copy()
        h_frame, w_frame, _ = frame.shape
        frame_area = float(h_frame * w_frame)

        # Automatic Night Mode Detection (Luminance < 50 or Saturation < 18)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mean_val = float(np.mean(hsv_frame[:, :, 2]))
        mean_sat = float(np.mean(hsv_frame[:, :, 1]))
        is_night_mode = bool(mean_val < 50.0 or mean_sat < 18.0)

        # 1. Vehicle Detection
        vehicle_detections = self.vehicle_detector.detect(frame)

        # 2. Multi-Object Tracking (ByteTrack)
        active_tracks = self.tracker.update(vehicle_detections)

        frame_telemetry = []

        for track in active_tracks:
            track_id = track["track_id"]
            bbox = track["bbox"]  # [x1, y1, x2, y2]
            vehicle_type = track["class_name"]

            x1, y1, x2, y2 = bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_frame, x2), min(h_frame, y2)
            vw = x2 - x1
            vh = y2 - y1
            veh_area = float(vw * vh)
            
            vehicle_crop = frame[y1:y2, x1:x2]
            if vehicle_crop.size == 0:
                continue

            # Initialize track state in cache if new
            if track_id not in self.track_cache:
                self.track_cache[track_id] = {
                    "locked": False,
                    "best_conf": 0.0,
                    "best_plate": "DETECTING...",
                    "observed_color": "unassigned",
                    "snapshot_base64": "",
                    "plate_crop_base64": "",
                    "risk_result": None
                }

            t_state = self.track_cache[track_id]

            # 3. Vehicle Color Classification
            observed_color, color_conf = self.color_classifier.predict(vehicle_crop)
            if observed_color and observed_color != "unassigned":
                t_state["observed_color"] = observed_color

            # 4. License Plate Detection (with anatomical bumper localization & RapidOCR)
            plate_crop, plate_box, plate_conf, direct_text = self.plate_detector.detect(vehicle_crop)

            # 5. Plate OCR Reading
            raw_plate_text = ""
            ocr_conf = 0.0

            if simulated_plate:
                raw_plate_text = simulated_plate
                ocr_conf = 0.98
            elif direct_text:
                raw_plate_text = direct_text
                ocr_conf = plate_conf
            elif plate_crop is not None and plate_crop.size > 0:
                # Run OCR on plate crop via detector's rapid_ocr if available
                if self.plate_detector.rapid_ocr:
                    try:
                        results, _ = self.plate_detector.rapid_ocr(plate_crop)
                        if results:
                            best_line = max(results, key=lambda x: x[2])
                            raw_plate_text = best_line[1].replace(" ", "").upper()
                            ocr_conf = float(best_line[2])
                    except Exception as e:
                        print(f"[AVNIT] Plate crop OCR warning: {e}")

            if raw_plate_text:
                self.temporal_ocr.add_observation(track_id, raw_plate_text, ocr_conf)

            # Retrieve temporally aggregated stable plate reading
            stable_plate, stable_conf = self.temporal_ocr.get_stable_plate(track_id)
            if not stable_plate:
                stable_plate = t_state.get("best_plate", "DETECTING...")
                stable_conf = t_state.get("best_conf", 0.0)

            # 6. Best-Frame Vehicle Snapshot Trigger
            # Triggers when vehicle reaches clear foreground (area >= 8% of frame or width >= 25%)
            # AND plate has been read with good confidence.
            is_foreground = (veh_area / frame_area >= 0.08) or (vw >= w_frame * 0.25)
            is_confident_plate = (stable_plate != "DETECTING..." and stable_conf >= 0.50)

            if is_foreground and is_confident_plate:
                if not t_state["locked"] or stable_conf > t_state["best_conf"]:
                    t_state["best_plate"] = stable_plate
                    t_state["best_conf"] = stable_conf
                    t_state["snapshot_base64"] = self._encode_image_base64(vehicle_crop, max_dim=480)
                    if plate_crop is not None and plate_crop.size > 0:
                        t_state["plate_crop_base64"] = self._encode_image_base64(plate_crop, max_dim=240)

                    # 7. Evaluate Risk & Cross-Reference VAHAN Registry
                    risk_result = evaluate_identity_risk(
                        plate_number=stable_plate,
                        ocr_confidence=stable_conf,
                        observed_type=vehicle_type,
                        observed_color=t_state["observed_color"],
                        is_night_mode=is_night_mode
                    )
                    t_state["risk_result"] = risk_result
                    t_state["locked"] = True

                    # Log verified incident to database
                    try:
                        log_event(
                            track_id=track_id,
                            plate_number=stable_plate,
                            ocr_confidence=stable_conf,
                            observed_type=vehicle_type,
                            observed_color=t_state["observed_color"],
                            risk_score=risk_result["risk_score"],
                            risk_level=risk_result["risk_level"],
                            reason=risk_result["reason"]
                        )
                        print(f"[AVNIT Snapshot] Locked Track #{track_id}: {stable_plate} ({vehicle_type}, {t_state['observed_color']}) -> {risk_result['risk_level']} ({risk_result['risk_score']}%)")
                    except Exception as e:
                        print(f"[AVNIT] Event log warning: {e}")
            elif not t_state["locked"] and stable_plate != "DETECTING...":
                # Continuous evaluation even before final foreground lock
                t_state["risk_result"] = evaluate_identity_risk(
                    plate_number=stable_plate,
                    ocr_confidence=stable_conf,
                    observed_type=vehicle_type,
                    observed_color=t_state["observed_color"],
                    is_night_mode=is_night_mode
                )

            current_risk = t_state.get("risk_result")
            display_plate = t_state.get("best_plate") if t_state["locked"] else stable_plate
            display_color = t_state.get("observed_color", observed_color)

            # Determine bounding box color
            if current_risk:
                if current_risk["risk_level"] == "GREEN":
                    box_color = (0, 220, 60)       # Emerald Green (Verified)
                elif current_risk["risk_level"] == "YELLOW":
                    box_color = (0, 180, 255)     # Amber (Review)
                else:
                    box_color = (0, 0, 240)       # Crimson Red (Tampering)
            else:
                box_color = (255, 175, 0)         # Amber during initial scan

            # Draw vehicle bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)

            # Draw vehicle tag label
            status_text = "LOCKED" if t_state["locked"] else "SCANNING"
            tag_label = f"ID #{track_id} | {vehicle_type.upper()} ({display_color.upper()}) [{status_text}]"
            (tw, th), _ = cv2.getTextSize(tag_label, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
            cv2.rectangle(annotated_frame, (x1, max(0, y1 - 22)), (x1 + tw + 10, y1), box_color, -1)
            cv2.putText(annotated_frame, tag_label, (x1 + 5, max(14, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 2, cv2.LINE_AA)

            # Draw license plate bounding box directly on bumper
            if plate_box:
                px, py, pw, ph = plate_box
                abs_px1 = x1 + px
                abs_py1 = y1 + py
                abs_px2 = abs_px1 + pw
                abs_py2 = abs_py1 + ph
                cv2.rectangle(annotated_frame, (abs_px1, abs_py1), (abs_px2, abs_py2), (0, 240, 255), 2)
                
                plate_label = f"PLATE: {display_plate}"
                cv2.putText(annotated_frame, plate_label, (abs_px1, max(12, abs_py1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 240, 255), 1, cv2.LINE_AA)

            # Telemetry object dispatched to WebSocket
            telemetry = {
                "track_id": track_id,
                "bbox": [x1, y1, x2, y2],
                "vehicle_type": vehicle_type,
                "observed_color": display_color,
                "plate_number": display_plate,
                "ocr_confidence": round(float(stable_conf), 2),
                "risk_result": current_risk,
                "is_night_mode": is_night_mode,
                "is_locked": t_state["locked"],
                "snapshot_image": t_state.get("snapshot_base64", ""),
                "plate_image": t_state.get("plate_crop_base64", "")
            }
            frame_telemetry.append(telemetry)

        return annotated_frame, frame_telemetry
