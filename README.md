# Katomaran Intelligent Face Tracker

An intelligent face tracking system that detects faces, automatically
registers new visitors, recognizes previously registered visitors,
tracks them through the video, records entry/exit events, stores cropped
face images, and maintains visitor metadata in SQLite.

## Hackathon Objective

The system is designed for the Katomaran hackathon requirement:

-   YOLO-based face detection
-   InsightFace/ArcFace-based face recognition
-   Automatic registration of new faces
-   Unique face IDs
-   Continuous tracking
-   Entry and exit event logging
-   Cropped face image storage
-   SQLite metadata storage
-   Unique visitor counting
-   Configurable detection interval
-   Structured logs for important AI and tracking events

## Architecture

``` mermaid
flowchart TD
    A[Input Video] --> B[YOLO Face Detector]
    B --> C[Simple Centroid Tracker]
    C --> D{Track Already Recognized?}
    D -- No --> E[InsightFace Embedding]
    E --> F[Face Manager]
    F --> G{Existing Face Match?}
    G -- Yes --> H[Existing FACE ID]
    G -- No --> I[Register New FACE ID]
    H --> J[Track Face]
    I --> J
    D -- Yes --> J
    J --> K[Entry / Exit Event Manager]
    K --> L[Face Crop Images]
    K --> M[SQLite Database]
    K --> N[events.log]
    J --> O[Annotated Output Video]
```

## Project Structure

``` text
katomaran-face-tracker/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── detector.py
│   ├── recognizer.py
│   ├── tracker.py
│   ├── database.py
│   ├── logger.py
│   ├── event_manager.py
│   ├── face_manager.py
│   └── video_processor.py
│
├── models/
│   └── yolov8n-face.pt
│
├── input/
│   └── sample.mp4
│
├── logs/
│   ├── entries/
│   ├── exits/
│   └── events.log
│
├── output/
│   └── tracked_output.mp4
│
├── database.db
├── config.json
├── requirements.txt
├── AI_PLANNING.md
├── ARCHITECTURE.md
└── README.md
```

## Technologies

-   Python
-   OpenCV
-   Ultralytics YOLO
-   InsightFace
-   ArcFace embeddings through InsightFace
-   NumPy
-   SQLite
-   JSON configuration
-   Centroid-based object tracking

## Main Processing Flow

1.  The input video is opened using OpenCV.
2.  YOLO detects faces at the configured detection interval.
3.  The tracker assigns a track ID to each detected face.
4.  InsightFace generates an embedding for a face when recognition is
    required.
5.  The Face Manager compares the embedding with registered embeddings.
6.  If a match exists, the existing `FACE_XXX` ID is reused.
7.  If there is no match, a new unique face ID is automatically created.
8.  The first appearance of an active face generates an entry event.
9.  The face remains associated with its track while visible.
10. When processing finishes, active visitors receive an exit event.
11. Cropped face images are stored under date-based entry/exit folders.
12. Event metadata is stored in SQLite.
13. Important operations are written to `logs/events.log`.
14. The processed video is written to `output/tracked_output.mp4`.

## Configuration

`config.json` controls the main parameters:

``` json
{
    "video_source": "input/sample.mp4",
    "yolo_model": "models/yolov8n-face.pt",
    "detection_skip_frames": 5,
    "detection_confidence": 0.5,
    "recognition_threshold": 0.5,
    "tracking_max_missing_frames": 30,
    "output_video": "output/tracked_output.mp4",
    "entry_log_folder": "logs/entries",
    "exit_log_folder": "logs/exits",
    "event_log": "logs/events.log"
}
```

### Important parameters

`detection_skip_frames` controls how many frames are skipped between
detection cycles.

`detection_confidence` controls the minimum YOLO confidence.

`recognition_threshold` controls the cosine-similarity threshold used
for face matching.

`tracking_max_missing_frames` controls how long a track can remain
missing.

## Installation

Create and activate a virtual environment:

``` cmd
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

``` cmd
pip install -r requirements.txt
```

## Run

From the project root:

``` cmd
python -m app.video_processor
```

The first InsightFace execution may download the required `buffalo_l`
model automatically.

## Output

After processing:

### Annotated video

``` text
output/tracked_output.mp4
```

### Entry images

``` text
logs/entries/YYYY-MM-DD/
```

### Exit images

``` text
logs/exits/YYYY-MM-DD/
```

### Event log

``` text
logs/events.log
```

### Database

``` text
database.db
```

## Database

The SQLite database contains:

### faces

Stores:

-   `face_id`
-   first-seen timestamp
-   face embedding

### events

Stores:

-   event ID
-   face ID
-   event type
-   timestamp
-   cropped image path

The unique visitor count is calculated from registered face IDs, so
recognizing the same person again does not create another unique
visitor.

## Sample Verification

The completed test run produced:

``` text
Unique visitors: 2
Output video: output/tracked_output.mp4
```

The database contained:

``` text
FACE_001
FACE_002
```

The latest successful run also generated an entry and exit event for
`FACE_002`.

## Logging

`logs/events.log` records important events including:

-   system start
-   detection cycles
-   embedding generation
-   face recognition
-   face registration
-   face entry
-   face exit
-   system stop

Example:

``` text
Embedding generated | Track 3
Face recognized | FACE_002 | Similarity 1.000
FACE ENTRY | FACE_002
FACE EXIT | FACE_002
SYSTEM STOPPED
```

## Assumptions

-   The input video contains sufficiently visible faces for detection
    and recognition.
-   Face recognition quality depends on face size, lighting, pose, and
    video quality.
-   The recognition threshold can be adjusted in `config.json`.
-   The current tracker is a lightweight centroid-based tracker intended
    to keep the project simple and CPU-compatible.
-   The system is designed to keep one persistent face ID for
    re-identification using stored embeddings.
-   The current demonstration uses a local video source. RTSP can use
    the same video-source configuration when required.

## Compute Considerations

The implementation supports CPU execution. InsightFace is configured
with `CPUExecutionProvider`.

The YOLO detection interval is configurable so detection can be reduced
when CPU performance is limited.

A GPU-enabled environment can substantially improve inference speed,
especially for longer videos or live camera streams.

## AI Components

### Face Detection

YOLO is used to locate faces and produce bounding boxes.

### Face Recognition

InsightFace with the `buffalo_l` model generates face embeddings.

### Face Matching

Embeddings are normalized and compared using cosine similarity.

### Tracking

A lightweight centroid-based tracker associates detections across
frames.

### Visitor Counting

Each newly registered face receives a unique ID. Therefore,
re-identification of an existing face does not increase the unique
visitor count.

## Demo

Add the final demonstration video link here:

``` text
DEMO VIDEO: <ADD LOOM OR YOUTUBE LINK>
```

## Hackathon Statement

This project is a part of a hackathon run by https://katomaran.com
