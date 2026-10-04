import cv2
import json
import os

from app.database import Database
from app.detector import FaceDetector
from app.recognizer import FaceRecognizer
from app.face_manager import FaceManager
from app.tracker import SimpleTracker
from app.logger import EventLogger
from app.event_manager import EventManager


CONFIG_PATH = "config.json"


def load_config():

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def crop_face(frame, bbox):

    x1, y1, x2, y2 = bbox

    height, width = frame.shape[:2]

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)

    if x2 <= x1 or y2 <= y1:
        return None

    return frame[y1:y2, x1:x2].copy()


def main():

    print("Starting Katomaran Face Tracker...")

    config = load_config()

    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    database = Database("database.db")

    detector = FaceDetector(
        config["yolo_model"],
        config["detection_confidence"]
    )

    recognizer = FaceRecognizer(
        config["recognition_threshold"]
    )

    face_manager = FaceManager(
        database,
        recognizer
    )

    tracker = SimpleTracker(
        config["tracking_max_missing_frames"]
    )

    logger = EventLogger(
        config["event_log"]
    )

    event_manager = EventManager(
        database,
        logger,
        config["entry_log_folder"],
        config["exit_log_folder"]
    )

    video_source = config["video_source"]

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():

        print("ERROR: Could not open video.")

        database.close()

        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    output_path = config["output_video"]

    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    if not writer.isOpened():

        print("ERROR: Could not create output video.")

        cap.release()
        database.close()

        return

    detection_skip = config["detection_skip_frames"]

    detection_interval = detection_skip + 1

    frame_number = 0

    track_face_ids = {}

    last_face_images = {}

    current_tracks = []

    print("Processing video...")

    logger.info("SYSTEM STARTED")

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_number += 1

        # Run YOLO periodically
        if frame_number % detection_interval == 0:

            detections = detector.detect(frame)

            print(
                f"Frame {frame_number}: "
                f"{len(detections)} faces detected"
            )

            logger.info(
                f"Detection cycle | "
                f"Frame {frame_number} | "
                f"Faces {len(detections)}"
            )

            current_tracks = tracker.update(
                detections
            )

        # Draw every current track
        for track in current_tracks:

            track_id = track["track_id"]

            x1, y1, x2, y2 = track["bbox"]

            face_image = crop_face(
                frame,
                track["bbox"]
            )

            if face_image is not None:

                last_face_images[track_id] = face_image

            # Recognize/register the track
            if (
                track_id not in track_face_ids
                and face_image is not None
            ):

                embedding = recognizer.get_embedding(
                    face_image
                )

                if embedding is not None:

                    logger.info(
                        f"Embedding generated | "
                        f"Track {track_id}"
                    )

                    result = face_manager.recognize_or_register(
                        embedding
                    )

                    face_id = result["face_id"]

                    track_face_ids[track_id] = face_id

                    if result["new_face"]:

                        logger.info(
                            f"Face registered | "
                            f"{face_id}"
                        )

                    else:

                        logger.info(
                            f"Face recognized | "
                            f"{face_id} | "
                            f"Similarity "
                            f"{result['similarity']:.3f}"
                        )

                    event_manager.register_entry(
                        face_id,
                        face_image
                    )

            # Draw bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )

            # Get face ID
            face_id = track_face_ids.get(
                track_id,
                "REGISTERING"
            )

            label = (
                f"{face_id} "
                f"Track:{track_id}"
            )

            # Label background
            (text_width, text_height), baseline = (
                cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    2
                )
            )

            cv2.rectangle(
                frame,
                (
                    x1,
                    max(
                        0,
                        y1 - text_height - baseline - 10
                    )
                ),
                (
                    x1 + text_width + 10,
                    y1
                ),
                (0, 255, 0),
                -1
            )

            # Label text
            cv2.putText(
                frame,
                label,
                (
                    x1 + 5,
                    y1 - 5
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2
            )

        # Write annotated frame
        writer.write(frame)

        # Display annotated frame
        cv2.imshow(
            "Katomaran Face Tracker",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    # Register exit events for active faces
    for track_id, face_id in list(
        track_face_ids.items()
    ):

        face_image = last_face_images.get(
            track_id
        )

        if face_image is not None:

            event_manager.register_exit(
                face_id,
                face_image
            )

            logger.info(
                f"Face exit | "
                f"{face_id} | "
                f"Track {track_id}"
            )

    cap.release()

    writer.release()

    cv2.destroyAllWindows()

    logger.info("SYSTEM STOPPED")

    print("\nProcessing completed.")

    print(
        "Unique visitors:",
        database.get_unique_visitor_count()
    )

    print(
        "Output video:",
        output_path
    )

    database.close()


if __name__ == "__main__":
    main()