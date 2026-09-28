<div align="center">
  <img src="assets/AVNIT.png" alt="A.V.N.I.T. Logo" width="220" style="border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);" />
  <h1>A.V.N.I.T.</h1>
  <h3>Automated Verification of Number Plate and Identity Tampering Detection</h3>
  <p><strong>An Autonomous Multi-Stage Deep Learning & Computer Vision System for Real-Time Vehicle Identity Verification, Number Plate Tampering Detection, and Registry Mismatch Auditing</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python" />
    <img src="https://img.shields.io/badge/PyTorch-2.1%2B%20(CPU%2FGPU)-ee4c2c?logo=pytorch" alt="PyTorch" />
    <img src="https://img.shields.io/badge/YOLO-v8%20Nano-00ffff?logo=yolo" alt="YOLOv8" />
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-18%20(Vite%205)-61dafb?logo=react" alt="React" />
    <img src="https://img.shields.io/badge/Tailwind-CSS%20v3-38bdf8?logo=tailwindcss" alt="Tailwind" />
    <img src="https://img.shields.io/badge/Database-SQLite%20WAL-003B57?logo=sqlite" alt="SQLite" />
    <img src="https://img.shields.io/badge/Tests-13%20Passed-brightgreen" alt="Tests" />
  </p>
</div>

---

## 📌 1. Executive Summary

Conventional Automatic Number Plate Recognition (ANPR) systems primarily answer one simple question:
> *"What alphanumeric characters are visible on this registration plate?"*

While effective for automated tolling, conventional ANPR suffers from a catastrophic security blind spot: **it cannot detect if a genuine registration plate has been illegally transferred to an unauthorized, cloned, or stolen vehicle.** 

Criminals, toll evaders, and smugglers exploit this gap by using magnetic brackets, duplicate cloned plates, or physical modifications (such as using tape to alter digits like `0` to `8` or `3` to `B`).

**A.V.N.I.T.** elevates ANPR to an autonomous security and identity-auditing platform by asking the critical question:
> **"Does the observed vehicle's physical identity match the legal registration record tied to the displayed plate?"**

By extracting and cross-verifying multimodal visual telemetry (**Vehicle Type, Body Color, License Plate Bounding Box, and Alphanumeric Character Geometry**) against official motor vehicle registry databases (e.g., VAHAN), A.V.N.I.T. produces an explainable, real-time **Risk Anomaly Score**:
* 🟢 **LIKELY VALID (Risk < 25%)**: All visual attributes match registry records with high optical confidence.
* 🟡 **NEEDS REVIEW (Risk 25% – 60%)**: Partial camera angle occlusion, minor color variations, or low OCR certainty.
* 🔴 **HIGH-RISK IDENTITY MISMATCH (Risk > 60%)**: Critical tamper detected (e.g., a Blue Sedan bearing plates registered to a White Hatchback, or a Car bearing Motorcycle plates).

---

## 🧠 2. Trained Deep Learning Neural Networks & Models

All custom models were trained on **Google Colab (NVIDIA Tesla T4 GPU, 16 GB VRAM)** using turn-key Jupyter Notebooks and exported to the backend (`backend/models/`).

