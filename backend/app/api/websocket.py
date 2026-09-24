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

@ws_router.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[AVNIT WebSocket] Client connected to live stream.")

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
                    if source_type == "scenario":
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
        if cap is not None:
            cap.release()
