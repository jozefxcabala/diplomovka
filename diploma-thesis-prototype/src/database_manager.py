import psycopg2
from psycopg2 import sql
import json
import cv2  # Import OpenCV na získanie dĺžky videa

class DatabaseManager:
    def __init__(self, db_name, user, password, host='localhost', port='5432'):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Pripojenie k databáze."""
        self.connection = psycopg2.connect(
            dbname=self.db_name, user=self.user, password=self.password,
            host=self.host, port=self.port
        )
        self.cursor = self.connection.cursor()

    def close(self):
        """Uzavretie pripojenia k databáze."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_tables(self):
        """Vytvorenie tabuliek (ak neexistujú)."""
        
        create_videos_table = """
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                video_path TEXT NOT NULL,
                duration INTEGER,
                date_processed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        create_detections_table = """
            CREATE TABLE IF NOT EXISTS detections (
                id SERIAL PRIMARY KEY,
                video_id INTEGER,
                start_frame INTEGER,
                end_frame INTEGER,
                class_id INTEGER,
                confidence FLOAT,
                track_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            );
        """

        create_bounding_boxes_table = """
            CREATE TABLE IF NOT EXISTS bounding_boxes (
                id SERIAL PRIMARY KEY,
                detection_id INTEGER REFERENCES detections(id),
                frame_id INTEGER,
                bbox TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        
        # Vytvorenie tabuliek
        self.cursor.execute(create_videos_table)
        self.cursor.execute(create_detections_table)
        self.cursor.execute(create_bounding_boxes_table)
        self.connection.commit()

    def clear_tables(self):
        """Vymazanie všetkých záznamov zo všetkých tabuliek."""
        delete_videos = "DELETE FROM videos;"
        delete_detections = "DELETE FROM detections;"
        delete_bounding_boxes = "DELETE FROM bounding_boxes;"

        self.cursor.execute(delete_videos)
        self.cursor.execute(delete_detections)
        self.cursor.execute(delete_bounding_boxes)
        self.connection.commit()

    def drop_tables(self):
        """Zmazanie tabuliek."""
        drop_videos_table = "DROP TABLE IF EXISTS videos;"
        drop_detections_table = "DROP TABLE IF EXISTS detections;"
        drop_bounding_boxes_table = "DROP TABLE IF EXISTS bounding_boxes;"
        
        self.cursor.execute(drop_videos_table)
        self.cursor.execute(drop_detections_table)
        self.cursor.execute(drop_bounding_boxes_table)
        self.connection.commit()

    def get_video_duration(self, video_path):
        """Získanie dĺžky videa v sekundách pomocou OpenCV."""
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise Exception("Error opening video file")
        duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
        return duration

    def insert_video(self, video_path):
        """Vkladanie metadát o videu do tabuľky videos."""
        duration = self.get_video_duration(video_path)
        insert_query = sql.SQL("""
            INSERT INTO videos (video_path, duration)
            VALUES (%s, %s) RETURNING id
        """)
        self.cursor.execute(insert_query, (video_path, duration))
        self.connection.commit()
        return self.cursor.fetchone()[0]  # Vráti ID nového videa

    def insert_detection(self, video_id, start_frame, end_frame, class_id, confidence, track_id):
        """Vkladanie detekcie do tabuľky detections."""
        insert_query = sql.SQL("""
            INSERT INTO detections (video_id, start_frame, end_frame, class_id, confidence, track_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """)
        self.cursor.execute(insert_query, (video_id, start_frame, end_frame, class_id, confidence, track_id))
        self.connection.commit()
        return self.cursor.fetchone()[0]  # Vráti ID novej detekcie

    def insert_bounding_box(self, detection_id, frame_id, bbox):
        """Vkladanie bounding boxu do tabuľky bounding_boxes."""
        insert_query = sql.SQL("""
            INSERT INTO bounding_boxes (detection_id, frame_id, bbox)
            VALUES (%s, %s, %s)
        """)
        self.cursor.execute(insert_query, (detection_id, frame_id, json.dumps(bbox)))
        self.connection.commit()

    def fetch_detections(self):
        """Extrahovanie všetkých detekcií."""
        self.cursor.execute("SELECT * FROM detections;")
        return self.cursor.fetchall()

    def fetch_bounding_boxes(self, detection_id):
        """Extrahovanie bounding boxov pre konkrétnu detekciu."""
        self.cursor.execute("SELECT * FROM bounding_boxes WHERE detection_id = %s;", (detection_id,))
        return self.cursor.fetchall()

    def fetch_video_by_id(self, video_id):
        """Extrahovanie videa podľa ID."""
        self.cursor.execute("SELECT * FROM videos WHERE id = %s;", (video_id,))
        return self.cursor.fetchone()
