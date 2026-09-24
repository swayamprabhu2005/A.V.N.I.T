import os
import cv2
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

def create_synthetic_vehicle_frame(
    bg_color=(45, 52, 54),
    vehicle_type="car",
    vehicle_color="white",
    plate_text="MH12DE1433",
    frame_idx=0,
    total_frames=90
):
    """Draws a clean, stylized vehicle with a high-contrast license plate moving across the frame."""
    width, height = 640, 480
    frame = np.full((height, width, 3), bg_color, dtype=np.uint8)

    # Road surface
    cv2.rectangle(frame, (0, 280), (width, height), (30, 30, 30), -1)
    # Road markings
    for x in range(0, width, 80):
        cv2.rectangle(frame, (x, 375), (x + 40, 385), (200, 200, 200), -1)

    # Calculate horizontal vehicle trajectory
    # Vehicle drives from left to right
    progress = frame_idx / max(1, total_frames - 1)
    center_x = int(-100 + progress * (width + 200))
    center_y = 310

    # Color definitions
    color_map = {
        "white": (240, 240, 240),
        "black": (20, 20, 20),
        "red": (30, 30, 210),
        "blue": (200, 60, 30),
        "silver_grey": (160, 160, 160)
    }
    car_rgb = color_map.get(vehicle_color.lower(), (240, 240, 240))

    if vehicle_type == "car":
        # Vehicle Body
        vx1, vy1 = center_x - 120, center_y - 60
        vx2, vy2 = center_x + 120, center_y + 40
        cv2.rectangle(frame, (vx1, vy1 + 25), (vx2, vy2), car_rgb, -1)
        cv2.rectangle(frame, (vx1, vy1 + 25), (vx2, vy2), (0, 0, 0), 2)
        # Cabin / Roof
        pts = np.array([
            [center_x - 70, vy1 + 25],
            [center_x - 40, vy1 - 25],
            [center_x + 50, vy1 - 25],
            [center_x + 80, vy1 + 25]
        ], np.int32)
        cv2.fillPoly(frame, [pts], car_rgb)
        cv2.polylines(frame, [pts], True, (0, 0, 0), 2)
        # Windows
        win_pts = np.array([
            [center_x - 35, vy1 - 20],
            [center_x + 45, vy1 - 20],
            [center_x + 70, vy1 + 20],
            [center_x - 60, vy1 + 20]
        ], np.int32)
        cv2.fillPoly(frame, [win_pts], (180, 210, 230))
        # Wheels
        cv2.circle(frame, (center_x - 70, vy2), 22, (10, 10, 10), -1)
        cv2.circle(frame, (center_x - 70, vy2), 10, (150, 150, 150), -1)
        cv2.circle(frame, (center_x + 70, vy2), 22, (10, 10, 10), -1)
        cv2.circle(frame, (center_x + 70, vy2), 10, (150, 150, 150), -1)

        # License Plate (White plate with black text and border)
        px1, py1 = center_x - 55, vy2 - 32
        px2, py2 = center_x + 55, vy2 - 8
        cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 255, 255), -1)
        cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 0, 0), 2)
        # Plate Text
        cv2.putText(frame, plate_text, (px1 + 6, py2 - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)

    elif vehicle_type == "motorcycle":
        # Motorcycle representation
        mx, my = center_x, center_y
        # Frame and wheels
        cv2.circle(frame, (mx - 45, my + 25), 18, (15, 15, 15), -1)
        cv2.circle(frame, (mx + 45, my + 25), 18, (15, 15, 15), -1)
        cv2.line(frame, (mx - 45, my + 25), (mx, my - 10), car_rgb, 6)
        cv2.line(frame, (mx + 45, my + 25), (mx, my - 10), car_rgb, 6)
        cv2.line(frame, (mx, my - 10), (mx + 20, my - 35), (80, 80, 80), 4) # handlebar
        # Rider helmet & body
        cv2.circle(frame, (mx - 5, my - 55), 16, (30, 30, 30), -1)
        cv2.rectangle(frame, (mx - 15, my - 40), (mx + 10, my - 10), (50, 50, 120), -1)
        # License Plate
        px1, py1 = mx - 45, my + 42
        px2, py2 = mx + 45, my + 62
        cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 255, 255), -1)
        cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 0, 0), 2)
        cv2.putText(frame, plate_text, (px1 + 4, py2 - 5),
                    cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

    return frame

def generate_video(filename: str, vehicle_type: str, vehicle_color: str, plate_text: str, total_frames: int = 75):
    out_path = OUT_DIR / filename
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(out_path), fourcc, 25.0, (640, 480))

    for i in range(total_frames):
        f = create_synthetic_vehicle_frame(
            vehicle_type=vehicle_type,
            vehicle_color=vehicle_color,
            plate_text=plate_text,
            frame_idx=i,
            total_frames=total_frames
        )
        writer.write(f)

    writer.release()
    print(f"[AVNIT] Generated synthetic scenario video: {out_path.name}")

def generate_all_scenarios():
    print("[AVNIT] Generating synthetic demo scenario videos...")
    # Scenario 1: Legitimate White Car (Registered: MH12DE1433 -> Car, White)
    generate_video("scenario_1_valid.mp4", "car", "white", "MH12DE1433")
    
    # Scenario 2: Identity Mismatch / Plate Swapping (White Car displaying Motorcycle plate GA07AB1234)
    generate_video("scenario_2_type_mismatch.mp4", "car", "white", "GA07AB1234")

    # Scenario 3: Color Mismatch (Red Car displaying White Car plate MH12DE1433)
    generate_video("scenario_3_color_mismatch.mp4", "car", "red", "MH12DE1433")

    # Scenario 4: Unregistered Cloned Plate (Car displaying unlisted plate DL99ZZ0000)
    generate_video("scenario_4_unregistered.mp4", "car", "silver_grey", "DL99ZZ0000")

if __name__ == "__main__":
    generate_all_scenarios()
