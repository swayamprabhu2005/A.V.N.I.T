import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .vehicle_detector import VehicleDetector
from .tracker import VehicleTracker
from .plate_detector import PlateDetector
from .color_classifier import VehicleColorClassifier
from .ocr_engine import PlateTemporalAggregator, normalize_indian_plate
from .risk_engine import evaluate_identity_risk
from ..database import log_event

class PipelineCoordinator:
    """
    Main AVNIT Computer Vision Pipeline Engine.
    Orchestrates vehicle detection, tracking, plate localization, OCR,
    color classification, and identity risk evaluation.
    """
    def __init__(self):
        print("[AVNIT] Initializing Pipeline Coordinator...")
        self.vehicle_detector = VehicleDetector()
        self.tracker = VehicleTracker()
        self.plate_detector = PlateDetector()
        self.color_classifier = VehicleColorClassifier()
        self.temporal_ocr = PlateTemporalAggregator()
        self.easyocr_reader = None
        self._init_ocr()

        # Cache of evaluated track events to prevent duplicate DB alerts for the same continuous pass
        self.evaluated_tracks = {}  # track_id -> result_dict

    def _init_ocr(self):
        try:
            import easyocr
            print("[AVNIT] Initializing EasyOCR CPU engine...")
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            print("[AVNIT] EasyOCR CPU engine initialized successfully.")
        except Exception as e:
            print(f"[AVNIT] Warning: EasyOCR not available ({e}). Fallback to simulation/text parsing.")

    def run_ocr(self, plate_crop: np.ndarray) -> Tuple[str, float]:
        """Runs OCR on the cropped license plate image."""
        if plate_crop is None or plate_crop.size == 0 or self.easyocr_reader is None:
            return "", 0.0

        try:
            # Preprocess plate crop: grayscale + contrast stretch
            gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            results = self.easyocr_reader.readtext(enhanced)
            if not results:
                # Try raw image
                results = self.easyocr_reader.readtext(plate_crop)

            if results:
                # Join recognized lines and take maximum confidence
                text_pieces = [res[1] for res in results]
                confidences = [res[2] for res in results]
                raw_text = "".join(text_pieces)
                avg_conf = sum(confidences) / len(confidences)
                return raw_text, round(avg_conf, 2)
        except Exception as e:
            print(f"[AVNIT] OCR exception: {e}")

        return "", 0.0

    def process_frame(self, frame: np.ndarray, simulated_plate: Optional[str] = None) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Processes a single video frame.
        Draws bounding boxes and status HUD directly on the frame.
        Returns: (annotated_frame, list_of_vehicle_telemetry)
        """
        if frame is None or frame.size == 0:
            return frame, []

        annotated_frame = frame.copy()
        h_frame, w_frame, _ = frame.shape

        # 1. Vehicle Detection
        vehicle_detections = self.vehicle_detector.detect(frame)

        # 2. Tracking
        active_tracks = self.tracker.update(vehicle_detections)

        frame_telemetry = []

        for track in active_tracks:
            track_id = track["track_id"]
            bbox = track["bbox"]  # [x1, y1, x2, y2]
            vehicle_type = track["class_name"]

            x1, y1, x2, y2 = bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_frame, x2), min(h_frame, y2)
            
            vehicle_crop = frame[y1:y2, x1:x2]
            if vehicle_crop.size == 0:
                continue

            # 3. Vehicle Color Classification
            observed_color, color_conf = self.color_classifier.predict(vehicle_crop)

            # 4. Number Plate Detection
            plate_crop, plate_box, plate_conf = self.plate_detector.detect(vehicle_crop)

            # 5. OCR & Normalization
            raw_plate_text = ""
            ocr_conf = 0.0

            if simulated_plate:
                # Used in controlled demo scenario testing
                raw_plate_text = simulated_plate
                ocr_conf = 0.96
            elif plate_crop is not None and plate_crop.size > 0:
                raw_plate_text, ocr_conf = self.run_ocr(plate_crop)

            if raw_plate_text:
                self.temporal_ocr.add_observation(track_id, raw_plate_text, ocr_conf)

            # Retrieve temporally aggregated stable plate reading
            stable_plate, stable_conf = self.temporal_ocr.get_stable_plate(track_id)
            if not stable_plate:
                stable_plate = "DETECTING..."
                stable_conf = 0.0

            # 6. Risk Engine Evaluation
            risk_result = None
            if stable_plate != "DETECTING...":
                risk_result = evaluate_identity_risk(
                    plate_number=stable_plate,
                    ocr_confidence=stable_conf,
                    observed_type=vehicle_type,
                    observed_color=observed_color
                )

                # Log event to database once per vehicle pass if confidence is reliable
                if track_id not in self.evaluated_tracks and stable_conf >= 0.40:
                    self.evaluated_tracks[track_id] = risk_result
                    log_event(
                        track_id=track_id,
                        plate_number=stable_plate,
                        ocr_confidence=stable_conf,
                        observed_type=vehicle_type,
                        observed_color=observed_color,
                        risk_score=risk_result["risk_score"],
                        risk_level=risk_result["risk_level"],
                        reason=risk_result["reason"]
                    )

            # Visual Annotation
            # Determine color for bounding box: Green = Valid, Yellow = Review, Red = Tampering
            if risk_result:
                if risk_result["risk_level"] == "GREEN":
                    box_color = (0, 255, 64)       # Bright Green
                elif risk_result["risk_level"] == "YELLOW":
                    box_color = (0, 215, 255)     # Amber / Yellow
                else:
                    box_color = (0, 0, 255)       # Red
            else:
                box_color = (255, 175, 0)         # Cyan/Blue during detection

            # Draw vehicle bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)

            # Draw vehicle label tag
            tag_label = f"ID #{track_id} | {vehicle_type.upper()} ({observed_color.upper()})"
            (tw, th), _ = cv2.getTextSize(tag_label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(annotated_frame, (x1, y1 - 22), (x1 + tw + 10, y1), box_color, -1)
            cv2.putText(annotated_frame, tag_label, (x1 + 5, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)

            # Draw plate bounding box if localized
            if plate_box:
                px, py, pw, ph = plate_box
                abs_px1 = x1 + px
                abs_py1 = y1 + py
                abs_px2 = abs_px1 + pw
                abs_py2 = abs_py1 + ph
                cv2.rectangle(annotated_frame, (abs_px1, abs_py1), (abs_px2, abs_py2), (0, 255, 255), 2)
                
                plate_label = f"PLATE: {stable_plate}"
                cv2.putText(annotated_frame, plate_label, (abs_px1, abs_py1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

            # Telemetry for frontend state
            telemetry = {
                "track_id": track_id,
                "bbox": [x1, y1, x2, y2],
                "vehicle_type": vehicle_type,
                "observed_color": observed_color,
                "plate_number": stable_plate,
                "ocr_confidence": stable_conf,
                "risk_result": risk_result
            }
            frame_telemetry.append(telemetry)

        return annotated_frame, frame_telemetry
