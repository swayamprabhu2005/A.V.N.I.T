# A.V.N.I.T.: Curated Datasets for Model Training & Fine-Tuning

This guide provides a comprehensive list of high-quality, verified public datasets from **Kaggle**, **Roboflow Universe**, and academic repositories that you can directly load into the provided **Google Colab Training Notebooks** (`colab/AVNIT_Plate_Detector_Training.ipynb` and `colab/AVNIT_Color_Classifier_Training.ipynb`).

---

## 1. Indian License Plate Detection (YOLO Format)
*Used for training `plate_detector.pt` with YOLOv8 on Google Colab GPU.*

| Dataset Name | Source | Format | Size | Description & Direct Link |
| :--- | :--- | :--- | :--- | :--- |
| **Indian Number Plates Dataset** | Kaggle | Images + XML/YOLO | ~1,500 images | High-quality Indian vehicles with labeled license plate bounding boxes.<br>🔗 [Kaggle Dataset Link](https://www.kaggle.com/datasets/dataturks/vehicle-number-plate-detection) |
| **Indian Vehicle License Plate Detection** | Kaggle | YOLOv8 Bounding Boxes | ~2,200 images | Day and night conditions, motorcycles, auto-rickshaws, and cars across Indian states.<br>🔗 [Kaggle Dataset Link](https://www.kaggle.com/datasets/prasad22/indian-vehicle-dataset) |
| **Car License Plate Detection** | Kaggle | YOLO format | ~430 images | Clean, high-resolution dataset formatted for quick training on YOLOv8.<br>🔗 [Kaggle Dataset Link](https://www.kaggle.com/datasets/andrewmvd/car-plate-detection) |
| **Roboflow Indian Number Plates** | Roboflow Universe | YOLOv8 PyTorch | ~3,500 annotated | Includes angled plates, low-light cameras, and two-wheelers.<br>🔗 [Roboflow Universe Project](https://universe.roboflow.com/search?q=indian+license+plate) |

### How to use in Colab:
In `colab/AVNIT_Plate_Detector_Training.ipynb`, you can either:
1. Run the automatic download cell (uses the curated open mirror).
2. Or download the zip file from Kaggle/Roboflow, and upload it to Colab as `custom_dataset.zip`.

---

## 2. Vehicle Color Classification Datasets
*Used for training `color_classifier.pt` with MobileNetV3-Small on Google Colab GPU.*

| Dataset Name | Source | Classes | Description & Direct Link |
| :--- | :--- | :--- | :--- |
| **Vehicle Color Recognition Dataset** | Kaggle | 8 Classes (White, Black, Silver, Red, Blue, etc.) | ~10,000 cropped vehicle images sorted by color folders.<br>🔗 [Kaggle Dataset Link](https://www.kaggle.com/datasets/landrybaza/vehicle-color-recognition) |
| **Car Color Classification Dataset** | Kaggle | 16 Classes | Multi-view vehicle crops taken from surveillance cameras.<br>🔗 [Kaggle Dataset Link](https://www.kaggle.com/datasets/prateek058/car-color-classifier) |
| **Comprehensive Cars (CompCars) Color Subset** | Academic / Mirror | 8 Primary colors | Surveillance and web-nature vehicle images with accurate ground truth.<br>🔗 [CompCars Dataset](http://mmlab.ie.cuhk.edu.hk/projects/CompCars.html) |

### How to use in Colab:
In `colab/AVNIT_Color_Classifier_Training.ipynb`, simply run the dataset cell or upload `vehicle_colors.zip` containing `train/` and `val/` subfolders for each color.

---

## 3. Indian License Plate Character Recognition (OCR)
*Optional for fine-tuning text recognition beyond default PaddleOCR / EasyOCR.*

| Dataset Name | Source | Description |
| :--- | :--- | :--- |
| **Indian Number Plate OCR Character Dataset** | Kaggle | Segmented alphanumeric characters (0-9, A-Z) from Indian number plates.<br>🔗 [Kaggle Character Dataset](https://www.kaggle.com/datasets/mobassir/indian-license-plate-character-dataset) |
| **Synthetic License Plate Generator (Python)** | GitHub | Generate synthetic Indian plate crops (e.g. `GA07AB1234`, `MH12DE1433`) with authentic fonts (FE-Schrift or Mandali font). |

---

## 4. Controlled Custom Dataset Collection (Recommended for Final AVNIT Demo)
As recommended in the AVNIT specification document, collecting 20–30 test clips of vehicles you have permission to record produces the most convincing live demonstration:
1. **Legitimate Case**: Vehicle A with Plate A (Ground truth match $\rightarrow$ Green).
2. **Swapped Plate Case**: Vehicle A with Plate B taped or clipped over it (Type mismatch: Car carrying Motorcycle plate $\rightarrow$ Red).
3. **Color Mismatch Case**: Red vehicle displaying White vehicle plate $\rightarrow$ Red.
4. **Obstructed Case**: Plate partially obscured by cloth/paper $\rightarrow$ Yellow (Low OCR Confidence review).
