# System Architecture

## High-Level Architecture

``` text
                         ┌─────────────────────┐
                         │    Input Video      │
                         │    sample.mp4       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   YOLO Face         │
                         │   Detection         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Simple Centroid     │
                         │ Tracker              │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ InsightFace         │
                         │ Embedding           │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Face Manager      │
                         │ Match / Register    │
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
               ┌──────────────┐          ┌──────────────┐
               │ Existing     │          │ New Face     │
               │ FACE ID      │          │ FACE ID      │
               └──────┬───────┘          └──────┬───────┘
                      │                         │
                      └────────────┬────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │   Event Manager     │
                         │ Entry / Exit        │
                         └───────┬─────┬───────┘
                                 │     │
                    ┌────────────┘     └─────────────┐
                    ▼                                ▼
           ┌─────────────────┐              ┌─────────────────┐
           │ SQLite Database │              │ Face Crop Images│
           │ faces + events  │              │ entries / exits │
           └─────────────────┘              └─────────────────┘

                         ┌─────────────────────┐
                         │    events.log       │
                         └─────────────────────┘

                         ┌─────────────────────┐
                         │ tracked_output.mp4  │
                         └─────────────────────┘
```

## Module Responsibilities

  Module                 Responsibility
  ---------------------- ----------------------------------------------
  `detector.py`          YOLO face detection
  `recognizer.py`        InsightFace embeddings and similarity
  `tracker.py`           Track association between detections
  `face_manager.py`      Face matching and automatic registration
  `event_manager.py`     Entry/exit event creation and image storage
  `database.py`          SQLite persistence
  `logger.py`            Structured application logging
  `video_processor.py`   End-to-end pipeline
  `main.py`              Application entry point/supporting execution

## Data Flow

``` text
Frame
  ↓
Detection
  ↓
Bounding Boxes
  ↓
Track IDs
  ↓
Face Crop
  ↓
Embedding
  ↓
Similarity Search
  ↓
FACE ID
  ↓
Event
  ├── SQLite
  ├── Cropped Image
  └── events.log
```

## Persistence Design

### `faces`

``` text
face_id      PRIMARY KEY
first_seen
embedding
```

### `events`

``` text
id           PRIMARY KEY
face_id
event_type
timestamp
image_path
```

## Storage Layout

``` text
logs/
├── events.log
├── entries/
│   └── 2026-10-04/
│       └── FACE_002_<time>.jpg
└── exits/
    └── 2026-10-04/
        └── FACE_002_<time>.jpg

output/
└── tracked_output.mp4

database.db
```

## Scalability

The system is modular so individual components can be upgraded
independently.

Possible future upgrades include:

-   stronger multi-object tracking
-   GPU inference
-   RTSP/live camera deployment
-   vector database for large face galleries
-   REST API
-   web dashboard
-   multi-camera support

These are extensions rather than requirements for the current
demonstration.
