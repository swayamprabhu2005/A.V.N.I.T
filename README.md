<div align="center">
  <img src="assets/AVNIT.png" alt="A.V.N.I.T. Logo" width="220" style="border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />
  <h1>A.V.N.I.T.</h1>
  <h3>Automated Verification of Number Plate and Identity Tampering Detection</h3>
  <p><strong>An Autonomous Multi-Stage Deep Learning & Computer Vision Platform for Real-Time Vehicle Identity Verification, Number Plate Tampering Detection, and Registry Mismatch Auditing</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-zinc?logo=python" alt="Python" />
    <img src="https://img.shields.io/badge/PyTorch-2.1%2B%20(CPU%2FGPU)-ee4c2c?logo=pytorch" alt="PyTorch" />
    <img src="https://img.shields.io/badge/YOLO-v8%20Nano-emerald?logo=yolo" alt="YOLOv8" />
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Vue.js-3.4%20(Vite%205)-42b883?logo=vuedotjs" alt="Vue.js 3" />
    <img src="https://img.shields.io/badge/PixiJS-v7%20WebGL%20HUD-e91e63?logo=pixijs" alt="PixiJS" />
    <img src="https://img.shields.io/badge/Tailwind-CSS%20v3%20(Zero%20Blue)-18181b?logo=tailwindcss" alt="Tailwind" />
    <img src="https://img.shields.io/badge/Database-SQLite%20WAL-18181b?logo=sqlite" alt="SQLite" />
    <img src="https://img.shields.io/badge/Tests-16%20Passed-emerald" alt="Tests" />
  </p>
</div>

---

## 📌 1. Executive Summary

Conventional Automatic Number Plate Recognition (ANPR) systems primarily answer one simple question:
> *"What alphanumeric characters are visible on this registration plate?"*

While effective for automated tolling, conventional ANPR suffers from a catastrophic security blind spot: **it cannot detect if a genuine registration plate has been illegally transferred to an unauthorized, cloned, or stolen vehicle.** 

Criminals, toll evaders, and vehicle smugglers exploit this gap using magnetic brackets, duplicate cloned plates, or physical modifications (such as using black tape to alter characters like `0` to `8` or `3` to `B`).

**A.V.N.I.T.** elevates ANPR to an autonomous security and identity-auditing platform by asking the critical question:
> **"Does the observed vehicle's physical identity match the legal registration record tied to the displayed plate?"**

By extracting and cross-verifying multimodal visual telemetry (**Vehicle Type, Body Color, License Plate Bounding Box, and Alphanumeric Character Geometry**) against official motor vehicle registry databases (e.g., VAHAN), A.V.N.I.T. produces an explainable, real-time **Risk Anomaly Score**:
* 🟢 **VERIFIED PASS (Risk < 30%)**: All visual attributes match registry records with high optical confidence.
* 🟡 **ATTRIBUTE VARIANCE REVIEW (Risk 30% – 59%)**: Minor color variations, partial camera occlusions, or lighting variance.
* 🔴 **CRITICAL IDENTITY TAMPERING (Risk >= 60%)**: Critical tamper detected (e.g., a Black SUV bearing plates registered to a White Hatchback, or a Car displaying Motorcycle plates).

---

## 🧠 2. Trained Deep Learning Neural Networks & Models

All custom models were trained on **Google Colab (NVIDIA Tesla T4 GPU, 16 GB VRAM)** using turn-key Jupyter Notebooks and exported directly to the backend runtime (`backend/models/`).

