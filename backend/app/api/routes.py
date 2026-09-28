from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
import shutil
from ..database import (
    list_vehicles,
    get_vehicle_by_plate,
    add_vehicle,
    update_vehicle,
    delete_vehicle,
    list_alerts,
    get_stats,
    log_event
)
from ..config import (
    TEST_SAMPLES_DIR,
    PLATE_DETECTOR_WEIGHTS,
    COLOR_CLASSIFIER_WEIGHTS,
    PLATE_OCR_WEIGHTS,
    YOLO_VEHICLE_WEIGHTS
)

router = APIRouter(prefix="/api")

# Pydantic Schemas
class VehicleCreateSchema(BaseModel):
    plate_number: str = Field(..., json_schema_extra={"example": "MH12DE1433"})
    vehicle_type: str = Field(..., json_schema_extra={"example": "car"})
    color: str = Field(..., json_schema_extra={"example": "white"})
    make: str = Field(..., json_schema_extra={"example": "Hyundai"})
    model: str = Field(..., json_schema_extra={"example": "i20"})
    registration_status: str = Field("Active", json_schema_extra={"example": "Active"})

class VehicleUpdateSchema(BaseModel):
    plate_number: str
    vehicle_type: str
    color: str
    make: str
    model: str
    registration_status: str = "Active"

# 1. Vehicle CRUD Endpoints
@router.get("/vehicles", response_model=List[Dict[str, Any]])
def get_all_vehicles():
    return list_vehicles()

@router.get("/vehicles/{plate_number}")
def get_vehicle(plate_number: str):
    v = get_vehicle_by_plate(plate_number)
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle plate not found in database.")
    return v

@router.post("/vehicles", status_code=201)
def create_vehicle(payload: VehicleCreateSchema):
    existing = get_vehicle_by_plate(payload.plate_number)
    if existing:
        raise HTTPException(status_code=400, detail="A vehicle with this plate number is already registered.")
    new_id = add_vehicle(
        plate_number=payload.plate_number,
        vehicle_type=payload.vehicle_type,
        color=payload.color,
        make=payload.make,
        model=payload.model,
        registration_status=payload.registration_status
    )
    return {"message": "Vehicle registered successfully", "vehicle_id": new_id}

@router.put("/vehicles/{vehicle_id}")
def edit_vehicle(vehicle_id: int, payload: VehicleUpdateSchema):
    success = update_vehicle(
        vehicle_id=vehicle_id,
        plate_number=payload.plate_number,
        vehicle_type=payload.vehicle_type,
        color=payload.color,
        make=payload.make,
        model=payload.model,
        registration_status=payload.registration_status
    )
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found or could not be updated.")
    return {"message": "Vehicle updated successfully"}

@router.delete("/vehicles/{vehicle_id}")
def remove_vehicle(vehicle_id: int):
    success = delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found or already deleted.")
    return {"message": "Vehicle deleted successfully"}

# 2. Alerts and System Stats
@router.get("/alerts")
def get_alerts(limit: int = Query(50, ge=1, le=200)):
    return list_alerts(limit=limit)

@router.get("/stats")
def get_system_stats():
    return get_stats()

# 3. Demo Scenarios & Videos
@router.get("/scenarios")
def list_available_scenarios():
    scenarios = []
    if os.path.exists(TEST_SAMPLES_DIR):
        for f in os.listdir(TEST_SAMPLES_DIR):
            if f.endswith(".mp4"):
                scenarios.append({
                    "filename": f,
                    "name": f.replace(".mp4", "").replace("_", " ").title(),
                    "path": str(TEST_SAMPLES_DIR / f)
                })
    return scenarios

@router.post("/upload-video")
async def upload_custom_video(file: UploadFile = File(...)):
    file_path = TEST_SAMPLES_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Video uploaded successfully", "filename": file.filename}

