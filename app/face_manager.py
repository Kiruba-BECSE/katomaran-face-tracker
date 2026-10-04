import numpy as np
from datetime import datetime


class FaceManager:

    def __init__(self, database, recognizer):

        self.database = database
        self.recognizer = recognizer

    def find_match(self, embedding):

        faces = self.database.get_all_faces()

        best_face_id = None
        best_similarity = -1.0

        for face in faces:

            stored_embedding = np.frombuffer(
                face["embedding"],
                dtype=np.float32
            )

            similarity = self.recognizer.compare(
                embedding,
                stored_embedding
            )

            if similarity > best_similarity:

                best_similarity = similarity
                best_face_id = face["face_id"]

        if (
            best_face_id is not None
            and best_similarity >= self.recognizer.threshold
        ):

            return {
                "face_id": best_face_id,
                "similarity": best_similarity
            }

        return None

    def register_face(self, embedding):

        faces = self.database.get_all_faces()

        face_number = len(faces) + 1

        face_id = f"FACE_{face_number:03d}"

        timestamp = datetime.now().isoformat(
            timespec="seconds"
        )

        self.database.add_face(
            face_id,
            timestamp,
            embedding
        )

        return face_id

    def recognize_or_register(self, embedding):

        match = self.find_match(embedding)

        if match is not None:

            return {
                "face_id": match["face_id"],
                "new_face": False,
                "similarity": match["similarity"]
            }

        face_id = self.register_face(embedding)

        return {
            "face_id": face_id,
            "new_face": True,
            "similarity": None
        }