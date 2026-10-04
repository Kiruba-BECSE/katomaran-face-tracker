import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognizer:

    def __init__(self, threshold=0.5):

        self.threshold = threshold

        print("Loading InsightFace model...")

        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

        print("InsightFace model loaded successfully.")

    def get_embedding(self, face_image):

        faces = self.app.get(face_image)

        if not faces:
            return None

        # Select the largest detected face
        face = max(
            faces,
            key=lambda f: (
                f.bbox[2] - f.bbox[0]
            ) * (
                f.bbox[3] - f.bbox[1]
            )
        )

        embedding = face.embedding

        # Normalize embedding
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.astype(np.float32)

    def compare(self, embedding1, embedding2):

        similarity = np.dot(
            embedding1,
            embedding2
        )

        return float(similarity)

    def is_match(self, embedding1, embedding2):

        similarity = self.compare(
            embedding1,
            embedding2
        )

        return similarity >= self.threshold