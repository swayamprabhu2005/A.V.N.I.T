import sqlite3
import datetime
from typing import List, Optional, Dict, Any
from .config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high performance concurrent reading/writing
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Vehicles table (Controlled registration database)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_number TEXT UNIQUE NOT NULL,
        vehicle_type TEXT NOT NULL,
        color TEXT NOT NULL,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        registration_status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Detections table (Tracked plate observations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER NOT NULL,
        plate_number TEXT NOT NULL,
        ocr_confidence REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Observations table (Visual attributes extracted by models)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS observations (
        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        detection_id INTEGER NOT NULL,
        observed_type TEXT NOT NULL,
        observed_color TEXT NOT NULL,
        observed_make TEXT DEFAULT '',
        observed_model TEXT DEFAULT '',
        FOREIGN KEY (detection_id) REFERENCES detections (detection_id)
    );
    """)

    # 4. Alerts table (Risk Engine results and explainability)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        detection_id INTEGER,
        plate_number TEXT NOT NULL,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        reason TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create Indexes for fast querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plate_number ON vehicles(plate_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC);")
    
    conn.commit()
    conn.close()

# Vehicle CRUD helpers
def get_vehicle_by_plate(plate_number: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles WHERE UPPER(plate_number) = UPPER(?)", (plate_number.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def list_vehicles() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles ORDER BY vehicle_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_vehicle(plate_number: str, vehicle_type: str, color: str, make: str, model: str, registration_status: str = "Active") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO vehicles (plate_number, vehicle_type, color, make, model, registration_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (plate_number.upper().strip(), vehicle_type.lower().strip(), color.lower().strip(), make.strip(), model.strip(), registration_status))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_vehicle(vehicle_id: int, plate_number: str, vehicle_type: str, color: str, make: str, model: str, registration_status: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vehicles
        SET plate_number = ?, vehicle_type = ?, color = ?, make = ?, model = ?, registration_status = ?
        WHERE vehicle_id = ?
    """, (plate_number.upper().strip(), vehicle_type.lower().strip(), color.lower().strip(), make.strip(), model.strip(), registration_status, vehicle_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_vehicle(vehicle_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Detection & Alert Logging
def log_event(track_id: int, plate_number: str, ocr_confidence: float, observed_type: str, 
              observed_color: str, risk_score: float, risk_level: str, reason: str,
              observed_make: str = "", observed_model: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert detection
    cursor.execute("""
        INSERT INTO detections (track_id, plate_number, ocr_confidence)
        VALUES (?, ?, ?)
    """, (track_id, plate_number, ocr_confidence))
    detection_id = cursor.lastrowid

    # Insert observation
    cursor.execute("""
        INSERT INTO observations (detection_id, observed_type, observed_color, observed_make, observed_model)
        VALUES (?, ?, ?, ?, ?)
    """, (detection_id, observed_type.lower(), observed_color.lower(), observed_make, observed_model))

    # Insert alert
    cursor.execute("""
        INSERT INTO alerts (detection_id, plate_number, risk_score, risk_level, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (detection_id, plate_number, risk_score, risk_level, reason))
    alert_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return alert_id

def list_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.alert_id, a.plate_number, a.risk_score, a.risk_level, a.reason, a.timestamp,
               d.ocr_confidence, d.track_id,
               o.observed_type, o.observed_color, o.observed_make, o.observed_model
        FROM alerts a
        LEFT JOIN detections d ON a.detection_id = d.detection_id
        LEFT JOIN observations o ON d.detection_id = o.detection_id
        ORDER BY a.alert_id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM detections")
    total_detections = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE risk_level = 'RED'")
    high_risk_alerts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE risk_level = 'YELLOW'")
    medium_risk_alerts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE risk_level = 'GREEN'")
    valid_passes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_vehicles = cursor.fetchone()[0]

    conn.close()
    return {
        "total_detections": total_detections,
        "valid_passes": valid_passes,
        "medium_risk_alerts": medium_risk_alerts,
        "high_risk_alerts": high_risk_alerts,
        "registered_vehicles": total_vehicles
    }
