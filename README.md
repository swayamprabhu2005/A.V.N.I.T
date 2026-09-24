# A.V.N.I.T. — AI-Based Vehicle Number Plate and Identity Tampering Detection

<div align="center">
  <img src="AVNIT.png" alt="A.V.N.I.T. Logo" width="160" style="border-radius: 20px;" />
  <h3>Automated Verification of Number Plate and Identity Tampering</h3>
  <p><strong>A Computer-Vision & Deep Learning System for Detecting Inconsistencies Between Observed Vehicles and Their Displayed Registration Plates</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python" />
    <img src="https://img.shields.io/badge/PyTorch-2.1%2B%20CPU%2FGPU-ee4c2c?logo=pytorch" alt="PyTorch" />
    <img src="https://img.shields.io/badge/YOLO-v8%20Nano-00ffff?logo=yolo" alt="YOLOv8" />
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-18%20(Vite)-61dafb?logo=react" alt="React" />
    <img src="https://img.shields.io/badge/Database-SQLite%20WAL-003B57?logo=sqlite" alt="SQLite" />
    <img src="https://img.shields.io/badge/Tests-13%20Passed-brightgreen" alt="Tests" />
  </p>
</div>

---

## 📌 Executive Summary

Conventional Automatic Number Plate Recognition (ANPR) systems primarily answer one simple question:  
> *"What alphanumeric characters are visible on this registration plate?"*

**A.V.N.I.T.** elevates that question to a critical security standard:  
> **"Does the detected plate actually belong to the vehicle carrying it?"**

A legitimate license plate can easily be mounted onto a stolen, cloned, or unauthorized vehicle using magnetic brackets or swapped plates. **A.V.N.I.T.** identifies visual and registration inconsistencies in real-time by analyzing visual vehicle attributes (vehicle type, color, OCR confidence, make/model) and cross-referencing them against an authorized registration database, producing an explainable, weighted **Risk Anomaly Score** (🟢 Likely Valid, 🟡 Needs Review, 🔴 High-Risk Identity Mismatch).

---

## ⚡ 4GB RAM PC Optimization & Cloud GPU Training Strategy

To guarantee that the system can be trained and run without requiring expensive local workstation hardware:
* **Zero Local Training**: All deep neural network training is offloaded to **Google Colab's free NVIDIA T4 GPU (16 GB VRAM)** using turn-key Jupyter Notebooks that auto-mount Google Drive and export `.pt` weights.
* **CPU-Native Local Inference**: The local pipeline uses ultra-lightweight architectures (**YOLOv8 Nano** at ~6 MB and **MobileNetV3-Small** at ~5 MB), processing frames in **~35 ms** and consuming under **250 MB of RAM**—running smoothly on standard 4GB RAM PCs without system freezing.

---

## 🏗️ System Architecture

```
                    ┌────────────────────────┐
                    │  Webcam / Video Feed   │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Vehicle Detector YOLO  │ (COCO Classes: Car, Motorcycle, Truck, Bus)
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Vehicle Tracker        │ (ByteTrack Multi-Object Persistent IDs)
                    └───────────┬────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
      ┌────────────────┐                  ┌────────────────┐
      │ Plate Detector │                  │ Vehicle Color  │
      │  (YOLOv8 Nano) │                  │ (MobileNetV3)  │
      └───────┬────────┘                  └───────┬────────┘
              │                                   │
              ▼                                   │
      ┌────────────────┐                          │
      │  OCR Normalizer│                          │
      │ (Regex Buffer) │                          │
      └───────┬────────┘                          │
              │                                   │
              └─────────────────┬─────────────────┘
                                ▼
                    ┌────────────────────────┐
                    │ 4-Factor Risk Engine   │ (Weighted Identity Mismatch Scoring)
                    └───────────┬────────────┘
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │  SQLite DB      │       │ React / Vite    │
          │ (Authorized DB) │       │ Web Dashboard   │
          └─────────────────┘       └─────────────────┘
```

---

## ⚖️ 4-Factor Risk Engine Breakdown

Instead of making rigid binary decisions, A.V.N.I.T. calculates a weighted risk score:

