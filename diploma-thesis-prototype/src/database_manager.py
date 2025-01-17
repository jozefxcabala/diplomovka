import psycopg2
from psycopg2 import sql
import json
import cv2  # Import OpenCV na získanie dĺžky videa
from psycopg2 import pool

class DatabaseManager:
    def __init__(self, db_name, user, password, host='localhost', port='5432'):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection_pool = None
        self.min_connection_pool = 1
        self.max_connection_pool = 20

    def connect(self):
        """Inicializácia connection poolu."""
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            self.min_connection_pool, self.max_connection_pool,  # Min a Max pripojení
            dbname=self.db_name, user=self.user, password=self.password,
            host=self.host, port=self.port
        )

    def get_connection(self):
        """Získa pripojenie z poolu."""
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        """Vráti pripojenie späť do poolu."""
        self.connection_pool.putconn(conn)

    def close(self):
        """Uzavretie všetkých pripojení v poolu."""
        self.connection_pool.closeall()

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
                FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
            );
        """

        create_bounding_boxes_table = """
            CREATE TABLE IF NOT EXISTS bounding_boxes (
              id SERIAL PRIMARY KEY,
              detection_id INTEGER REFERENCES detections(id) ON DELETE CASCADE,
              frame_id INTEGER,
              bbox TEXT,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        conn = self.get_connection()
        cursor = conn.cursor()

        # Vytvorenie tabuliek
        cursor.execute(create_videos_table)
        cursor.execute(create_detections_table)
        cursor.execute(create_bounding_boxes_table)
        conn.commit()

        self.release_connection(conn)

    def clear_tables(self):
        """Vymazanie všetkých záznamov zo všetkých tabuliek."""
        delete_bounding_boxes = "DELETE FROM bounding_boxes;"
        delete_detections = "DELETE FROM detections;"
        delete_videos = "DELETE FROM videos;"


        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(delete_bounding_boxes)
        cursor.execute(delete_detections)
        cursor.execute(delete_videos)
        conn.commit()

        self.release_connection(conn)

    def drop_tables(self):
        """Zmazanie tabuliek."""
        drop_videos_table = "DROP TABLE IF EXISTS videos;"
        drop_detections_table = "DROP TABLE IF EXISTS detections;"
        drop_bounding_boxes_table = "DROP TABLE IF EXISTS bounding_boxes;"
        
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(drop_videos_table)
        cursor.execute(drop_detections_table)
        cursor.execute(drop_bounding_boxes_table)
        conn.commit()

        self.release_connection(conn)

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
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (video_path, duration))
        conn.commit()

        video_id = cursor.fetchone()[0]
        self.release_connection(conn)
        return video_id

    def insert_detection(self, video_id, start_frame, end_frame, class_id, confidence, track_id):
        """Vkladanie detekcie do tabuľky detections."""
        insert_query = sql.SQL("""
            INSERT INTO detections (video_id, start_frame, end_frame, class_id, confidence, track_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """)
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (video_id, start_frame, end_frame, class_id, confidence, track_id))
        conn.commit()

        detection_id = cursor.fetchone()[0]
        self.release_connection(conn)
        return detection_id

    def insert_bounding_box(self, detection_id, frame_id, bbox):
        """Vkladanie bounding boxu do tabuľky bounding_boxes."""
        insert_query = sql.SQL("""
            INSERT INTO bounding_boxes (detection_id, frame_id, bbox)
            VALUES (%s, %s, %s)
        """)
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (detection_id, frame_id, json.dumps(bbox)))
        conn.commit()

        self.release_connection(conn)

    def fetch_detections(self):
        """Extrahovanie všetkých detekcií."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detections;")
        result = cursor.fetchall()
        self.release_connection(conn)
        return result

    def fetch_bounding_boxes(self, detection_id):
        """Extrahovanie bounding boxov pre konkrétnu detekciu."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bounding_boxes WHERE detection_id = %s;", (detection_id,))
        result = cursor.fetchall()
        self.release_connection(conn)
        return result

    def update_detection_end_frame(self, detection_id, new_end_frame):
      """Aktualizuje end_frame pre existujúcu detekciu."""
      # Získame pripojenie a cursor z poolu
      conn = self.get_connection()
      cursor = conn.cursor()

      # Aktualizujeme end_frame
      update_query = "UPDATE detections SET end_frame = %s WHERE id = %s;"
      cursor.execute(update_query, (new_end_frame, detection_id))
      conn.commit()

      # Uvoľníme pripojenie späť do poolu
      self.release_connection(conn)

    def fetch_detection_end_frame(self, detection_id):
      """Získa current end_frame pre detekciu."""
      # Získame pripojenie a cursor z poolu
      conn = self.get_connection()
      cursor = conn.cursor()

      # Získame current end_frame
      query = "SELECT end_frame FROM detections WHERE id = %s;"
      cursor.execute(query, (detection_id,))
      result = cursor.fetchone()

      # Uvoľníme pripojenie späť do poolu
      self.release_connection(conn)

      return result[0] if result else None

