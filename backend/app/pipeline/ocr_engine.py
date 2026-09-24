import re
from typing import Optional, Tuple, Dict, List
from collections import defaultdict, Counter

# Character substitution lookup dictionaries
# In Indian number plates, the structure is:
# Position 0-1: State Code (Letters, e.g., GA, MH, DL, KA)
# Position 2-3: District / RTO Code (Digits, e.g., 07, 12, 01)
# Position 4-5/6: Series Letters (Letters, e.g., AB, DE, CA)
# Last 4: Unique Number (Digits, e.g., 1234, 1433)

DIGIT_TO_CHAR = {
    '0': 'O',
    '1': 'I',
    '2': 'Z',
    '5': 'S',
    '6': 'G',
    '8': 'B'
}

CHAR_TO_DIGIT = {
    'O': '0',
    'D': '0',
    'Q': '0',
    'I': '1',
    'L': '1',
    'Z': '2',
    'S': '5',
    'G': '6',
    'B': '8'
}

INDIAN_STATES = {
    "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "DN", "GA", 
    "GJ", "HR", "HP", "JH", "JK", "KA", "KL", "LA", "LD", "MH", 
    "ML", "MN", "MP", "MZ", "NL", "OD", "PB", "PY", "RJ", "SK", 
    "TN", "TR", "TS", "UK", "UP", "WB"
}

def clean_raw_plate(raw_text: str) -> str:
    """Removes non-alphanumeric characters, whitespace and capitalizes."""
    if not raw_text:
        return ""
    return re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()

def normalize_indian_plate(raw_text: str) -> Tuple[str, float]:
    """
    Applies position-aware character correction for Indian Number Plates.
    Standard Format: [State: 2 Alpha][RTO: 1-2 Digits][Series: 1-3 Alpha][Number: 4 Digits]
    Returns (normalized_plate, validity_confidence_score).
    """
    cleaned = clean_raw_plate(raw_text)
    if len(cleaned) < 8 or len(cleaned) > 11:
        # Length out of standard bounds
        return cleaned, 0.40

    chars = list(cleaned)
    n = len(chars)

    # 1. First 2 characters must be State Code (Letters)
    for i in range(min(2, n)):
        if chars[i].isdigit() and chars[i] in DIGIT_TO_CHAR:
            chars[i] = DIGIT_TO_CHAR[chars[i]]

    # 2. Next 1 or 2 characters must be RTO Digits
    # (If total length is 10: State(2), RTO(2), Series(2), Number(4))
    if n == 10:
        # Indices 2, 3 should be digits
        for i in [2, 3]:
            if chars[i] in CHAR_TO_DIGIT:
                chars[i] = CHAR_TO_DIGIT[chars[i]]
        # Indices 4, 5 should be letters
        for i in [4, 5]:
            if chars[i].isdigit() and chars[i] in DIGIT_TO_CHAR:
                chars[i] = DIGIT_TO_CHAR[chars[i]]
        # Indices 6, 7, 8, 9 should be digits
        for i in [6, 7, 8, 9]:
            if chars[i] in CHAR_TO_DIGIT:
                chars[i] = CHAR_TO_DIGIT[chars[i]]

    normalized = "".join(chars)

    # Validate against standard Indian regex
    pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$"
    if re.match(pattern, normalized):
        state_code = normalized[:2]
        confidence = 0.95 if state_code in INDIAN_STATES else 0.85
        return normalized, confidence
    
    return normalized, 0.50

class PlateTemporalAggregator:
    """
    Accumulates OCR readings across multiple frames for each tracked vehicle ID.
    Selects the most stable/frequent plate via majority voting and confidence weighting.
    """
    def __init__(self, buffer_size: int = 15):
        self.buffer_size = buffer_size
        self.tracks = defaultdict(list)

    def add_observation(self, track_id: int, plate_text: str, confidence: float):
        norm_text, norm_conf = normalize_indian_plate(plate_text)
        overall_conf = (confidence + norm_conf) / 2.0
        
        self.tracks[track_id].append((norm_text, overall_conf))
        if len(self.tracks[track_id]) > self.buffer_size:
            self.tracks[track_id].pop(0)

    def get_stable_plate(self, track_id: int) -> Tuple[Optional[str], float]:
        observations = self.tracks.get(track_id, [])
        if not observations:
            return None, 0.0

        # Weighted majority vote
        plate_weights = defaultdict(float)
        for plate, conf in observations:
            plate_weights[plate] += conf

        best_plate = max(plate_weights, key=plate_weights.get)
        count = sum(1 for p, _ in observations if p == best_plate)
        avg_conf = sum(conf for p, conf in observations if p == best_plate) / max(1, count)

        return best_plate, round(avg_conf, 3)

    def clear_track(self, track_id: int):
        if track_id in self.tracks:
            del self.tracks[track_id]

class CustomPlateOCR:
    """
    Loads custom PyTorch character recognition neural network if plate_ocr_crnn.pt is present.
    """
    def __init__(self, weight_path=None):
        import os
        from ..config import PLATE_OCR_WEIGHTS
        self.weight_path = weight_path or PLATE_OCR_WEIGHTS
        self.model = None
        self.classes = []
        self._load()

    def _load(self):
        import os
        if os.path.exists(self.weight_path):
            try:
                import torch
                from torchvision import models
                import torch.nn as nn
                checkpoint = torch.load(self.weight_path, map_location="cpu")
                self.classes = checkpoint.get("classes", [])
                model = models.resnet18(weights=None)
                in_features = model.fc.in_features
                model.fc = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_features, len(self.classes))
                )
                model.load_state_dict(checkpoint["state_dict"])
                model.eval()
                self.model = model
                print("[AVNIT] Successfully loaded Colab-trained Plate OCR Neural Network!")
            except Exception as e:
                print(f"[AVNIT] Warning: Could not load plate OCR weights: {e}")
                self.model = None

