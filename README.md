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

Standard Automatic Number Plate Recognition (ANPR) systems suffer from a critical security vulnerability: **they only transcribe characters, completely blind to whether a plate has been illegally cloned or attached to a stolen vehicle.**

> **The Core Problem**: Conventional ANPR only reads characters; it cannot detect if a genuine registration plate has been cloned, forged, or transferred to an unauthorized vehicle.
>
> **The A.V.N.I.T. Solution**: Transforms ANPR into an autonomous **Identity Cross-Verification Platform**. It extracts multimodal visual intelligence (**Vehicle Type, Exterior Color, Plate Geometry, and Character Topology**) and cross-references it against official motor vehicle registry databases (e.g., VAHAN) in real time to detect fraud instantly.

### Real-Time Anomaly Scoring Matrix

| Verdict Level | Risk Score | Operational Trigger | Visual Status |
| :--- | :---: | :--- | :---: |
| **Verified Pass** | `< 30%` | Visual attributes (type, color, plate) match registry records with high optical confidence | 🟢 **PASS** |
| **Variance Review** | `30% – 59%` | Minor color shifts, low-light/weather variance, or partial camera angle occlusions | 🟡 **REVIEW** |
| **Critical Tampering** | `>= 60%` | Severe identity mismatch (e.g., cloned plates on wrong vehicle type or color) | 🔴 **ALERT** |

---

## 🧠 2. Trained Deep Learning Neural Networks & Models

All custom models were trained on **Google Colab (NVIDIA Tesla T4 GPU, 16 GB VRAM)** using turn-key Jupyter Notebooks and exported directly to `backend/models/`.

