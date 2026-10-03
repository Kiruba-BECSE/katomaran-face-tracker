import cv2

from app.detector import FaceDetector


VIDEO_PATH = "input/sample.mp4"
MODEL_PATH = "models/yolov8n-face.pt"
OUTPUT_PATH = "output/detection_result.mp4"


def main():

    print("Starting YOLO Face Detection...")

    detector = FaceDetector(
        MODEL_PATH,
        confidence=0.5
    )

    video = cv2.VideoCapture(VIDEO_PATH)

    if not video.isOpened():
        print("ERROR: Could not open video.")
        return

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    output = cv2.VideoWriter(
        OUTPUT_PATH,
        fourcc,
        fps,
        (width, height)
    )

    frame_number = 0

    while True:

        success, frame = video.read()

        if not success:
            break

        frame_number += 1

        faces = detector.detect(frame)

        for face in faces:

            x1, y1, x2, y2 = face["bbox"]
            confidence = face["confidence"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            label = f"Face {confidence:.2f}"

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        output.write(frame)

        if frame_number % 100 == 0:
            print(
                f"Processed {frame_number} frames | "
                f"Faces detected: {len(faces)}"
            )

    video.release()
    output.release()

    print()
    print("Detection completed.")
    print(f"Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()