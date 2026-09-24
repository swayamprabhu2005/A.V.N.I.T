import os
import cv2
import numpy as np
from typing import List, Dict, Any
from ..config import YOLO_VEHICLE_WEIGHTS

# COCO vehicle class mappings
COCO_VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

class VehicleDetector:
    def __init__(self):
        self.model = None
        self._init_model()

    def _init_model(self):
        try:
            from ultralytics import YOLO
            # If yolov8n.pt exists locally, load it; otherwise YOLO downloads it automatically
            weight_path = str(YOLO_VEHICLE_WEIGHTS) if os.path.exists(YOLO_VEHICLE_WEIGHTS) else "yolov8n.pt"
            print(f"[AVNIT] Initializing YOLOv8 Vehicle Detector ({weight_path})...")
            self.model = YOLO(weight_path)
            print("[AVNIT] YOLOv8 Vehicle Detector successfully loaded.")
        except Exception as e:
            print(f"[AVNIT] Warning: Could not initialize YOLOv8: {e}")
            self.model = None

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.35) -> List[Dict[str, Any]]:
        """
        Runs inference on the frame and filters vehicle classes: car, motorcycle, bus, truck.
        Returns: list of dicts with keys: bbox [x1, y1, x2, y2], class_name, confidence
        """
        if self.model is None or frame is None or frame.size == 0:
            return []

        vehicles = []
        try:
            results = self.model.predict(
                source=frame,
                classes=list(COCO_VEHICLE_CLASSES.keys()),
                conf=conf_threshold,
                verbose=False
            )
            
            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    cls_id = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    class_name = COCO_VEHICLE_CLASSES.get(cls_id, "car")
                    
                    vehicles.append({
                        "bbox": xyxy.tolist(),
                        "class_name": class_name,
                        "confidence": round(conf, 2)
                    })
        except Exception as e:
            print(f"[AVNIT] Error during vehicle detection: {e}")

        return vehicles
