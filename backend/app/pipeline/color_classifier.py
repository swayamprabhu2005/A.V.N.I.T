import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from typing import Tuple
from ..config import COLOR_CLASSIFIER_WEIGHTS

COLOR_CLASSES = ['white', 'black', 'silver_grey', 'red', 'blue', 'yellow', 'green', 'brown']

# HSV Color ranges for fallback rule-based classifier
HSV_COLOR_RANGES = [
    ("black", np.array([0, 0, 0]), np.array([180, 255, 45])),
    ("white", np.array([0, 0, 195]), np.array([180, 40, 255])),
    ("silver_grey", np.array([0, 0, 45]), np.array([180, 50, 195])),
    ("red", np.array([0, 70, 50]), np.array([10, 255, 255])),
    ("red", np.array([170, 70, 50]), np.array([180, 255, 255])),
    ("yellow", np.array([20, 70, 50]), np.array([35, 255, 255])),
    ("green", np.array([36, 50, 50]), np.array([85, 255, 255])),
    ("blue", np.array([90, 50, 50]), np.array([130, 255, 255])),
    ("brown", np.array([10, 50, 20]), np.array([20, 200, 150]))
]

class VehicleColorClassifier:
    def __init__(self):
        self.device = torch.device("cpu")
        self.model = None
        self.is_custom_model_loaded = False
        self._load_model()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _load_model(self):
        if os.path.exists(COLOR_CLASSIFIER_WEIGHTS):
            try:
                print(f"[AVNIT] Loading Colab-trained Color Classifier from: {COLOR_CLASSIFIER_WEIGHTS}")
                checkpoint = torch.load(COLOR_CLASSIFIER_WEIGHTS, map_location=self.device)
                
                # Rebuild MobileNetV3-Small
                model = models.mobilenet_v3_small(weights=None)
                in_features = model.classifier[3].in_features
                model.classifier[3] = nn.Linear(in_features, len(COLOR_CLASSES))
                
                state_dict = checkpoint.get("state_dict", checkpoint)
                model.load_state_dict(state_dict)
                model.eval()
                self.model = model
                self.is_custom_model_loaded = True
                print("[AVNIT] Successfully loaded Colab Color Classifier model!")
            except Exception as e:
                print(f"[AVNIT] Warning: Could not load {COLOR_CLASSIFIER_WEIGHTS}: {e}. Using CV fallback.")
                self.model = None
        else:
            print(f"[AVNIT] Info: Colab color weights not found at {COLOR_CLASSIFIER_WEIGHTS}. Using fast CV fallback.")

    def predict_cv_fallback(self, bgr_image: np.ndarray) -> Tuple[str, float]:
        """HSV and Histogram Color Extraction (Fast, CPU-native, 0 MB VRAM)"""
        h, w, _ = bgr_image.shape
        # Sample the central 50% of the vehicle crop to ignore road, background and sky
        ymin, ymax = int(h * 0.25), int(h * 0.75)
        xmin, xmax = int(w * 0.25), int(w * 0.75)
        center_crop = bgr_image[ymin:ymax, xmin:xmax]
        
        if center_crop.size == 0:
            center_crop = bgr_image

        hsv = cv2.cvtColor(center_crop, cv2.COLOR_BGR2HSV)
        
        color_counts = {}
        total_pixels = center_crop.shape[0] * center_crop.shape[1]

        for color_name, lower, upper in HSV_COLOR_RANGES:
            mask = cv2.inRange(hsv, lower, upper)
            count = cv2.countNonZero(mask)
            color_counts[color_name] = color_counts.get(color_name, 0) + count

        if not color_counts or max(color_counts.values()) == 0:
            return "white", 0.50

        best_color = max(color_counts, key=color_counts.get)
        confidence = min(0.95, color_counts[best_color] / max(1, total_pixels) + 0.35)
        return best_color, round(confidence, 2)

    def predict(self, bgr_image: np.ndarray) -> Tuple[str, float]:
        """Classifies vehicle color from image crop."""
        if bgr_image is None or bgr_image.size == 0:
            return "unknown", 0.0

        if self.model and self.is_custom_model_loaded:
            try:
                rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_image)
                tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    logits = self.model(tensor)
                    probs = torch.softmax(logits, dim=1)[0]
                    conf, pred_idx = torch.max(probs, dim=0)
                    predicted_color = COLOR_CLASSES[pred_idx.item()]
                    return predicted_color, round(conf.item(), 2)
            except Exception as e:
                print(f"[AVNIT] Error during neural color inference: {e}. Falling back to CV.")

        return self.predict_cv_fallback(bgr_image)