| Signal Factor | Weight | Evaluation Logic & Detection Role |
| :--- | :---: | :--- |
| **Vehicle Type Match** | **35%** | Compares detected class (car, motorcycle, truck, bus) against registered class. (e.g. Car carrying a motorcycle plate triggers an immediate penalty). |
| **Make & Model Match** | **25%** | Cross-references brand and model series when available in registration records. |
| **Vehicle Color Match** | **20%** | Compares visual body color against registered color (e.g. White car carrying a Black car's plate). |
| **Plate OCR Confidence** | **20%** | Validates alphanumeric reading stability and checks against standard Indian plate syntax. |

### Classification Verdicts:
* 🟢 **LIKELY VALID (Risk < 25%)**: All observed attributes match the authorized registration record.
* 🟡 **NEEDS REVIEW (Risk 25% – 60%)**: Partial OCR degradation, minor color variation, or camera angle obstruction.
* 🔴 **HIGH-RISK IDENTITY MISMATCH (Risk > 60%)**: Swapped license plate, vehicle type mismatch, or plate not registered in database.

---

## 📁 Repository Structure

```
A.V.N.I.T./
├── AVNIT.png                                   # Official Project Branding Logo
├── .gitignore                                  # Git exclusion rules (cache, venv, heavy weights)
├── DATASETS_GUIDE.md                           # Curated Kaggle & Roboflow datasets guide
├── README.md                                   # Comprehensive Project Documentation
├── colab/                                      # Google Colab GPU Training Suite
│   ├── AVNIT_Plate_Detector_Training.ipynb     # Model 1: License Plate YOLOv8n Training
│   ├── AVNIT_Color_Classifier_Training.ipynb   # Model 2: Vehicle Color MobileNetV3 Training
│   ├── AVNIT_Plate_OCR_Training.ipynb          # Model 3: Plate Character Deep CNN/CRNN Training
│   └── README_COLAB.md                         # Step-by-step Colab tutorial
├── backend/                                    # FastAPI Backend & AI Pipeline
│   ├── app/
│   │   ├── main.py                             # FastAPI entrypoint (serves API & pre-built React UI)
│   │   ├── config.py                           # Settings, paths, weights, and thresholds
│   │   ├── database.py                         # SQLite schema (vehicles, detections, alerts)
│   │   ├── seed_data.py                        # Pre-seeded test vehicles for all demo scenarios
│   │   ├── pipeline/
│   │   │   ├── coordinator.py                  # Master CV pipeline coordinator
│   │   │   ├── vehicle_detector.py             # YOLOv8 vehicle detection
│   │   │   ├── tracker.py                      # ByteTrack vehicle tracking
│   │   │   ├── plate_detector.py               # License plate localizer & heuristic fallback
│   │   │   ├── ocr_engine.py                   # Indian plate normalizer & temporal aggregator
│   │   │   ├── color_classifier.py             # MobileNetV3 color classifier & CV fallback
│   │   │   └── risk_engine.py                  # 4-Factor explainable risk engine
│   │   └── api/
│   │       ├── routes.py                       # REST API (Vehicles CRUD, Stats, Alerts)
│   │       └── websocket.py                    # Real-time WebSocket video frame streaming
│   ├── models/                                 # Trained neural network weights (.pt files)
│   │   ├── README.md                           # Documentation on placing .pt weights
│   │   └── .gitkeep                            # Git structure keeper
│   ├── data/                                   # SQLite database directory
│   │   └── .gitkeep
│   ├── test_samples/                           # Synthetic demo scenario videos (.mp4)
│   ├── tests/                                  # Automated Pytest suite (13 tests)
│   └── requirements.txt                        # Backend Python dependencies
└── frontend/                                   # Modern React (Vite + TailwindCSS) Dashboard
    ├── public/
    │   └── AVNIT.png                           # Web logo and favicon
    ├── src/
    │   ├── App.jsx                             # Main dashboard interface
    │   ├── components/
    │   │   ├── Header.jsx                      # Status banner with model readiness indicators
    │   │   ├── VideoPlayer.jsx                 # Live video viewport with HUD & source switcher
    │   │   ├── StatusBanner.jsx                # Prominent color-coded verdict card
    │   │   ├── RiskGauge.jsx                   # Radial 0-100% anomaly gauge & factor bars
    │   │   ├── AttributeMatrix.jsx             # Explainability Observed vs Registered matrix
    │   │   ├── DetectionHistory.jsx            # Audit history trail
    │   │   └── VehicleManagerModal.jsx         # In-dashboard database CRUD modal
    │   └── services/api.js                     # REST & WebSocket client
    └── dist/                                   # Pre-built production frontend bundle
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **Python 3.10+**
* **Node.js 18+** (Optional, only needed if modifying frontend source code)

### 2. Start the Backend API & Web Dashboard

Run the server using Uvicorn:
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:  
👉 **[http://localhost:8000](http://localhost:8000)**

*(The FastAPI server automatically serves the pre-compiled, high-performance React dashboard directly on port 8000).*

---

## 🎮 Pre-Packaged Demo Scenarios

The dashboard includes 4 ready-to-test demonstration video clips:

1. **Scenario 1 (Valid Identity)**: White Car displaying plate `MH12DE1433` $\rightarrow$ 🟢 **Likely Valid (GREEN)**.
2. **Scenario 2 (Plate Swapping / Type Mismatch)**: Car displaying motorcycle plate `GA07AB1234` $\rightarrow$ 🔴 **High-Risk Identity Mismatch (RED)** *(Reason: Vehicle Type Mismatch)*.
3. **Scenario 3 (Color Mismatch)**: Red Car displaying white car plate `MH12DE1433` $\rightarrow$ 🔴 **Color Mismatch Alert (RED)** *(Reason: Color Mismatch)*.
4. **Scenario 4 (Unregistered / Cloned Plate)**: Car displaying unlisted plate `DL99ZZ0000` $\rightarrow$ 🔴 **Unregistered Vehicle Alert (RED)**.

You can also toggle to **Live Webcam** mode to test real-world camera feeds.

---

## 🧠 Google Colab Deep Learning Training Suite

All 3 neural networks are trained on **Google Colab's free T4 GPU**:

| Model | Notebook | Neural Architecture | Output Weight File |
| :--- | :--- | :--- | :--- |
| **Model 1: Plate Detector** | [`colab/AVNIT_Plate_Detector_Training.ipynb`](colab/AVNIT_Plate_Detector_Training.ipynb) | YOLOv8 Nano (`yolov8n.pt`) | `plate_detector.pt` |
| **Model 2: Color Classifier** | [`colab/AVNIT_Color_Classifier_Training.ipynb`](colab/AVNIT_Color_Classifier_Training.ipynb) | MobileNetV3-Small | `color_classifier.pt` |
| **Model 3: Plate OCR** | [`colab/AVNIT_Plate_OCR_Training.ipynb`](colab/AVNIT_Plate_OCR_Training.ipynb) | Deep Character CNN / ResNet | `plate_ocr_crnn.pt` |

### How Training Works:
1. Open [Google Colab](https://colab.research.google.com) and set the accelerator to **T4 GPU** (`Runtime` $\rightarrow$ `Change runtime type` $\rightarrow$ `T4 GPU`).
2. Upload any of the 3 notebooks from `colab/` and click **Run All** (`Ctrl + F9`).
3. Each notebook automatically connects to your **Google Drive** and saves all intermediate checkpoints to `My Drive/AVNIT_Models/`.
4. Once training finishes, the notebook triggers a browser download for the `.pt` weight file.
5. Move the downloaded weights into:
   ```text
   backend/models/
   ```
6. The backend dynamically detects and hot-loads your custom trained neural networks!

*For dataset links and instructions, see [`DATASETS_GUIDE.md`](DATASETS_GUIDE.md).*

---

## 🧪 Verification & Automated Tests

A.V.N.I.T. includes a test suite covering OCR normalization, 4-factor risk scoring, SQLite CRUD, and REST endpoints:

```powershell
python -m pytest backend/tests/
```

**Results:**
```text
======================= 13 passed in 28.07s ========================
backend/tests/test_api.py ................ [PASS]
backend/tests/test_database.py ........... [PASS]
backend/tests/test_normalizer.py ......... [PASS]
backend/tests/test_risk_engine.py ........ [PASS]
```

---

## 🔒 Ethics, Privacy & Scope

* **Anomaly Detection, Not Definitive Fraud Proof**: A standard RGB camera cannot physically detect mechanical mounting mechanisms (e.g. magnets). A.V.N.I.T. highlights visual and registration discrepancies to assist human operators.
* **Controlled & Synthetic Data**: Demonstrations utilize synthetic/controlled registration databases without storing sensitive private citizen data.
* **Fair Explainability**: Every flagged risk score is accompanied by human-readable justifications explaining precisely why a vehicle was flagged.

---

## 📄 License
This prototype is developed for academic, educational, and security research purposes under the MIT License.
