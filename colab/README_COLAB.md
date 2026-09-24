# Google Colab Training Guide for A.V.N.I.T.

Since local training requires a dedicated GPU and your PC has 4GB RAM with CPU-only, all deep neural network training in **A.V.N.I.T.** is designed to run completely on **Google Colab's free NVIDIA T4 GPU**.

---

## 3 Notebooks Overview

1. **`AVNIT_Plate_Detector_Training.ipynb`**:
   - **Task**: License Plate Localization (Bounding Box Detection).
   - **Architecture**: Ultralytics YOLOv8 Nano (`yolov8n.pt`).
   - **Dataset**: Roboflow Indian Number Plates Dataset (~3,500 annotated images).
   - **Output**: `plate_detector.pt` (placed in `backend/models/plate_detector.pt`).
   - **Training Time**: ~10–12 minutes on Colab T4 GPU.

2. **`AVNIT_Color_Classifier_Training.ipynb`**:
   - **Task**: Vehicle Color Recognition (8 classes: White, Black, Silver/Grey, Red, Blue, Yellow, Green, Brown).
   - **Architecture**: MobileNetV3-Small (lightweight PyTorch CNN).
   - **Dataset**: Vehicle Color Recognition Dataset.
   - **Output**: `color_classifier.pt` (placed in `backend/models/color_classifier.pt`).
   - **Training Time**: ~8–10 minutes on Colab T4 GPU.

3. **`AVNIT_Plate_OCR_Training.ipynb`**:
   - **Task**: Plate Character Recognition (Alphanumeric OCR 0-9, A-Z).
   - **Architecture**: Deep Character CNN / ResNet-18.
   - **Dataset**: Indian Number Plate OCR Character Dataset.
   - **Output**: `plate_ocr_crnn.pt` (placed in `backend/models/plate_ocr_crnn.pt`).
   - **Training Time**: ~8–10 minutes on Colab T4 GPU.

---

## How to Run in Google Colab (Step-by-Step)

### Step 1: Open Google Colab
1. Navigate to [Google Colab](https://colab.research.google.com).
2. Click **Upload** and upload any of the 3 notebooks from the `colab/` folder.

### Step 2: Enable Free GPU
1. In the top menu, go to **Runtime** > **Change runtime type**.
2. Under **Hardware accelerator**, select **T4 GPU**.
3. Click **Save**.

### Step 3: Run All Cells
1. Click **Runtime** > **Run all** (or press `Ctrl+F9`).
2. When prompted, permit Google Drive mounting.
3. The notebook will automatically:
   - Check GPU availability.
   - Mount your Google Drive at `My Drive/AVNIT_Models/`.
   - Download the training dataset.
   - Train the neural network across epochs.
   - Save intermediate epoch checkpoints and final weights directly to your Google Drive!
   - Trigger a direct browser download for the `.pt` file.

### Step 4: Transfer Weights to Local Project
Move the downloaded files to:
```text
backend/models/plate_detector.pt
backend/models/color_classifier.pt
backend/models/plate_ocr_crnn.pt
```

### Step 5: Start A.V.N.I.T.
Start the backend server on your PC:
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open **http://localhost:8000** to view your custom trained models live!
