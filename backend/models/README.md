# A.V.N.I.T. — Trained Deep Learning Models & Weights

This directory stores the trained deep learning neural network checkpoints and weights used by the **A.V.N.I.T.** backend pipeline for real-time vehicle detection, color identification, and number plate character recognition.

---

## 📊 Comprehensive Model Specifications & Performance Matrix

| Model Identifier | Weight File | Category & Architecture | Dataset Used & Source | Dataset Size & Classes | Parameters & File Size | Training Epochs & Hardware | Final Accuracy & Performance Metrics |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1: Plate Detector** | `plate_detector.pt` | **Deep Learning (CNN)**<br>Ultralytics YOLOv8 Nano (Anchor-Free Spatial Convolutions + C2f Cross-Stage Partial Network) | **[Car Plate Detection](https://www.kaggle.com/datasets/andrewmvd/car-plate-detection)**<br>`andrewmvd/car-plate-detection` | 433 annotated vehicle images with high-resolution license plate bounding boxes in YOLO format | **~3.2 Million**<br>`6.25 MB` | **35 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Precision**: **98.8%**<br>• **Recall**: **100.0%**<br>• **mAP@50**: **99.44%**<br>• **mAP@50-95**: **94.55%**<br>• Inference: **~12 ms/frame** |
| **Model 2: Color Classifier** | `color_classifier.pt` | **Deep Learning (CNN)**<br>MobileNetV3-Small (Depthwise Separable Convolutions + Squeeze-and-Excitation + Hard-Swish) | **[VCoR Vehicle Color Recognition](https://www.kaggle.com/datasets/landrykezebou/vcor-vehicle-color-recognition-dataset)**<br>`landrykezebou/vcor-vehicle-color-recognition-dataset` | 10,645 vehicle crops across 15 color classes (*beige, black, blue, brown, gold, green, grey, orange, pink, purple, red, silver, tan, white, yellow*) | **~1.52 Million**<br>`6.27 MB` | **20 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Validation Accuracy**: **99.39%**<br>• **Final Loss**: **0.0245**<br>• Multi-class Cross-Entropy<br>• Inference: **~8 ms/frame** |
| **Model 3: Plate OCR Verifier** | `plate_ocr_crnn.pt` | **Deep Learning (Deep Residual CNN)**<br>ResNet-18 (8 Residual Blocks with Skip Connections $F(x)+x$ + Dropout 0.3) | **[License Plate Digits Classification](https://www.kaggle.com/datasets/aladdinss/license-plate-digits-classification-dataset)**<br>`aladdinss/license-plate-digits-classification-dataset` | 17,565 character crops (14,050 train / 3,515 val) across 36 alphanumeric classes (`0`–`9`, `A`–`Z`) | **~11.19 Million**<br>`44.86 MB` | **20 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Validation Accuracy**: **100.00%**<br>• **Training Accuracy**: **100.00%**<br>• **Final Loss**: **0.0001**<br>• Inference: **~15 ms/batch** |
| **Base Vehicle Detector** | `yolov8n.pt` | **Deep Learning (CNN)**<br>YOLOv8 Nano pretrained on MS COCO | **MS COCO 2017 Benchmark** | 80 object classes (extracts `car`, `motorcycle`, `bus`, `truck`) | **~3.2 Million**<br>`6.25 MB` | Pretrained baseline | • **mAP@50**: **37.3%** on COCO (Full scale)<br>• Vehicle detection: **>95% recall** |

---

## 🔍 Detailed Model Architecture & Dataset Breakdown

### 1. Model 1: License Plate Detector (`plate_detector.pt`)
* **Architecture**: Ultralytics YOLOv8 Nano object detection model with decoupled head separating objectness, classification, and bounding box regression.
* **Role**: Scans detected vehicle crops and extracts sub-pixel bounding box coordinates for vehicle registration plates under diverse camera angles and illumination.
* **Dataset**: `andrewmvd/car-plate-detection` (Kaggle). Contains 433 real-world vehicle images in YOLO bounding box format.
* **Training Hyperparameters**:
  * Image Resolution: `640 x 640`
  * Batch Size: `16`
  * Optimizer: `AdamW` (lr0=0.01, lrf=0.01)
  * Training Epochs: `35`
  * Final Precision: **98.8%** | Recall: **100.0%** | mAP@50: **99.44%** | mAP@50-95: **94.55%**

### 2. Model 2: Vehicle Color Classifier (`color_classifier.pt`)
* **Architecture**: MobileNetV3-Small featuring Depthwise Separable Convolutions, Squeeze-and-Excitation (SE) channel-attention modules, and computationally efficient Hard-Swish activation functions.
* **Role**: Accurately classifies the primary visual exterior color of detected vehicles to compare against official registration records and identify color-swapping identity tampering.
* **Dataset**: `landrykezebou/vcor-vehicle-color-recognition-dataset` (Kaggle). Contains 10,645 high-resolution vehicle crops distributed across 15 distinct color classes.
* **Classes (15)**: `beige`, `black`, `blue`, `brown`, `gold`, `green`, `grey`, `orange`, `pink`, `purple`, `red`, `silver`, `tan`, `white`, `yellow`.
* **Dynamic Mapping**: Automatically mapped into A.V.N.I.T. standard classes (`white`, `black`, `silver_grey`, `red`, `blue`, `yellow`, `green`).
* **Training Hyperparameters**:
  * Image Resolution: `224 x 224`
  * Batch Size: `32`
  * Optimizer: `AdamW` with Cosine Annealing learning rate schedule (`T_max=20`)
  * Final Validation Accuracy: **99.39%** | Training Loss: **0.0245**

### 3. Model 3: Plate Character Recognizer (`plate_ocr_crnn.pt`)
* **Architecture**: ResNet-18 Deep Residual Convolutional Neural Network. Employs 8 residual blocks with identity shortcut connections to solve vanishing gradients and extract high-order topological features of characters.
* **Role**: Evaluates segmented alphanumeric character crops across 36 classes to verify individual character geometry, detecting character tampering, taped alterations (e.g., modifying `8` to `B` or `0` to `D`), and plate forgery.
* **Dataset**: `aladdinss/license-plate-digits-classification-dataset` (Kaggle). Contains 17,565 character crops extracted directly from real vehicle license plates.
* **Classes (36)**: Digits `0` through `9` and uppercase letters `A` through `Z`.
* **Training / Validation Split**:
  * Training Images: **14,050** images (80%)
  * Validation Images: **3,515** images (20%)
* **Training Hyperparameters**:
  * Image Resolution: `64 x 64` (grayscale with 3-channel normalization)
  * Batch Size: `64`
  * Data Augmentations: Random 8° rotation, brightness & contrast jitter
  * Optimizer: `AdamW` (learning rate `1e-3`, weight decay `1e-4`)
  * Scheduler: `CosineAnnealingLR` (`T_max=25`)
  * Final Validation Accuracy: **100.00%** | Final Training Accuracy: **100.00%** | Loss: **0.0001**

---

## 🛠️ Loading in Backend Pipeline

All three models are seamlessly loaded by the backend pipeline (`backend/app/pipeline/`):
* `backend/app/pipeline/plate_detector.py` loads `plate_detector.pt` via `ultralytics.YOLO`.
* `backend/app/pipeline/color_classifier.py` loads `color_classifier.pt` with PyTorch 2.6 safe unpickling (`weights_only=False`).
* `backend/app/pipeline/ocr_engine.py` loads `plate_ocr_crnn.pt` into `CustomPlateOCR` for character-level visual verification.