# 4. System & Model Status
@router.get("/system/status")
def check_system_status():
    return {
        "status": "online",
        "models": {
            "yolo_vehicle": {
                "loaded": True,
                "note": "Pre-trained YOLOv8n COCO (Vehicle Detector)"
            },
            "plate_detector": {
                "loaded": os.path.exists(PLATE_DETECTOR_WEIGHTS),
                "path": str(PLATE_DETECTOR_WEIGHTS),
                "source": "Colab-trained" if os.path.exists(PLATE_DETECTOR_WEIGHTS) else "Heuristic Fallback Active"
            },
            "color_classifier": {
                "loaded": os.path.exists(COLOR_CLASSIFIER_WEIGHTS),
                "path": str(COLOR_CLASSIFIER_WEIGHTS),
                "source": "Colab-trained" if os.path.exists(COLOR_CLASSIFIER_WEIGHTS) else "CV HSV Fallback Active"
            },
            "plate_ocr": {
                "loaded": os.path.exists(PLATE_OCR_WEIGHTS),
                "path": str(PLATE_OCR_WEIGHTS),
                "source": "Colab-trained" if os.path.exists(PLATE_OCR_WEIGHTS) else "EasyOCR / Regex Fallback Active"
            }
        },
        "specs": "4GB RAM CPU Optimized Engine"
    }

# 5. Roadside & Government Camera Edge Telemetry Ingress
EDGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "edge"

class EdgeTelemetrySchema(BaseModel):
    camera_id: str = Field(..., json_schema_extra={"example": "DELHI-NH48-POLE-14"})
    location: str = Field(default="NH-48 KM 24", json_schema_extra={"example": "NH-48 KM 24"})
    plate_number: str = Field(..., json_schema_extra={"example": "MH12DE1433"})
    vehicle_type: str = Field(..., json_schema_extra={"example": "car"})
    observed_color: str = Field(..., json_schema_extra={"example": "white"})
    ocr_confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str = Field(..., json_schema_extra={"example": "GREEN"})
    reason: str = Field(default="Identity Verified")
    observed_make: Optional[str] = ""
    observed_model: Optional[str] = ""
    snapshot_base64: Optional[str] = None
    is_night_mode: Optional[bool] = False
    timestamp: Optional[str] = None

@router.post("/telemetry/ingress", status_code=201)
async def ingest_edge_telemetry(payload: EdgeTelemetrySchema):
    """
    Receives autonomous telemetry pings from roadside edge camera agents.
    Persists detection and alert events to SQLite and broadcasts to live dashboards.
    """
    alert_id = log_event(
        track_id=0,
        plate_number=payload.plate_number,
        ocr_confidence=payload.ocr_confidence,
        observed_type=payload.vehicle_type,
        observed_color=payload.observed_color,
        risk_score=payload.risk_score,
        risk_level=payload.risk_level,
        reason=f"[{payload.camera_id} @ {payload.location}] {payload.reason}",
        observed_make=payload.observed_make or "",
        observed_model=payload.observed_model or ""
    )

    # Broadcast to connected dashboard WebSockets
    try:
        from .websocket import broadcast_edge_event
        data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        await broadcast_edge_event(data)
    except Exception:
        pass

    return {
        "status": "received",
        "alert_id": alert_id,
        "camera_id": payload.camera_id,
        "risk_level": payload.risk_level
    }

@router.get("/edge/agent-script")
def download_edge_agent():
    """Serves the standalone autonomous roadside edge agent script for deployment."""
    script_path = EDGE_DIR / "avnit_edge_agent.py"
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Edge agent script not found on server.")
    return FileResponse(
        path=str(script_path),
        filename="avnit_edge_agent.py",
        media_type="text/x-python"
    )

@router.get("/edge/default-config")
def download_edge_config():
    """Serves the default JSON configuration template for roadside edge agents."""
    config_path = EDGE_DIR / "edge_config.json"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Edge config template not found on server.")
    return FileResponse(
        path=str(config_path),
        filename="edge_config.json",
        media_type="application/json"
    )

