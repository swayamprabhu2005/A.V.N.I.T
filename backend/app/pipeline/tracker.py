import numpy as np
from typing import List, Dict, Any, Tuple

def compute_iou(boxA, boxB) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

class VehicleTracker:
    """
    Lightweight, fast CPU tracker with persistent Track IDs.
    Matches detections across consecutive frames using IoU association and distance smoothing.
    """
    def __init__(self, max_missed_frames: int = 15, iou_threshold: float = 0.30):
        self.max_missed_frames = max_missed_frames
        self.iou_threshold = iou_threshold
        self.next_track_id = 1
        self.tracks = {}  # track_id -> dict(bbox, class_name, confidence, missed, hits)

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes current frame detections and assigns persistent track IDs.
        Returns: list of tracked vehicle dicts with track_id included.
        """
        matched_track_ids = set()
        matched_det_indices = set()
        results = []

        if self.tracks and detections:
            # Build IoU cost matrix
            track_ids = list(self.tracks.keys())
            iou_matrix = np.zeros((len(track_ids), len(detections)), dtype=float)

            for i, tid in enumerate(track_ids):
                t_box = self.tracks[tid]["bbox"]
                for j, det in enumerate(detections):
                    iou_matrix[i, j] = compute_iou(t_box, det["bbox"])

            # Greedy matching
            while True:
                max_val = np.max(iou_matrix)
                if max_val < self.iou_threshold:
                    break
                i, j = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                tid = track_ids[i]
                
                # Update matched track
                self.tracks[tid]["bbox"] = detections[j]["bbox"]
                self.tracks[tid]["class_name"] = detections[j]["class_name"]
                self.tracks[tid]["confidence"] = detections[j]["confidence"]
                self.tracks[tid]["missed"] = 0
                self.tracks[tid]["hits"] += 1

                matched_track_ids.add(tid)
                matched_det_indices.add(j)

                # Invalidate row and column
                iou_matrix[i, :] = -1
                iou_matrix[:, j] = -1

        # Create new tracks for unmatched detections
        for j, det in enumerate(detections):
            if j not in matched_det_indices:
                tid = self.next_track_id
                self.next_track_id += 1
                self.tracks[tid] = {
                    "bbox": det["bbox"],
                    "class_name": det["class_name"],
                    "confidence": det["confidence"],
                    "missed": 0,
                    "hits": 1
                }
                matched_track_ids.add(tid)

        # Increment missed frames for unmatched existing tracks
        to_delete = []
        for tid, track in self.tracks.items():
            if tid not in matched_track_ids:
                track["missed"] += 1
                if track["missed"] > self.max_missed_frames:
                    to_delete.append(tid)

        for tid in to_delete:
            del self.tracks[tid]

        # Return active tracks with >= 2 hits or immediate if new
        for tid, track in self.tracks.items():
            if track["missed"] == 0:
                results.append({
                    "track_id": tid,
                    "bbox": track["bbox"],
                    "class_name": track["class_name"],
                    "confidence": track["confidence"]
                })

        return results
