import os
import cv2
import numpy as np
from typing import List, Tuple, Optional
from ..config import PLATE_DETECTOR_WEIGHTS

class PlateDetector:
    def __init__(self):
        self.model = None
        self.is_custom_model_loaded = False
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

    def detect_plate_cv_fallback(self, vehicle_crop: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Heuristic fallback to locate plate region if Colab model is not yet placed.
        Scans lower 40% of the vehicle for high-gradient rectangular contours.
        """
        h, w, _ = vehicle_crop.shape
        if h < 50 or w < 50:
            return None

        # Number plates are typically in the lower 45% of the vehicle
        y_start = int(h * 0.55)
        roi = vehicle_crop[y_start:h, :]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Morphological gradient to detect plate text edges
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
            # Standard Indian plate aspect ratio is between 2.0 and 5.5
            if 2.0 <= aspect_ratio <= 5.5 and bw > 40 and bh > 12:
                score = bw * bh
                if score > best_score:
                    best_score = score
                    best_box = (x, y_start + y, bw, bh)

        # Fallback to central lower box if no contour passed
        if not best_box:
            bw = int(w * 0.40)
            bh = int(h * 0.16)
            bx = int((w - bw) / 2)
            by = int(h * 0.70)
            best_box = (bx, by, bw, bh)

        return best_box

    def detect(self, vehicle_crop: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], float]:
        """
        Detects license plate inside the vehicle image crop.
        Returns: (plate_crop, (x, y, w, h), confidence)
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None, None, 0.0

        h, w, _ = vehicle_crop.shape

        if self.model and self.is_custom_model_loaded:
            try:
                results = self.model.predict(source=vehicle_crop, conf=0.25, verbose=False)
                if results and len(results[0].boxes) > 0:
                    box = results[0].boxes[0]
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0].cpu().numpy())
                    x1, y1, x2, y2 = xyxy
                    # Clamp
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    crop = vehicle_crop[y1:y2, x1:x2]
                    return crop, (x1, y1, x2 - x1, y2 - y1), conf
            except Exception as e:
                print(f"[AVNIT] Error during plate model prediction: {e}")

        # Fallback heuristic
        box = self.detect_plate_cv_fallback(vehicle_crop)
        if box:
            x, y, bw, bh = box
            crop = vehicle_crop[y:y+bh, x:x+bw]
            return crop, box, 0.75

        return None, None, 0.0
