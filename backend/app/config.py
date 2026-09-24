import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
TEST_SAMPLES_DIR = BASE_DIR / "test_samples"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEST_SAMPLES_DIR, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "avnit.db"

# Model Paths
YOLO_VEHICLE_WEIGHTS = MODELS_DIR / "yolov8n.pt"
PLATE_DETECTOR_WEIGHTS = MODELS_DIR / "plate_detector.pt"
COLOR_CLASSIFIER_WEIGHTS = MODELS_DIR / "color_classifier.pt"
PLATE_OCR_WEIGHTS = MODELS_DIR / "plate_ocr_crnn.pt"

# Risk Scoring Weights (Total = 1.0)
WEIGHT_VEHICLE_TYPE = 0.35
WEIGHT_COLOR = 0.20
WEIGHT_OCR_CONFIDENCE = 0.20
WEIGHT_MAKE_MODEL = 0.25

# Risk Thresholds
THRESHOLD_LOW_RISK = 25.0    # Green: Likely Valid (<25)
THRESHOLD_MED_RISK = 60.0    # Yellow: Needs Review (25 - 60)
                             # Red: High-Risk Identity Mismatch (>60)

# OCR Indian Plate Regex Pattern
INDIAN_PLATE_REGEX = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$"

# Server Config
HOST = "0.0.0.0"
PORT = 8000
CORS_ORIGINS = ["*"]