| Model Identifier | Weight File | AI / ML Category & Exact Architecture | Dataset Used & Provenance | Dataset Size & Classes | Parameters & File Size | Training Epochs & Hardware | Final Accuracy & Performance Metrics | Core Role in A.V.N.I.T. |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1: Plate Detector** | [`plate_detector.pt`](file:///D:/MyFiles/Projects/AVNIT/backend/models/plate_detector.pt) | **Deep Learning (CNN)**<br>Ultralytics YOLOv8 Nano (Anchor-Free Spatial Convolutions + C2f Cross-Stage Partial Network) | **[Car Plate Detection](https://www.kaggle.com/datasets/andrewmvd/car-plate-detection)** (`andrewmvd/car-plate-detection`) | 433 vehicle images with high-resolution license plate annotations in YOLO bounding box format | **~3.2 Million**<br>`6.25 MB` | **35 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Precision**: **98.8%**<br>• **Recall**: **100.0%**<br>• **mAP@50**: **99.44%**<br>• **mAP@50-95**: **94.55%**<br>• Inference: **~12 ms/frame** | Detects license plate boundaries on moving vehicles under diverse camera angles and night/day illumination. |
| **Model 2: Color Classifier** | [`color_classifier.pt`](file:///D:/MyFiles/Projects/AVNIT/backend/models/color_classifier.pt) | **Deep Learning (CNN)**<br>MobileNetV3-Small (Depthwise Separable Convolutions + Squeeze-and-Excitation + Hard-Swish) | **[VCoR Vehicle Color Recognition](https://www.kaggle.com/datasets/landrykezebou/vcor-vehicle-color-recognition-dataset)** (`landrykezebou/vcor-vehicle-color-recognition-dataset`) | 10,645 vehicle crops across 15 color classes (*beige, black, blue, brown, gold, green, grey, orange, pink, purple, red, silver, tan, white, yellow*) | **~1.52 Million**<br>`6.27 MB` | **20 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Validation Accuracy**: **99.39%**<br>• **Final Loss**: **0.0245**<br>• Multi-class Cross-Entropy<br>• Inference: **~8 ms/frame** | Classifies vehicle exterior body color to detect stolen/swapped plates on mismatched vehicles. |
| **Model 3: Plate OCR Verifier** | [`plate_ocr_crnn.pt`](file:///D:/MyFiles/Projects/AVNIT/backend/models/plate_ocr_crnn.pt) | **Deep Learning (Deep Residual CNN)**<br>ResNet-18 (8 Residual Blocks with Skip Connections $F(x)+x$ + Dropout 0.3) | **[License Plate Digits Classification](https://www.kaggle.com/datasets/aladdinss/license-plate-digits-classification-dataset)** (`aladdinss/license-plate-digits-classification-dataset`) | 17,565 character crops (14,050 train / 3,515 val) across 36 alphanumeric classes (`0`–`9`, `A`–`Z`) | **~11.19 Million**<br>`44.86 MB` | **20 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Validation Accuracy**: **100.00%**<br>• **Training Accuracy**: **100.00%**<br>• **Final Loss**: **0.0001**<br>• Inference: **~15 ms/batch** | Character-level topological verification to catch taped alterations, forged fonts, and symbol spoofing. |
| **Primary Sequence Reader** | Integrated | **Deep Learning (Hybrid Neural Net)**<br>EasyOCR CRNN (VGG/ResNet feature extractor + BiLSTM sequence modeling + CTC loss) | Pretrained on multi-language alphanumeric sequences with Indian syntax post-processing | Standard ASCII characters | Dynamic Sequence | Pretrained CPU-optimized | Full license plate string extraction with position-aware Indian state normalization (`DL`, `MH`, `KA`, `UP`, etc.). | Transcribes full license plate strings with Indian RTO regular expressions and temporal majority voting. |
| **Base Vehicle Detector** | [`yolov8n.pt`](file:///D:/MyFiles/Projects/AVNIT/yolov8n.pt) | **Deep Learning (CNN)**<br>YOLOv8 Nano pretrained on MS COCO Benchmark | MS COCO 2017 Benchmark | 80 object categories (extracts `car`, `motorcycle`, `bus`, `truck`) | **~3.2 Million**<br>`6.25 MB` | Pretrained baseline | • **mAP@50**: **37.3%** on COCO (Full scale)<br>• Vehicle detection: **>95% recall** | Isolates whole vehicle boundaries and coordinates tracking state vectors. |

---

## 🏗️ 3. End-to-End System Architecture

```
                                  +-------------------------------------------------------------+
                                  |           Incoming Traffic Camera / Video Stream            |
                                  +-------------------------------------------------------------+
                                                                 |
                                                                 v
                                  +-------------------------------------------------------------+
                                  |                 Vehicle Detector (YOLOv8)                   |
                                  |             Isolates Car, Motorcycle, Truck, Bus            |
                                  +-------------------------------------------------------------+
                                                 |                               |
                         Vehicle Bounding Box    |                               | Vehicle Bounding Box
                                                 v                               v
                  +----------------------------------------------+  +-------------------------------------------+
                  |         Model 1: Plate Detector              |  |         Model 2: Color Classifier         |
                  |          (Custom YOLOv8 Nano)                |  |           (MobileNetV3-Small)             |
                  |    Sub-pixel License Plate Cropping          |  |       15-Class Vehicle Color Extraction   |
                  +----------------------------------------------+  +-------------------------------------------+
                                                 |                                               |
                                                 v                                               |
                  +----------------------------------------------+                               |
                  |         Dual-Stage OCR Pipeline              |                               |
                  | 1. EasyOCR (CRNN = ResNet + BiLSTM + CTC)   |                               |
                  | 2. Model 3 (ResNet-18 Character Verifier)   |                               |
                  | 3. Indian Position-Aware Regex Normalization|                               |
                  +----------------------------------------------+                               |
                                                 \                                              /
                                                  \                                            /
                                                   v                                          v
                                  +-------------------------------------------------------------+
                                  |            Persistent Tracking & Temporal Aggregator        |
                                  |       ByteTrack (Kalman Filter + Hungarian Algorithm)       |
                                  |      Majority Voting Buffer across Consecutive Frames       |
                                  +-------------------------------------------------------------+
                                                                 |
                                                                 v
                                  +-------------------------------------------------------------+
                                  |          Explainable 4-Factor Bayesian Risk Engine          |
                                  |     Cross-References Observed Telemetry vs VAHAN Registry   |
                                  +-------------------------------------------------------------+
                                                 |                               |
                                                 v                               v
                                  +------------------------------+  +---------------------------+
                                  |      SQLite WAL Database     |  |       React 18 / Vite     |
                                  | Audit Trail, Records, Alerts |  |   Real-Time HUD Dashboard |
                                  +------------------------------+  +---------------------------+
```

---

## 💻 4. Technology Stack

### A. Frontend Architecture
* **Framework**: [React 18](https://react.dev/) using functional components and hooks (`useState`, `useEffect`, `useCallback`, `useRef`).
* **Build Tool**: [Vite 5](https://vitejs.dev/) with Fast Refresh / HMR and optimized production bundling.
* **Styling & Theme**: [Tailwind CSS v3](https://tailwindcss.com/) with a specialized dark cyber-security HUD palette (`bg-[#0B0F19]`, emerald pass indicators, rose warning badges, slate borders).
* **Icons**: [Lucide React](https://lucide.dev/) modern stroke icons.
* **Real-Time Rendering**: HTML5 Canvas overlay engine computing sub-pixel bounding boxes, track IDs, risk gauges, and telemetry directly over streaming video frames.
* **Dashboard Modules**:
  * **Live Stream & Video Player**: Real-time canvas projection with upload and inference toggle.
  * **Risk Gauge**: Radial visual risk meter (0–100%) with dynamic severity coloring.
  * **Attribute Comparison Matrix**: Side-by-side verification table (Observed vs Registered).
  * **Verification History**: Chronological log of recent vehicle scans with instant alert filtering.
  * **Vehicle Registry Modal**: Full CRUD interface for adding, searching, and managing VAHAN database records.

### B. Backend Architecture
* **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) with asynchronous non-blocking request handlers and auto-generated Swagger documentation (`/docs`).
* **Inference Runtime**: [PyTorch 2.6](https://pytorch.org/) CPU-optimized execution engine (~35 ms total frame processing latency on 4GB RAM PCs).
* **Database**: [SQLite](https://www.sqlite.org/) with Write-Ahead Logging (WAL) for thread-safe concurrent reads and writes (`backend/data/avnit.db`).
* **Tracking Engine**: ByteTrack implementation using 8-dimensional Kalman Filters and the Hungarian bipartite assignment algorithm.
* **Testing**: [pytest](https://pytest.org/) automated test suite with Starlette test client integration.

---

## ⚖️ 5. The 4-Factor Risk Scoring Engine

Rather than relying on brittle binary checks, A.V.N.I.T. deploys an explainable weighted Bayesian decision matrix:

| Factor | Weight | Evaluation Logic & Detection Role |
| :--- | :---: | :--- |
| **Vehicle Type Match** | **35%** | Compares detected visual category (`car`, `motorcycle`, `bus`, `truck`) against registered vehicle type. A motorcycle carrying a car plate triggers an immediate critical penalty. |
| **Make & Model Match** | **25%** | Compares detected vehicle silhouette and make against registered brand and model series. |
| **Vehicle Color Match** | **20%** | Compares MobileNetV3 visual color against registered color (e.g., Red vehicle displaying plates belonging to a White vehicle). |
| **Plate OCR Confidence** | **20%** | Evaluates optical character recognition confidence, topological character sanity, and adherence to standard Indian registration syntax (`^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$`). |

---

## 🚀 6. Installation & Quick Start

### Prerequisites
* **Python 3.10+** (64-bit)
* **Node.js 18+** & **npm**

### Step 1: Clone Repository
```powershell
git clone https://github.com/your-repo/AVNIT.git
cd AVNIT
```

### Step 2: Set Up Backend
```powershell
# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 3: Run Automated Verification Tests
```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests
```
*(All 13 unit tests will verify the database, risk scoring engine, OCR normalizer, and API endpoints).*

### Step 4: Start the Backend Server
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
* Backend API live at: `http://localhost:8000`
* Interactive API Documentation: `http://localhost:8000/docs`

### Step 5: Start the Frontend Dashboard
Open a new terminal window:
```powershell
cd frontend
npm install
npm run dev
```
* Frontend Dashboard live at: `http://localhost:5173`

---

## 📁 7. Project Structure

```text
AVNIT/
├── assets/
│   └── AVNIT.png                       # Official A.V.N.I.T. System Logo
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py               # REST API endpoints (inference, telemetry, vehicles)
│   │   ├── core/
│   │   │   └── risk_engine.py          # 4-Factor Bayesian Identity Tampering Engine
│   │   ├── db/
│   │   │   └── database.py             # SQLite WAL database & VAHAN vehicle registry
│   │   ├── pipeline/
│   │   │   ├── coordinator.py          # Full-pipeline video processor & tracker
│   │   │   ├── plate_detector.py       # Model 1 (YOLOv8 Nano Plate Detector)
│   │   │   ├── color_classifier.py     # Model 2 (MobileNetV3 Color Classifier)
│   │   │   └── ocr_engine.py           # Model 3 (ResNet-18 OCR Verifier & EasyOCR)
│   │   ├── config.py                   # Central configuration & model paths
│   │   └── main.py                     # FastAPI application entrypoint
│   ├── data/
│   │   └── avnit.db                    # Persistent SQLite database file
│   ├── models/
│   │   ├── color_classifier.pt         # Trained MobileNetV3 weights (6.27 MB)
│   │   ├── plate_detector.pt           # Trained YOLOv8 Nano weights (6.25 MB)
│   │   ├── plate_ocr_crnn.pt           # Trained ResNet-18 OCR weights (44.86 MB)
│   │   └── README.md                   # Model specifications & training documentation
│   ├── tests/
│   │   ├── test_api.py                 # FastAPI endpoint integration tests
│   │   ├── test_database.py            # SQLite CRUD & schema tests
│   │   ├── test_normalizer.py          # Indian plate regex & OCR normalization tests
│   │   └── test_risk_engine.py         # 4-Factor risk scoring unit tests
│   └── requirements.txt                # Python backend dependencies
├── colab/
│   ├── AVNIT_Plate_Detector_Training.ipynb   # Model 1 YOLOv8 training notebook
│   ├── AVNIT_Color_Classifier_Training.ipynb # Model 2 MobileNetV3 training notebook
│   └── AVNIT_Plate_OCR_Training.ipynb        # Model 3 ResNet-18 OCR training notebook
├── frontend/
│   ├── public/
│   │   └── AVNIT.png                   # Favicon & branding asset
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── AttributeMatrix.jsx     # Side-by-side observed vs registered table
│   │   │   ├── DetectionHistory.jsx    # Chronological scan log & alert feed
│   │   │   ├── Header.jsx              # System status & navigation header
│   │   │   ├── RiskGauge.jsx           # Radial SVG risk score visualization
│   │   │   ├── StatusBanner.jsx        # Top-level pass/tamper alert indicator
│   │   │   ├── VehicleManagerModal.jsx # VAHAN database management modal
│   │   │   └── VideoPlayer.jsx         # Real-time HTML5 canvas inference overlay
│   │   ├── services/
│   │   │   └── api.js                  # Axios/Fetch API client bindings
│   │   ├── App.jsx                     # Root application coordinator
│   │   └── main.jsx                    # Vite React DOM entrypoint
│   ├── package.json                    # Frontend dependencies
│   ├── tailwind.config.js              # Tailwind styling configuration
│   └── vite.config.js                  # Vite bundler configuration
├── DATASETS_GUIDE.md                   # Comprehensive guide to training datasets
├── README.md                           # Master Project Documentation
└── yolov8n.pt                          # Base COCO YOLOv8 Nano weights
```

---

## 🛡️ 8. Security & Privacy Considerations

* **Local Data Sovereignty**: All inference and database queries run entirely on the local device or edge server; no video frames or license plate data are transmitted to unverified third-party cloud APIs.
* **Explainable AI (XAI)**: Every tamper alert provides a transparent breakdown of the contributing risk factors (e.g. `Color mismatch: observed Red vs registered White (Risk +20%)`), preventing opaque automated penalties.
* **Thread-Safe Concurrent Auditing**: Database interactions use SQLite Write-Ahead Logging to guarantee zero database locking under high-frequency camera scans.

---

## 👥 9. Authors & Academic Attribution

* **Project**: A.V.N.I.T. (Automated Verification of Number Plate and Identity Tampering Detection)
* **Application**: Intelligent Transportation Systems (ITS), Smart Cities, Automated Border Control & Law Enforcement
* **License**: MIT Academic License (Open Source)
