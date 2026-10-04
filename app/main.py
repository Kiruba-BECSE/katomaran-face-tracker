from app.database import Database
from app.recognizer import FaceRecognizer
from app.face_manager import FaceManager


DATABASE_PATH = "database.db"


def main():

    print("Starting Katomaran Face Tracker...")

    # Initialize database
    print("\nInitializing database...")

    db = Database(DATABASE_PATH)

    print("Database ready.")

    # Initialize InsightFace
    print("\nInitializing face recognizer...")

    recognizer = FaceRecognizer(
        threshold=0.5
    )

    print("Face recognizer ready.")

    # Initialize face manager
    face_manager = FaceManager(
        db,
        recognizer
    )

    print("\nFace manager ready.")

    # Display registered faces
    faces = db.get_all_faces()

    print(
        "\nRegistered faces:",
        len(faces)
    )

    print("\nSystem is ready.")

    db.close()


if __name__ == "__main__":
    main()