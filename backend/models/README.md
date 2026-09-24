# AVNIT Model Weights Directory

This directory stores the neural network weights used by the AVNIT backend.

## Expected Files

1. **`yolov8n.pt`**:
   - Pre-trained Ultralytics YOLOv8 Nano model on COCO dataset (detects `car`, `motorcycle`, `bus`, `truck`).
   - Automatically downloaded by Ultralytics when starting the backend if not present (~6 MB).

2. **`plate_detector.pt`**:
   - Number plate detection model trained on Google Colab (`colab/AVNIT_Plate_Detector_Training.ipynb`).
   - Once downloaded from Colab, place it here as:
     `backend/models/plate_detector.pt`

3. **`color_classifier.pt`**:
   - MobileNetV3 vehicle color classifier trained on Google Colab (`colab/AVNIT_Color_Classifier_Training.ipynb`).
   - Once downloaded from Colab, place it here as:
     `backend/models/color_classifier.pt`

4. **`plate_ocr_crnn.pt`**:
   - Deep character recognition neural network trained on Google Colab (`colab/AVNIT_Plate_OCR_Training.ipynb`).
   - Once downloaded from Colab, place it here as:
     `backend/models/plate_ocr_crnn.pt`

> [!NOTE]
> If any of the `.pt` weight files are not yet placed here, AVNIT uses an intelligent CPU fallback (heuristic plate localization, HSV color extraction, and EasyOCR engine) so the entire application remains fully functional and testable right away!
