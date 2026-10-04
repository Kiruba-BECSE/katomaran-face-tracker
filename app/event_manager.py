import os
import cv2
from datetime import datetime


class EventManager:

    def __init__(
        self,
        database,
        logger,
        entry_folder,
        exit_folder
    ):

        self.database = database

        self.logger = logger

        self.entry_folder = entry_folder

        self.exit_folder = exit_folder

        self.active_faces = {}

    def save_face_image(
        self,
        face_image,
        face_id,
        event_type,
        timestamp
    ):

        date_folder = timestamp.strftime(
            "%Y-%m-%d"
        )

        if event_type == "entry":

            base_folder = self.entry_folder

        else:

            base_folder = self.exit_folder

        folder = os.path.join(
            base_folder,
            date_folder
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        filename = (
            f"{face_id}_"
            f"{timestamp.strftime('%H-%M-%S-%f')}.jpg"
        )

        image_path = os.path.join(
            folder,
            filename
        )

        cv2.imwrite(
            image_path,
            face_image
        )

        return image_path

    def register_entry(
        self,
        face_id,
        face_image
    ):

        if face_id in self.active_faces:

            return

        timestamp = datetime.now()

        image_path = self.save_face_image(
            face_image,
            face_id,
            "entry",
            timestamp
        )

        self.database.add_event(
            face_id,
            "entry",
            timestamp.isoformat(
                timespec="seconds"
            ),
            image_path
        )

        self.active_faces[face_id] = timestamp

        self.logger.info(
            f"FACE ENTRY | "
            f"{face_id} | "
            f"{image_path}"
        )

    def register_exit(
        self,
        face_id,
        face_image
    ):

        if face_id not in self.active_faces:

            return

        timestamp = datetime.now()

        image_path = self.save_face_image(
            face_image,
            face_id,
            "exit",
            timestamp
        )

        self.database.add_event(
            face_id,
            "exit",
            timestamp.isoformat(
                timespec="seconds"
            ),
            image_path
        )

        del self.active_faces[face_id]

        self.logger.info(
            f"FACE EXIT | "
            f"{face_id} | "
            f"{image_path}"
        )