import cv2

from app.database import Database
from app.recognizer import FaceRecognizer
from app.face_manager import FaceManager


DATABASE_PATH = "database.db"


def main():

    print("Starting face recognition test...")

    # Open database
    db = Database(DATABASE_PATH)

    # Load InsightFace
    recognizer = FaceRecognizer(
        threshold=0.5
    )

    # Create face manager
    face_manager = FaceManager(
        db,
        recognizer
    )

    # Load test image
    image_path = "input/test.jpg"

    print("\nLoading image:", image_path)

    image = cv2.imread(image_path)

    if image is None:

        print("ERROR: Could not load image.")
        print("Make sure input/test.jpg exists.")

        db.close()
        return

    print("Image loaded successfully.")

    # Generate face embedding
    print("\nDetecting face...")

    embedding = recognizer.get_embedding(image)

    if embedding is None:

        print("No face detected in the image.")

        db.close()
        return

    print("Face embedding generated.")
    print("Embedding size:", len(embedding))

    # Recognize or register
    result = face_manager.recognize_or_register(
        embedding
    )

    print("\nRecognition result:")

    print("Face ID:", result["face_id"])
    print("New face:", result["new_face"])
    print("Similarity:", result["similarity"])

    # Show database count
    faces = db.get_all_faces()

    print("\nTotal registered faces:", len(faces))

    db.close()

    print("\nFace recognition test completed.")


if __name__ == "__main__":
    main()