| Model Identifier | Weight File | AI / ML Category & Exact Architecture | Dataset Used & Provenance | Dataset Size & Classes | Parameters & File Size | Training Epochs & Hardware | Final Accuracy & Performance Metrics | Core Role in A.V.N.I.T. |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1: Plate Detector** | [`plate_detector.pt`](file:///D:/MyFiles/Projects/AVNIT/backend/models/plate_detector.pt) | **Deep Learning (CNN)**<br>Ultralytics YOLOv8 Nano (Anchor-Free Spatial Convolutions + C2f Cross-Stage Partial Network) | **[Car Plate Detection](https://www.kaggle.com/datasets/andrewmvd/car-plate-detection)** (`andrewmvd/car-plate-detection`) | 433 vehicle images with high-resolution license plate annotations in YOLO bounding box format | **~3.2 Million**<br>`6.25 MB` | **35 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Precision**: **98.8%**<br>• **Recall**: **100.0%**<br>• **mAP@50**: **99.44%**<br>• **mAP@50-95**: **94.55%**<br>• Inference: **~12 ms/frame** | Detects license plate boundaries on moving vehicles under diverse camera angles and night/day illumination. |
| **Model 2: Color Classifier** | [`color_classifier.pt`](file:///D:/MyFiles/Projects/AVNIT/backend/models/color_classifier.pt) | **Deep Learning (CNN)**<br>MobileNetV3-Small (Depthwise Separable Convolutions + Squeeze-and-Excitation + Hard-Swish) | **[VCoR Vehicle Color Recognition](https://www.kaggle.com/datasets/landrykezebou/vcor-vehicle-color-recognition-dataset)** (`landrykezebou/vcor-vehicle-color-recognition-dataset`) | 10,645 vehicle crops across 15 color classes (*beige, black, blue, brown, gold, green, grey, orange, pink, purple, red, silver, tan, white, yellow*) | **~1.52 Million**<br>`6.27 MB` | **20 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Validation Accuracy**: **99.39%**<br>• **Final Loss**: **0.0245**<br>• Multi-class Cross-Entropy<br>• Inference: **~8 ms/frame** | Classifies vehicle exterior body color to detect stolen/swapped plates on mismatched vehicles. |
| **Model 3: Plate OCR Verifier** | [`plate_ocr_crnn.pt`](file:///D:/MyFiles/Projects/AVNIT/backend/models/plate_ocr_crnn.pt) | **Deep Learning (Deep Residual CNN)**<br>ResNet-18 (8 Residual Blocks with Skip Connections $F(x)+x$ + Dropout 0.3) | **[License Plate Digits Classification](https://www.kaggle.com/datasets/aladdinss/license-plate-digits-classification-dataset)** (`aladdinss/license-plate-digits-classification-dataset`) | 17,565 character crops (14,050 train / 3,515 val) across 36 alphanumeric classes (`0`–`9`, `A`–`Z`) | **~11.19 Million**<br>`44.86 MB` | **20 Epochs**<br>Google Colab (Tesla T4 GPU) | • **Validation Accuracy**: **100.00%**<br>• **Training Accuracy**: **100.00%**<br>• **Final Loss**: **0.0001**<br>• Inference: **~15 ms/batch** | Character-level topological verification to catch taped alterations, forged fonts, and symbol spoofing. |
| **Primary Sequence Reader** | Integrated | **Deep Learning (Hybrid Neural Net)**<br>EasyOCR CRNN (VGG/ResNet feature extractor + BiLSTM sequence modeling + CTC loss) | Pretrained on multi-language alphanumeric sequences with Indian syntax post-processing | Standard ASCII characters | Dynamic Sequence | Pretrained CPU-optimized | Full license plate string extraction with position-aware Indian state normalization (`DL`, `MH`, `KA`, `UP`, etc.). | Transcribes full license plate strings with Indian RTO regular expressions and temporal majority voting. |
| **Base Vehicle Detector** | [`yolov8n.pt`](file:///D:/MyFiles/Projects/AVNIT/yolov8n.pt) | **Deep Learning (CNN)**<br>YOLOv8 Nano pretrained on MS COCO Benchmark | MS COCO 2017 Benchmark | 80 object categories (extracts `car`, `motorcycle`, `bus`, `truck`) | **~3.2 Million**<br>`6.25 MB` | Pretrained baseline | • **mAP@50**: **37.3%** on COCO (Full scale)<br>• Vehicle detection: **>95% recall** | Isolates whole vehicle boundaries and coordinates tracking state vectors. |

---

## 🏗️ 3. End-to-End System Architecture

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │          Roadside Cameras / Highway Infrastructure          │
                    └─────────────────────────────────────────────────────────────┘
                                                   │
                    ┌──────────────────────────────┴──────────────────────────────┐
                    ▼                                                             ▼
     [ METHOD 1: Direct RTSP Stream Ingestion ]                 [ METHOD 2: Downloadable Edge Agent ]
     • Operator inputs RTSP URL in Web Dashboard                 • Agency deploys avnit_edge_agent.py
     • Central backend streams and processes feed                • Runs AI on pole PC; sends 2KB JSON
                    │                                                             │
                    └──────────────────────────────┬──────────────────────────────┘
                                                   ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │               Automatic Night Mode & CLAHE                  │
                    │        (L < 50 / S < 18% Detection -> Adaptive IR Weights)  │
                    └─────────────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │          Multi-Stage Deep Learning Vision Pipeline          │
                    │   1. YOLOv8 Vehicle Detector     2. YOLOv8 Plate Detector   │
                    │   3. MobileNetV3 Color Net       4. ResNet-18 OCR Verifier  │
                    └─────────────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │               Explainable Bayesian Risk Engine              │
                    │       Cross-References Telemetry vs VAHAN Registry DB       │
                    └─────────────────────────────────────────────────────────────┘
                                   │                               │
                                   ▼                               ▼
                    ┌──────────────────────────────┐ ┌───────────────────────────┐
                    │     SQLite WAL Database      │ │      Vue 3 + Vite +       │
                    │ Audit Trail, Alerts, Records │ │   PixiJS WebGL HUD UI     │
                    └──────────────────────────────┘ └───────────────────────────┘
```

---

## 💻 4. Technology Stack

### A. Frontend Architecture (Modernized Vue 3)
* **Framework**: [Vue.js 3](https://vuejs.org/) (Composition API `<script setup>`).
* **Build Tool**: [Vite 5](https://vitejs.dev/) with instantaneous HMR and optimized production asset chunking.
* **GPU HUD Engine**: [PixiJS v7](https://pixijs.com/) rendering WebGL tactical targeting brackets, sub-pixel bounding boxes, and monospace HUD cards at a stable 60 FPS.
* **Physics Motion**: [@motionone/vue](https://motion.dev/) powering spring-physics radial sweeps on the Bayesian Risk Gauge.
* **Reporting Engine**: [jsPDF](https://github.com/parallax/jsPDF) & [jsPDF-AutoTable](https://github.com/simonbengtsson/jsPDF-AutoTable) for instant CSV exports and styled vector PDF law enforcement dossiers.
* **Design System**: [Tailwind CSS v3](https://tailwindcss.com/) with an **Executive Enterprise Light Theme** featuring warm off-whites, neutral slate/stone cards, and **STRICTLY ZERO SHADES OF BLUE** (using onyx `#18181b`, emerald `#059669`, amber `#d97706`, and rose `#e11d48`).
* **Clean Operator Navigation**: Developer debugging indicators (`Backend Online`, `Models Loaded`, `DB Active`) are completely decoupled from operator view to maintain a professional command-center workflow.

### B. Backend Architecture
* **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) with asynchronous non-blocking request handlers, WebSockets, and Swagger docs (`/docs`).
* **Inference Runtime**: [PyTorch 2.6](https://pytorch.org/) CPU-optimized execution engine (~35 ms total frame processing latency on 4GB RAM PCs).
* **Database**: [SQLite](https://www.sqlite.org/) with Write-Ahead Logging (WAL) for thread-safe concurrent reads and writes (`backend/data/avnit.db`).
* **Edge Telemetry Ingress**: `POST /api/telemetry/ingress` endpoint receiving real-time edge detections from roadside poles and broadcasting to connected dashboards.
* **Testing**: [pytest](https://pytest.org/) automated test suite with Starlette client testing (16/16 tests passing).

---

## 🛣️ 5. Roadside & Government Camera Integration

A.V.N.I.T. supports two production-ready methods for roadside integration:

### Method 1: Direct Web-Based RTSP Stream Ingestion
Operators click **"Connect IP Camera"** in the top navigation and enter:
* Camera Identifier Name (e.g., `NH-48 Toll Lane 4`)
* RTSP Stream URL (`rtsp://admin:pass@192.168.1.50:554/live`)
* Highway Location Description (`NH-48 KM 42 Junction`)

The backend connects directly to the camera feed and streams live detections to the dashboard.

### Method 2: Autonomous Roadside Edge Agent (`edge/avnit_edge_agent.py`)
For city-scale highway networks where transmitting 4K video feeds is bandwidth-prohibitive:
1. Field teams deploy the standalone script [`edge/avnit_edge_agent.py`](file:///D:/MyFiles/Projects/AVNIT/edge/avnit_edge_agent.py) on a roadside pole PC (NVIDIA Jetson, Raspberry Pi 5, or Industrial IPC).
2. The agent executes vehicle and plate detection locally on the camera feed at 20–30 FPS.
3. It sends tiny **~2 KB JSON telemetry pings** to `POST /api/telemetry/ingress`.
4. When high-risk identity tampering is detected, it attaches a compressed snapshot crop as legal evidence.
5. Operators can download both [`avnit_edge_agent.py`](file:///D:/MyFiles/Projects/AVNIT/edge/avnit_edge_agent.py) and [`edge_config.json`](file:///D:/MyFiles/Projects/AVNIT/edge/edge_config.json) directly with one click from the dashboard modal.

---

## 🌙 6. Automatic Night Mode & Contrast Optimization

* **Automatic Detection**: Every video frame is analyzed for average luminance ($L < 50$) and saturation ($S < 18\%$). When low-light or monochrome infrared (IR) night vision is detected, **Night Mode activates automatically**.
* **Adaptive CLAHE Enhancement**: Applies Contrast Limited Adaptive Histogram Equalization with dynamic clip limits ($3.5\times$ during night mode) to suppress high-beam headlight glare and amplify dim plate characters.
* **Adaptive Bayesian Weighting**: In night mode, the risk engine dynamically reduces the Color Mismatch weight from 20% to **5%** (to account for monochrome IR camera feeds) and shifts weight to **Vehicle Silhouette Type** (40%) and **Plate OCR Syntax & Topology** (35%), eliminating false alarms.

---

## 📊 7. One-Click Reporting & Export Engine

* **One-Click CSV Export**: Downloads a clean spreadsheet containing all detection incidents, timestamps, plate numbers, visual attributes, risk scores, and audit findings.
* **Official PDF Law Enforcement Dossier**: Generates a professional multi-page PDF document complete with:
  * Official `A.V.N.I.T. LAW ENFORCEMENT AUDIT DOSSIER` header
  * Executive Summary KPI grid (*Total Scanned, Valid Passes, Variances, Tamper Alerts*)
  * Chronological tabular evidence with status-colored tags and monospace plate typography
  * Legal evidence watermark and confidentiality disclaimer

---

## 🚀 8. Installation & Quick Start

### Prerequisites
* **Python 3.10+** (64-bit)
* **Node.js 18+** & **npm**

### Step 1: Clone Repository
```powershell
git clone https://github.com/swayamprabhu2005/A.V.N.I.T.git
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
*(All 16 unit tests will verify the database, risk scoring engine, OCR normalizer, and edge API endpoints).*

---

### ⚡ One-Click Full Project Launch (Recommended)
You can start both the **FastAPI backend** and **Vue 3 frontend dashboard** simultaneously with one command:
```powershell
.\run.bat
```
* Automatically detects or activates your Python environment.
* Launches the backend API on `http://localhost:8000`.
* Launches the Vue 3 + Vite dashboard on `http://localhost:5173`.
* Automatically opens your default web browser to the dashboard.

---

### Alternative: Manual Step-by-Step Launch

#### Step 4A: Start the Backend Server
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
* Backend API live at: `http://localhost:8000`
* Interactive API Documentation: `http://localhost:8000/docs`

#### Step 4B: Start the Frontend Dashboard
Open a second terminal window:
```powershell
cd frontend
npm install
npm run dev
```
* Frontend Dashboard live at: `http://localhost:5173`

---

## 📁 9. Project Structure

```text
AVNIT/
├── assets/
│   └── AVNIT.png                       # Official A.V.N.I.T. System Logo
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py               # REST API endpoints (CRUD, stats, edge ingress)
│   │   │   └── websocket.py            # Streaming WebSocket & external event broadcaster
│   │   ├── pipeline/
│   │   │   ├── coordinator.py          # Full vision pipeline, tracker & night mode detector
│   │   │   ├── risk_engine.py          # 4-Factor Bayesian Risk Engine with IR compensation
│   │   │   ├── plate_detector.py       # Model 1 (YOLOv8 Nano Plate Detector)
│   │   │   ├── color_classifier.py     # Model 2 (MobileNetV3 Color Classifier)
│   │   │   └── ocr_engine.py           # Model 3 (ResNet-18 OCR Verifier & EasyOCR)
│   │   ├── database.py                 # SQLite WAL database & VAHAN vehicle registry
│   │   ├── config.py                   # Central configuration & model paths
│   │   └── main.py                     # FastAPI application entrypoint
│   ├── data/
│   │   └── avnit.db                    # Persistent SQLite database file
│   ├── models/
│   │   ├── color_classifier.pt         # Trained MobileNetV3 weights (6.27 MB)
│   │   ├── plate_detector.pt           # Trained YOLOv8 Nano weights (6.25 MB)
│   │   ├── plate_ocr_crnn.pt           # Trained ResNet-18 OCR weights (44.86 MB)
│   │   └── README.md                   # Model specifications & training documentation
│   └── tests/
│       ├── test_api.py                 # FastAPI endpoint & edge ingress tests
│       ├── test_database.py            # SQLite CRUD & schema tests
│       ├── test_normalizer.py          # Indian plate regex & OCR normalization tests
│       └── test_risk_engine.py         # 4-Factor risk scoring & night mode unit tests
├── edge/
│   ├── avnit_edge_agent.py             # Autonomous roadside edge processing agent
│   ├── edge_config.json                # Edge configuration template
│   └── README.md                       # Field deployment documentation
├── colab/
│   ├── AVNIT_Plate_Detector_Training.ipynb   # Model 1 YOLOv8 training notebook
│   ├── AVNIT_Color_Classifier_Training.ipynb # Model 2 MobileNetV3 training notebook
│   └── AVNIT_Plate_OCR_Training.ipynb        # Model 3 ResNet-18 OCR training notebook
├── frontend/
│   ├── public/
│   │   └── AVNIT.png                   # Favicon & branding asset
│   ├── src/
│   │   ├── assets/
│   │   │   └── AVNIT.png               # Official logo asset
│   │   ├── components/
│   │   │   ├── AppHeader.vue           # Executive light header (no developer debug tags)
│   │   │   ├── VideoPlayer.vue         # PixiJS WebGL canvas overlay & video stream
│   │   │   ├── RiskGauge.vue           # Motion One radial gauge & explainability factors
│   │   │   ├── AttributeMatrix.vue     # Side-by-side observed vs registered comparison
│   │   │   ├── DetectionHistory.vue    # Chronological audit feed with search & filters
│   │   │   ├── ConnectCameraModal.vue  # Direct RTSP input & edge agent download modal
│   │   │   ├── VehicleModal.vue        # VAHAN database CRUD manager modal
│   │   │   └── StatusBanner.vue        # Real-time high-risk violation banner
│   │   ├── composables/
│   │   │   ├── useCameraChannels.js    # Multi-channel camera manager (Presets, RTSP, Webcam)
│   │   │   ├── useWebSocket.js         # Resilient streaming client with auto-reconnect
│   │   │   ├── usePixiOverlay.js       # PixiJS WebGL tactical targeting reticles
│   │   │   └── useExportReports.js     # One-click CSV and vector PDF dossier generator
│   │   ├── App.vue                     # Root executive layout (Zero Blue)
│   │   ├── index.css                   # Custom scrollbars & Tailwind base
│   │   └── main.js                     # Vue 3 application entrypoint
│   ├── index.html                      # Executive light theme HTML5 template
│   ├── package.json                    # Vue 3, PixiJS, Motion One, jsPDF dependencies
│   ├── tailwind.config.js              # Custom zero-blue executive color palette
├── run.bat                             # Master one-click startup launcher
├── README.md                           # Master Project Documentation
└── yolov8n.pt                          # Base COCO YOLOv8 Nano weights
```

---

## 👥 10. Authors & Academic Attribution

* **Project**: A.V.N.I.T. (Automated Verification of Number Plate and Identity Tampering Detection)
* **Application**: Intelligent Transportation Systems (ITS), Smart Cities, Automated Border Control & Law Enforcement
* **License**: MIT Academic License (Open Source)
