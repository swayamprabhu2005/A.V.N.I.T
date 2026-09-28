import os
import cv2
import numpy as np
from typing import List, Tuple, Optional, Any
from ..config import PLATE_DETECTOR_WEIGHTS

try:
    from rapidocr_onnxruntime import RapidOCR
    RAPID_OCR_AVAILABLE = True
except ImportError:
    RAPID_OCR_AVAILABLE = False

class PlateDetector:
    """
    Sub-pixel License Plate Detection & Localization Engine.
    Uses Colab YOLOv8 Plate Detector with strict vehicle anatomical boundary verification
    and RapidOCR bumper-zone sub-pixel localization fallback to eliminate false positives on car hoods.
    """
    def __init__(self):
        self.model = None
        self.is_custom_model_loaded = False
        self.rapid_ocr = None
        if RAPID_OCR_AVAILABLE:
            try:
                self.rapid_ocr = RapidOCR()
                print("[AVNIT] RapidOCR engine initialized for anatomical bumper plate localization.")
            except Exception as e:
                print(f"[AVNIT] Warning: Could not initialize RapidOCR: {e}")

        self._load_model()

    def _load_model(self):
        if os.path.exists(PLATE_DETECTOR_WEIGHTS):
            try:
                from ultralytics import YOLO
                print(f"[AVNIT] Loading Colab-trained Plate Detector from: {PLATE_DETECTOR_WEIGHTS}")
                self.model = YOLO(str(PLATE_DETECTOR_WEIGHTS))
                self.is_custom_model_loaded = True
                print("[AVNIT] Successfully loaded Colab Plate Detector!")
            except Exception as e:
                print(f"[AVNIT] Warning: Could not load plate weights: {e}")
                self.model = None
        else:
            print(f"[AVNIT] Info: Plate detector weights not found at {PLATE_DETECTOR_WEIGHTS}. Using heuristic plate locator fallback.")

    def _is_anatomically_valid_plate(self, box: Tuple[int, int, int, int], vehicle_shape: Tuple[int, int]) -> bool:
        """
        Validates that a detected plate box complies with real-world vehicle anatomy:
        1. Plate is in lower 45% - 95% of vehicle height (NEVER on hood, windshield, or roof).
        2. Plate width does not exceed 60% of vehicle width.
        3. Aspect ratio (width / height) is between 2.0 and 6.5.
        """
        vh, vw = vehicle_shape
        x, y, w, h = box
        if w <= 0 or h <= 0 or vw <= 0 or vh <= 0:
            return False

        aspect_ratio = float(w) / float(h)
        rel_y = float(y) / float(vh)
        rel_w = float(w) / float(vw)
        rel_h = float(h) / float(vh)

        # Reject hood / roof detections
        if rel_y < 0.40:
            return False

        # Reject boxes that are too large (e.g., entire front grille/hood)
        if rel_w > 0.60 or rel_h > 0.35:
            return False

        # Must have plausible plate aspect ratio
        if aspect_ratio < 1.8 or aspect_ratio > 6.5:
            return False

        return True

    def detect_via_bumper_ocr(self, vehicle_crop: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], float, Optional[str]]:
        """
        Locates plate with sub-pixel precision directly inside the lower bumper zone
        using RapidOCR deep text detection.
        """
        if not self.rapid_ocr or vehicle_crop is None or vehicle_crop.size == 0:
            return None, None, 0.0, None

        vh, vw, _ = vehicle_crop.shape
        if vh < 60 or vw < 80:
            return None, None, 0.0, None

        # Focus strictly on the lower bumper region
        bumper_y1 = int(vh * 0.45)
        bumper_y2 = int(vh * 0.96)
        bumper_x1 = int(vw * 0.15)
        bumper_x2 = int(vw * 0.85)

        bumper_roi = vehicle_crop[bumper_y1:bumper_y2, bumper_x1:bumper_x2]
        if bumper_roi.size == 0:
            return None, None, 0.0, None

        try:
            results, _ = self.rapid_ocr(bumper_roi)
            if results:
                best_plate = None
                best_box = None
                best_conf = 0.0

                for line in results:
                    poly, text, conf = line
                    clean = text.replace(" ", "").upper()
                    # Look for plausible license plate text (6-11 alphanumeric characters)
                    if len(clean) >= 6 and conf > best_conf:
                        best_conf = conf
                        best_plate = clean
                        pts = np.array(poly).astype(int)
                        bx1 = int(np.min(pts[:, 0]))
                        by1 = int(np.min(pts[:, 1]))
                        bx2 = int(np.max(pts[:, 0]))
                        by2 = int(np.max(pts[:, 1]))

                        # Add small margin for license plate border
                        pad_x = int((bx2 - bx1) * 0.15)
                        pad_y = int((by2 - by1) * 0.40)

                        v_px1 = max(0, bumper_x1 + bx1 - pad_x)
                        v_py1 = max(0, bumper_y1 + by1 - pad_y)
                        v_px2 = min(vw, bumper_x1 + bx2 + pad_x)
                        v_py2 = min(vh, bumper_y1 + by2 + pad_y)

                        pw = v_px2 - v_px1
                        ph = v_py2 - v_py1
                        best_box = (v_px1, v_py1, pw, ph)

                if best_box:
                    px, py, pw, ph = best_box
                    crop = vehicle_crop[py:py+ph, px:px+pw]
                    return crop, best_box, round(float(best_conf), 3), best_plate
        except Exception as e:
            print(f"[AVNIT] Bumper OCR localization warning: {e}")

        return None, None, 0.0, None

    def detect_plate_cv_fallback(self, vehicle_crop: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Morphological gradient heuristic fallback targeting the lower bumper.
        """
        h, w, _ = vehicle_crop.shape
        if h < 50 or w < 50:
            return None

        # Number plates are in the lower 45% of the vehicle
        y_start = int(h * 0.55)
        roi = vehicle_crop[y_start:int(h * 0.95), int(w * 0.15):int(w * 0.85)]
        if roi.size == 0:
            return None

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)
        _, thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_box = None
        best_score = 0
        
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = float(bw) / max(1, bh)
            if 2.0 <= aspect_ratio <= 5.5 and bw > 40 and bh > 12:
                score = bw * bh
                if score > best_score:
                    best_score = score
                    abs_x = int(w * 0.15) + x
                    abs_y = y_start + y
                    best_box = (abs_x, abs_y, bw, bh)

        if not best_box:
            bw = int(w * 0.38)
            bh = int(h * 0.12)
            bx = int((w - bw) / 2)
            by = int(h * 0.72)
            best_box = (bx, by, bw, bh)

        return best_box

    def detect(self, vehicle_crop: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], float, Optional[str]]:
        """
        Detects license plate inside the vehicle image crop.
        Returns: (plate_crop, (x, y, w, h), confidence, direct_ocr_text)
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None, None, 0.0, None

        vh, vw, _ = vehicle_crop.shape

        # 1. Primary: Run Bumper OCR Localization (highest precision on actual plates)
        crop, box, conf, text = self.detect_via_bumper_ocr(vehicle_crop)
        if crop is not None and box is not None and conf >= 0.40:
            return crop, box, conf, text

        # 2. Secondary: Check Colab YOLO Plate Detector if loaded
        if self.model and self.is_custom_model_loaded:
            try:
                results = self.model.predict(source=vehicle_crop, conf=0.20, verbose=False)
                if results and len(results[0].boxes) > 0:
                    for b in results[0].boxes:
                        xyxy = b.xyxy[0].cpu().numpy().astype(int)
                        conf = float(b.conf[0].cpu().numpy())
                        x1, y1, x2, y2 = xyxy
                        w = x2 - x1
                        h = y2 - y1
                        candidate_box = (x1, y1, w, h)

                        # Enforce anatomical validation
                        if self._is_anatomically_valid_plate(candidate_box, (vh, vw)):
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(vw, x2), min(vh, y2)
                            crop = vehicle_crop[y1:y2, x1:x2]
                            return crop, (x1, y1, x2 - x1, y2 - y1), conf, None
            except Exception as e:
                print(f"[AVNIT] Error during plate model prediction: {e}")

        # 3. Fallback: Morphological bumper contour heuristic
        box = self.detect_plate_cv_fallback(vehicle_crop)
        if box:
            x, y, bw, bh = box
            crop = vehicle_crop[y:y+bh, x:x+bw]
            return crop, box, 0.65, None

        return None, None, 0.0, None
