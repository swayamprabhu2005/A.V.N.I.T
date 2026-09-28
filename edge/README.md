# A.V.N.I.T. Autonomous Roadside Edge Agent

This package provides a lightweight, autonomous edge processing agent for traffic cameras and roadside pole installations.

## Architecture

Instead of streaming bandwidth-heavy 4K video feeds over cellular/WAN backhauls to a central server:
1. The Edge Agent connects to the local camera via RTSP (`rtsp://user:pass@192.168.1.10:554/live`).
2. Real-time vehicle detection, plate recognition, and identity verification execute locally on the pole device (NVIDIA Jetson, Raspberry Pi 5, or Industrial IPC).
3. The Edge Agent transmits tiny **~2 KB JSON telemetry pings** to the central A.V.N.I.T. server.
4. On high-risk tampering detection, a compressed snapshot evidence crop is automatically attached.

## Quick Start

### 1. Requirements
```bash
pip install opencv-python numpy
```

### 2. Configure
Edit `edge_config.json`:
```json
{
  "server_url": "http://<central-server-ip>:8000",
  "api_key": "YOUR_AUTHORIZED_POLE_KEY",
  "camera_id": "ROAD-CAM-NH48-01",
  "location": "NH-48 Highway Junction KM 42",
  "rtsp_url": "rtsp://admin:pass@192.168.1.50:554/live",
  "send_snapshots_on_alert": true
}
```

### 3. Run
```bash
python avnit_edge_agent.py --config edge_config.json
```
