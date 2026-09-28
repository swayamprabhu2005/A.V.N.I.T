import cv2
import base64
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..config import TEST_SAMPLES_DIR
from ..pipeline.coordinator import PipelineCoordinator

ws_router = APIRouter()

# Instantiate singleton pipeline engine
pipeline_engine = PipelineCoordinator()

active_connections: set = set()

async def broadcast_edge_event(event_data: dict):
    """Broadcasts external roadside telemetry events to all active dashboard WebSocket clients."""
    if not active_connections:
        return
    message = json.dumps({
        "type": "edge_telemetry",
        "data": event_data
    })
    disconnected = set()
    for ws in active_connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        active_connections.discard(ws)

@ws_router.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print(f"[AVNIT WebSocket] Client connected to live stream. Total active: {len(active_connections)}")

    cap = None
    is_running = False
    source_type = "scenario"
    scenario_filename = "scenario_1_valid.mp4"
    simulated_plate_override = None

    try:
        while True:
            # Check for client messages non-blocking
            try:
                raw_data = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                msg = json.loads(raw_data)
                action = msg.get("action")

                if action == "start":
                    source_type = msg.get("source", "scenario")
                    scenario_filename = msg.get("filename", "scenario_1_valid.mp4")
                    simulated_plate_override = msg.get("simulated_plate", None)
                    
                    if cap is not None:
                        cap.release()

                    if source_type == "webcam":
                        print("[AVNIT WebSocket] Opening webcam device 0...")
                        cap = cv2.VideoCapture(0)
                    elif source_type == "rtsp":
                        rtsp_url = msg.get("rtsp_url", "")
                        print(f"[AVNIT WebSocket] Opening RTSP network camera: {rtsp_url}")
                        cap = cv2.VideoCapture(rtsp_url)
                    else:
                        video_path = str(TEST_SAMPLES_DIR / scenario_filename)
                        print(f"[AVNIT WebSocket] Opening video scenario: {video_path}")
                        cap = cv2.VideoCapture(video_path)

                    is_running = True

                elif action == "stop":
                    is_running = False
                    if cap is not None:
                        cap.release()
                        cap = None

                elif action == "override_plate":
                    simulated_plate_override = msg.get("plate", None)

            except asyncio.TimeoutError:
                pass
            except Exception as e:
                # Malformed message or ignore
                pass

            if is_running and cap is not None:
                ret, frame = cap.read()
                if not ret:
                    # If video file ended, loop back to start
                    if source_type in ["scenario", "custom"]:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                    else:
                        is_running = False
                        continue

                if ret and frame is not None:
                    # Run AVNIT computer vision pipeline
                    annotated_frame, telemetry = pipeline_engine.process_frame(
                        frame, simulated_plate=simulated_plate_override
                    )

                    # Compress frame to JPEG
                    _, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

                    payload = {
                        "type": "frame",
                        "image": f"data:image/jpeg;base64,{jpg_as_text}",
                        "telemetry": telemetry
                    }

                    await websocket.send_text(json.dumps(payload))

            # Maintain smooth ~18-22 FPS to preserve CPU on 4GB RAM
            await asyncio.sleep(0.045)

    except WebSocketDisconnect:
        print("[AVNIT WebSocket] Client disconnected.")
    except Exception as e:
        print(f"[AVNIT WebSocket] Stream error: {e}")
    finally:
        active_connections.discard(websocket)
        if cap is not None:
            cap.release()

