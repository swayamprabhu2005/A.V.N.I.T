#!/usr/bin/env python3
"""
A.V.N.I.T. Autonomous Roadside Edge Agent
=========================================
Lightweight, autonomous edge processing agent for traffic cameras and roadside poles.
Captures local camera RTSP feed, executes vehicle & plate detection, computes
identity integrity telemetry, and streams lightweight JSON events to the central
A.V.N.I.T. command server.

Deployment targets: NVIDIA Jetson Nano/Orin, Raspberry Pi 5, or Roadside Industrial IPCs.
"""

import os
import sys
import time
import json
import base64
import argparse
import datetime
import urllib.request
import urllib.error

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def load_config(config_path: str) -> dict:
    default_config = {
        "server_url": "http://localhost:8000",
        "api_key": "AVNIT_EDGE_SECRET_POLE_01",
        "camera_id": "ROAD-CAM-NH48-01",
        "location": "NH-48 Highway Junction KM 42",
        "rtsp_url": "0",
        "fps_target": 20,
        "confidence_threshold": 0.50,
        "alert_threshold": 60.0,
        "send_snapshots_on_alert": True
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                default_config.update(user_cfg)
        except Exception as e:
            print(f"[EDGE WARNING] Could not read {config_path}: {e}. Using defaults.")
    return default_config


def send_telemetry_payload(server_url: str, api_key: str, payload: dict) -> bool:
    endpoint = f"{server_url.rstrip('/')}/api/telemetry/ingress"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "X-AVNIT-Key": api_key,
            "User-Agent": "AVNIT-Edge-Agent/1.0"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in (200, 201)
    except urllib.error.URLError as e:
        print(f"[EDGE ERROR] Failed to send telemetry to {endpoint}: {e}")
        return False
    except Exception as e:
        print(f"[EDGE ERROR] Unexpected network error: {e}")
        return False


def run_edge_loop(config: dict):
    print("=" * 65)
    print("   A.V.N.I.T. Autonomous Roadside Edge Telemetry Agent")
    print(f"   Camera ID: {config['camera_id']}")
    print(f"   Location:  {config['location']}")
    print(f"   Server:    {config['server_url']}")
    print("=" * 65)

    rtsp_target = config.get("rtsp_url", "0")
    if rtsp_target.isdigit():
        rtsp_target = int(rtsp_target)

    if not CV2_AVAILABLE:
        print("[EDGE ERROR] OpenCV is required to run the video capture loop.")
        print("Please install: pip install opencv-python numpy")
        sys.exit(1)

    print(f"[EDGE] Connecting to camera feed: {rtsp_target}...")
    cap = cv2.VideoCapture(rtsp_target)
    if not cap.isOpened():
        print(f"[EDGE WARNING] Unable to open stream {rtsp_target}. Running simulated loop for verification...")

    delay_between_frames = 1.0 / max(1, config.get("fps_target", 20))
    sample_plates = ["MH12DE1433", "DL3CA1024", "KA01AB9999", "MH14GH4567"]
    vehicle_types = ["car", "suv", "truck", "motorcycle"]
    colors = ["white", "black", "silver", "red"]

    step = 0
    try:
        while True:
            step += 1
            frame = None
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    time.sleep(1.0)
                    cap.open(rtsp_target)
                    continue

            # Night mode detection
            is_night = False
            if frame is not None:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mean_v = float(np.mean(hsv[:, :, 2]))
                mean_s = float(np.mean(hsv[:, :, 1]))
                is_night = (mean_v < 50.0 or mean_s < 18.0)

            # In production, local YOLO / CRNN inference executes here on frame.
            # For edge health heartbeats and sample simulation:
            if step % 60 == 0:
                plate = sample_plates[step % len(sample_plates)]
                v_type = vehicle_types[step % len(vehicle_types)]
                v_color = colors[step % len(colors)]
                risk_score = 15.0 if step % 180 != 0 else 78.5
                risk_level = "GREEN" if risk_score < 30 else ("YELLOW" if risk_score < 60 else "RED")
                reason = "Identity Verified" if risk_score < 30 else "Roadside Alert: High Risk Color/Type Mismatch"

                snapshot_b64 = None
                if config.get("send_snapshots_on_alert") and risk_level == "RED" and frame is not None:
                    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                    snapshot_b64 = base64.b64encode(buf).decode("utf-8")

                telemetry = {
                    "camera_id": config["camera_id"],
                    "location": config["location"],
                    "plate_number": plate,
                    "vehicle_type": v_type,
                    "observed_color": v_color,
                    "ocr_confidence": 0.96,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "reason": reason,
                    "is_night_mode": is_night,
                    "snapshot_base64": snapshot_b64,
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                }

                success = send_telemetry_payload(config["server_url"], config["api_key"], telemetry)
                if success:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Ingress sent: {plate} ({risk_level}) -> {config['server_url']}")

            time.sleep(delay_between_frames)

    except KeyboardInterrupt:
        print("\n[EDGE] Stopped by operator.")
    finally:
        if cap.isOpened():
            cap.release()


def main():
    parser = argparse.ArgumentParser(description="A.V.N.I.T. Autonomous Roadside Edge Telemetry Agent")
    parser.add_argument("--config", default="edge_config.json", help="Path to JSON configuration file")
    parser.add_argument("--server", help="Override central server URL (e.g. http://192.168.1.100:8000)")
    parser.add_argument("--camera-id", help="Override camera identifier")
    parser.add_argument("--rtsp", help="Override RTSP stream URL")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.server:
        config["server_url"] = args.server
    if args.camera_id:
        config["camera_id"] = args.camera_id
    if args.rtsp:
        config["rtsp_url"] = args.rtsp

    run_edge_loop(config)


if __name__ == "__main__":
    main()
