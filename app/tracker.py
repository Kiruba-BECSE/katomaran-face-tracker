import math


class SimpleTracker:

    def __init__(self, max_missing_frames=30):

        self.max_missing_frames = max_missing_frames
        self.next_track_id = 1
        self.tracks = {}

    def calculate_center(self, bbox):

        x1, y1, x2, y2 = bbox

        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2
        )

    def calculate_distance(self, p1, p2):

        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2
        )

    def update(self, detections):

        new_tracks = {}
        used_tracks = set()

        for detection in detections:

            bbox = detection["bbox"]

            center = self.calculate_center(bbox)

            best_track = None
            best_distance = float("inf")

            for track_id, track in self.tracks.items():

                if track_id in used_tracks:
                    continue

                distance = self.calculate_distance(
                    center,
                    track["center"]
                )

                if distance < best_distance and distance < 150:

                    best_distance = distance
                    best_track = track_id

            if best_track is None:

                best_track = self.next_track_id
                self.next_track_id += 1

            new_tracks[best_track] = {
                "track_id": best_track,
                "bbox": bbox,
                "center": center,
                "missing_frames": 0
            }

            used_tracks.add(best_track)

        for track_id, track in self.tracks.items():

            if track_id not in new_tracks:

                track["missing_frames"] += 1

                if track["missing_frames"] <= self.max_missing_frames:

                    new_tracks[track_id] = track

        self.tracks = new_tracks

        return list(self.tracks.values())