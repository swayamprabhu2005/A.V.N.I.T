from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import shutil
from ..database import (
    list_vehicles,
    get_vehicle_by_plate,
    add_vehicle,
    update_vehicle,
    delete_vehicle,
    list_alerts,
    get_stats
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
