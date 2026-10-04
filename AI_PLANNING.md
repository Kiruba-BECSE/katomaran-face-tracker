# AI Planning

## 1. Problem

Build an intelligent face tracker that can detect people, automatically
register previously unknown faces, recognize returning visitors, track
them continuously, and maintain reliable entry/exit records.

## 2. AI Pipeline

``` text
Video
  ↓
YOLO Face Detection
  ↓
Face Bounding Box
  ↓
Tracking
  ↓
InsightFace Embedding
  ↓
Embedding Comparison
  ↓
Existing Face / New Face
  ↓
Unique Face ID
  ↓
Entry / Tracking / Exit
  ↓
Image + SQLite + Event Log
```

## 3. Face Detection

YOLO is used as the first AI stage.

The detector produces:

-   bounding box coordinates
-   detection confidence

The detection interval is configurable through `config.json`.

## 4. Face Recognition

InsightFace is used instead of the prohibited `face_recognition`
package.

For each face requiring recognition:

1.  A face crop is extracted.
2.  InsightFace generates an embedding.
3.  The embedding is normalized.
4.  The embedding is compared against registered embeddings.
5.  The highest similarity is selected.
6.  The configured recognition threshold determines whether it is
    treated as the same person.

## 5. Automatic Registration

If no stored embedding passes the recognition threshold:

``` text
New Face
   ↓
Generate unique ID
   ↓
FACE_001 / FACE_002 / ...
   ↓
Store embedding in SQLite
```

This allows the system to operate without a manual registration screen.

## 6. Tracking Strategy

A lightweight centroid tracker is used.

For every detection:

1.  Calculate the center of the bounding box.
2.  Compare it with existing track centers.
3.  Associate the closest suitable track.
4.  Create a new track when no suitable track exists.
5.  Keep temporarily missing tracks for the configured number of frames.

This keeps the implementation simple and reduces computational overhead.

## 7. Event Strategy

A face can have an active state.

### Entry

An entry is created when a recognized/registered face becomes active and
does not already have an active entry.

### Exit

An exit is created when the active visit ends during processing.

The event manager prevents duplicate entries for the same active face.

## 8. Unique Visitor Counting

The unique count is based on the number of registered face IDs.

Example:

``` text
FACE_001 enters
FACE_001 exits
FACE_001 returns

Unique visitors = 1
```

A returning visitor does not create another face record.

## 9. Data Storage

### Face metadata

Stored in SQLite:

``` text
face_id
first_seen
embedding
```

### Event metadata

Stored in SQLite:

``` text
face_id
event_type
timestamp
image_path
```

### Images

Stored by event type and date:

``` text
logs/
├── entries/
│   └── YYYY-MM-DD/
└── exits/
    └── YYYY-MM-DD/
```

### System logs

Critical events are written to:

``` text
logs/events.log
```

## 10. Reliability

The system separates responsibilities into modules:

-   `detector.py` --- detection
-   `recognizer.py` --- embedding and similarity
-   `tracker.py` --- tracking
-   `face_manager.py` --- registration and recognition
-   `event_manager.py` --- entry/exit events
-   `database.py` --- persistence
-   `logger.py` --- event logging
-   `video_processor.py` --- pipeline orchestration

This makes individual components easier to test and replace.

## 11. Configurability

The following values are intentionally externalized:

-   input source
-   YOLO model
-   detection skip interval
-   detection confidence
-   recognition threshold
-   maximum missing tracking frames
-   output video path
-   image log folders
-   event log path

## 12. Expected Result

For every visitor:

``` text
Detect
→ Track
→ Recognize/Register
→ Assign FACE ID
→ Record Entry
→ Continue Tracking
→ Record Exit
```

For returning visitors:

``` text
Detect
→ Track
→ Match Stored Embedding
→ Reuse Existing FACE ID
```

The design therefore supports automatic registration, recognition,
tracking, visitor counting, and structured event recording without
requiring a manual registration workflow.