| Model & Weights | AI Architecture & Type | Dataset Provenance | Benchmark Accuracy | Footprint | Primary Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Plate Detector**<br>[`plate_detector.pt`](backend/models/plate_detector.pt) | **Deep Learning (CNN)**<br>Ultralytics YOLOv8 Nano | [Car Plate Detection](https://www.kaggle.com/datasets/andrewmvd/car-plate-detection)<br>*(433 images, YOLO format)* | **99.44% mAP@50**<br>• Precision: 98.8%<br>• Recall: 100.0%<br>• Inference: ~12 ms | 3.2M params<br>`6.25 MB` | Sub-pixel license plate localization across diverse lighting & angles |
| **Color Classifier**<br>[`color_classifier.pt`](backend/models/color_classifier.pt) | **Deep Learning (CNN)**<br>MobileNetV3-Small | [VCoR Vehicle Color](https://www.kaggle.com/datasets/landrykezebou/vcor-vehicle-color-recognition-dataset)<br>*(10,645 crops, 15 colors)* | **99.39% Val Accuracy**<br>• Loss: 0.0245<br>• Cross-Entropy<br>• Inference: ~8 ms | 1.5M params<br>`6.27 MB` | 15-class exterior color classification to detect swapped/cloned plates |
| **Plate OCR Verifier**<br>[`plate_ocr_crnn.pt`](backend/models/plate_ocr_crnn.pt) | **Deep Learning (Residual CNN)**<br>ResNet-18 (8 Residual Blocks) | [Plate Digits Classification](https://www.kaggle.com/datasets/aladdinss/license-plate-digits-classification-dataset)<br>*(17,565 crops, 36 classes)* | **100.00% Val Accuracy**<br>• Training: 100.00%<br>• Loss: 0.0001<br>• Inference: ~15 ms | 11.2M params<br>`44.86 MB` | Character-level topological verification to catch taped digit alterations |
| **Sequence OCR Reader**<br>`EasyOCR (Integrated)` | **Deep Learning (CRNN)**<br>VGG/ResNet + BiLSTM + CTC | Pretrained Multi-Language Alphanumeric + Indian Syntax Regex | **High-Fidelity OCR**<br>• Position-aware normalization<br>• Temporal majority voting | Dynamic Seq<br>CPU-tuned | Full alphanumeric transcription with Indian RTO standard syntax matching |
| **Vehicle Detector**<br>[`yolov8n.pt`](yolov8n.pt) | **Deep Learning (CNN)**<br>YOLOv8 Nano (MS COCO) | MS COCO 2017 Benchmark<br>*(Extracts car, bus, truck, motorcycle)* | **>95% Vehicle Recall**<br>• 37.3% mAP@50 (COCO) | 3.2M params<br>`6.25 MB` | Vehicle bounding box extraction and ByteTrack motion state tracking |

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

### 🖥️ Frontend Architecture (Modernized Vue 3)

| Layer / Module | Technology | Version | Key Capabilities & Architectural Highlights |
| :--- | :--- | :---: | :--- |
| **Core Framework** | ![Vue.js](https://img.shields.io/badge/Vue.js-3.4-42b883?style=flat-square&logo=vuedotjs&logoColor=white) | `v3.4.31` | Composition API (`<script setup>`), reactive ref telemetry store, and modular composables. |
| **Build & Tooling** | ![Vite](https://img.shields.io/badge/Vite-5.3-646cff?style=flat-square&logo=vite&logoColor=white) | `v5.3.1` | Ultra-fast Hot Module Replacement (HMR) and optimized Rollup code-splitting. |
| **WebGL HUD Engine** | ![PixiJS](https://img.shields.io/badge/PixiJS-v7.4-e91e63?style=flat-square&logo=pixijs&logoColor=white) | `v7.4.2` | GPU-accelerated canvas overlay rendering sub-pixel targeting brackets, track IDs, and HUD cards at 60 FPS. |
| **Motion Physics** | ![Motion](https://img.shields.io/badge/Motion_One-10.16-f59e0b?style=flat-square) | `v10.16.2` | Spring-physics animated radial sweep (0–100%) on the Bayesian Risk Gauge. |
| **Reporting Engine** | ![jsPDF](https://img.shields.io/badge/jsPDF-2.5-e11d48?style=flat-square) | `v2.5.1` | Instant client-side generation of CSV spreadsheets and formatted vector PDF Law Enforcement Dossiers. |
| **Design System** | ![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.4-06b6d4?style=flat-square&logo=tailwindcss&logoColor=white) | `v3.4.4` | Executive Enterprise Light Theme with warm off-whites, neutral slate cards, and **strictly zero shades of blue**. |
| **Iconography** | ![Lucide](https://img.shields.io/badge/Lucide_Vue-0.39-f43f5e?style=flat-square) | `v0.395.0` | Crisp modern vector iconography tailored for transportation and security dashboards. |

### ⚙️ Backend Architecture

| Layer / Module | Technology | Version | Key Capabilities & Architectural Highlights |
| :--- | :--- | :---: | :--- |
| **API Framework** | ![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white) | `v0.100+` | Asynchronous non-blocking REST endpoints, persistent WebSockets, and automatic Swagger docs (`/docs`). |
| **Inference Engine** | ![PyTorch](https://img.shields.io/badge/PyTorch-2.6%2B-ee4c2c?style=flat-square&logo=pytorch&logoColor=white) | `v2.6+` | CPU-optimized deep learning inference pipeline (~35 ms total latency per frame on 4GB RAM PCs). |
| **Vision Runtime** | ![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5c3ee8?style=flat-square&logo=opencv&logoColor=white) | `v4.8+` | Video decoding, real-time CLAHE contrast enhancement, and automatic night mode HSV detection. |
| **Vehicle Tracker** | ![ByteTrack](https://img.shields.io/badge/ByteTrack-Kalman-10b981?style=flat-square) | Built-in | 8-dimensional Kalman Filters and Hungarian assignment algorithm for persistent vehicle track association. |
| **Registry Database** | ![SQLite](https://img.shields.io/badge/SQLite-WAL_Mode-003B57?style=flat-square&logo=sqlite&logoColor=white) | Native | Write-Ahead Logging (WAL) for thread-safe concurrent reads/writes of VAHAN records and audit trails. |
| **Edge Ingress** | ![Edge](https://img.shields.io/badge/Edge_Ingress-REST-18181b?style=flat-square) | Built-in | Lightweight `POST /api/telemetry/ingress` endpoint receiving 2 KB telemetry pings from roadside pole agents. |
| **Automated Testing**| ![pytest](https://img.shields.io/badge/pytest-9.1-0a9edc?style=flat-square&logo=pytest&logoColor=white) | `v9.1.1` | Comprehensive test suite covering API endpoints, database CRUD, OCR normalizer, and risk engine (16/16 pass). |

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
