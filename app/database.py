import sqlite3


class Database:

    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = sqlite3.connect(
            database_path,
            check_same_thread=False
        )

        self.create_tables()

    def create_tables(self):

        cursor = self.connection.cursor()

        # Registered faces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faces (
                face_id TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL,
                embedding BLOB NOT NULL
            )
        """)

        # Entry and exit events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                face_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                image_path TEXT
            )
        """)

        self.connection.commit()

    def add_face(self, face_id, timestamp, embedding):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO faces (
                face_id,
                first_seen,
                embedding
            )
            VALUES (?, ?, ?)
            """,
            (
                face_id,
                timestamp,
                embedding.tobytes()
            )
        )

        self.connection.commit()

    def get_all_faces(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT face_id, first_seen, embedding
            FROM faces
            """
        )

        rows = cursor.fetchall()

        faces = []

        for row in rows:

            face_id = row[0]
            first_seen = row[1]
            embedding = row[2]

            faces.append({
                "face_id": face_id,
                "first_seen": first_seen,
                "embedding": embedding
            })

        return faces

    def add_event(
        self,
        face_id,
        event_type,
        timestamp,
        image_path
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO events (
                face_id,
                event_type,
                timestamp,
                image_path
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                face_id,
                event_type,
                timestamp,
                image_path
            )
        )

        self.connection.commit()

    def get_unique_visitor_count(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM faces"
        )

        return cursor.fetchone()[0]

    def close(self):

        self.connection.close()