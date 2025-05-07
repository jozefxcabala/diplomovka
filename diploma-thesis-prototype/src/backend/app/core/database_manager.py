import psycopg2
from psycopg2 import sql
import json
import cv2
from psycopg2 import pool

# This class, `DatabaseManager`, provides an interface for interacting with a PostgreSQL database to store and manage video processing data.
# It includes methods for:
# - Connecting to the database using a connection pool to manage multiple connections efficiently.
# - Creating, clearing, and dropping tables for storing video metadata, detections, and bounding boxes.
# - Inserting new video, detection, and bounding box records into the database.
# - Fetching detections and bounding boxes from the database, filtered by video ID or detection ID.
# - Updating detection data such as the end frame for a detection.
# The connection pool is initialized with minimum and maximum pool sizes, ensuring efficient database access without overloading the server with too many concurrent connections.
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
        """Initialize the connection pool and create database if it doesn't exist."""
        try:
            # Step 1: Connect to default 'postgres' DB to check existence
            sys_conn = psycopg2.connect(
                dbname="postgres",
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            sys_conn.autocommit = True
            sys_cursor = sys_conn.cursor()

            # Step 2: Check if target database exists
            sys_cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (self.db_name,))
            exists = sys_cursor.fetchone()

            # Step 3: Create the database if it doesn't exist
            if not exists:
                print(f"Database '{self.db_name}' not found. Creating it...")
                sys_cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))

            sys_cursor.close()
            sys_conn.close()

            # Step 4: Connect to the actual DB with pooling
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.min_connection_pool, self.max_connection_pool,
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print(f"Connected to database '{self.db_name}' successfully.")

        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise

    def get_connection(self):
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        self.connection_pool.putconn(conn)

    def close(self):
        self.connection_pool.closeall()

    def create_tables(self):
        create_videos_table = """
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                video_path TEXT NOT NULL,
                duration INTEGER,
                fps FLOAT,
                date_processed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name_of_analysis TEXT DEFAULT 'Unnamed analysis'
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
                video_object_detection_path TEXT NULL,
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

        create_anomaly_recognition_data_table = """
            CREATE TABLE IF NOT EXISTS anomaly_recognition_data (
              video_id INTEGER,
              detection_id INTEGER,
              logits_per_video BYTEA DEFAULT NULL,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
              FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE CASCADE
            );
        """

        create_analysis_configurations_table = """
            CREATE TABLE IF NOT EXISTS analysis_configurations (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                categories TEXT[] NOT NULL,
                settings JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        create_analysis_configurations_link_table = """
            CREATE TABLE IF NOT EXISTS analysis_configurations_link (
                video_id INTEGER PRIMARY KEY,
                config_id INTEGER,
                FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
                FOREIGN KEY (config_id) REFERENCES analysis_configurations(id) ON DELETE SET NULL
            );
        """

        create_detection_anomalies_table = """
            CREATE TABLE IF NOT EXISTS detection_anomalies (
                id SERIAL PRIMARY KEY,
                detection_id INTEGER REFERENCES detections(id) ON DELETE CASCADE,
                anomaly_label TEXT NOT NULL,
                anomaly_score FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(create_videos_table)
        cursor.execute(create_detections_table)
        cursor.execute(create_bounding_boxes_table)
        cursor.execute(create_anomaly_recognition_data_table)
        cursor.execute(create_analysis_configurations_table)
        cursor.execute(create_analysis_configurations_link_table)
        cursor.execute(create_detection_anomalies_table)

        conn.commit()

        self.release_connection(conn)

    def clear_tables(self):
        delete_bounding_boxes = "DELETE FROM bounding_boxes;"
        delete_detections = "DELETE FROM detections;"
        delete_videos = "DELETE FROM videos;"
        delete_anomaly_recognition_data = "DELETE FROM anomaly_recognition_data;"
        delete_analysis_configurations_data = "DELETE FROM analysis_configurations;"
        delete_analysis_configurations_link_data = "DELETE FROM analysis_configurations_link;"
        delete_detection_anomalies = "DELETE FROM detection_anomalies;"


        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(delete_detection_anomalies)
        cursor.execute(delete_analysis_configurations_link_data)
        cursor.execute(delete_analysis_configurations_data)
        cursor.execute(delete_anomaly_recognition_data)
        cursor.execute(delete_bounding_boxes)
        cursor.execute(delete_detections)
        cursor.execute(delete_videos)
        conn.commit()

        self.release_connection(conn)

    def drop_tables(self):
        drop_videos_table = "DROP TABLE IF EXISTS videos;"
        drop_detections_table = "DROP TABLE IF EXISTS detections;"
        drop_bounding_boxes_table = "DROP TABLE IF EXISTS bounding_boxes;"
        drop_anomaly_recognition_data_table = "DROP TABLE IF EXISTS anomaly_recognition_data;"
        drop_analysis_configurations_link_table = "DROP TABLE IF EXISTS analysis_configurations_link;"
        drop_analysis_configurations_table = "DROP TABLE IF EXISTS analysis_configurations;"
        drop_detection_anomalies_table = "DROP TABLE IF EXISTS detection_anomalies;"

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(drop_detection_anomalies_table)
        cursor.execute(drop_analysis_configurations_link_table)
        cursor.execute(drop_analysis_configurations_table)
        cursor.execute(drop_anomaly_recognition_data_table)
        cursor.execute(drop_bounding_boxes_table)
        cursor.execute(drop_detections_table)
        cursor.execute(drop_videos_table)
        conn.commit()

        self.release_connection(conn)

    def get_video_duration(self, video_path):
        """Získanie dĺžky videa v sekundách pomocou OpenCV."""
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise Exception("Error opening video file")
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        return duration, fps

    def insert_video(self, video_path, name_of_analysis):
        duration, fps = self.get_video_duration(video_path)
        insert_query = """
                INSERT INTO videos (video_path, duration, fps, name_of_analysis)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (video_path, duration, fps, name_of_analysis))
        conn.commit()

        video_id = cursor.fetchone()[0]
        self.release_connection(conn)
        return video_id

    def insert_detection(self, video_id, start_frame, end_frame, class_id, confidence, track_id, video_type="mp4"):
        insert_query = """
            INSERT INTO detections (video_id, start_frame, end_frame, class_id, confidence, track_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(insert_query, (video_id, start_frame, end_frame, class_id, confidence, track_id))
        conn.commit()
        
        detection_id = cursor.fetchone()[0]
        
        video_object_detection_path = f"data/output/{video_id}/anomaly_recognition_preprocessor/{video_id}_{detection_id}.{video_type}"

        update_query = """
            UPDATE detections
            SET video_object_detection_path = %s
            WHERE id = %s
        """
        
        cursor.execute(update_query, (video_object_detection_path, detection_id))
        conn.commit()

        self.release_connection(conn)
        
        return detection_id

    def insert_bounding_box(self, detection_id, frame_id, bbox):
        insert_query = """
            INSERT INTO bounding_boxes (detection_id, frame_id, bbox)
            VALUES (%s, %s, %s)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (detection_id, frame_id, json.dumps(bbox)))
        conn.commit()

        self.release_connection(conn)

    def fetch_detections(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detections;")
        result = cursor.fetchall()
        self.release_connection(conn)
        return result

    def update_detection_end_frame(self, detection_id, new_end_frame):
      conn = self.get_connection()
      cursor = conn.cursor()

      update_query = "UPDATE detections SET end_frame = %s WHERE id = %s;"
      cursor.execute(update_query, (new_end_frame, detection_id))
      conn.commit()

      self.release_connection(conn)

    def fetch_detection_end_frame(self, detection_id):
      conn = self.get_connection()
      cursor = conn.cursor()

      query = "SELECT end_frame FROM detections WHERE id = %s;"
      cursor.execute(query, (detection_id,))
      result = cursor.fetchone()

      self.release_connection(conn)

      return result[0] if result else None

    def fetch_detection_by_id(self, detection_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, video_id, start_frame, end_frame, class_id, confidence, track_id, video_object_detection_path
            FROM detections WHERE id = %s;
        """
        cursor.execute(query, (detection_id,))
        result = cursor.fetchone()
        self.release_connection(conn)

        if result:
            return {
                'id': result[0],
                'video_id': result[1],
                'start_frame': result[2],
                'end_frame': result[3],
                'class_id': result[4],
                'confidence': result[5],
                'track_id': result[6],
                'video_object_detection_path': result[7]
            }
        else:
            return None

    def fetch_bounding_boxes_by_detection_id(self, detection_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, detection_id, frame_id, bbox FROM bounding_boxes WHERE detection_id = %s;
        """
        cursor.execute(query, (detection_id,))
        result = cursor.fetchall()
        self.release_connection(conn)

        bounding_boxes = []
        for row in result:
            bounding_boxes.append({
                'id': row[0],
                'detection_id': row[1],
                'frame_id': row[2],
                'bbox': json.loads(row[3])
            })

        return bounding_boxes
    
    def fetch_detections_by_video_id(self, video_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, video_id, start_frame, end_frame, class_id, confidence, track_id, video_object_detection_path
            FROM detections WHERE video_id = %s;
        """
        cursor.execute(query, (video_id,))
        result = cursor.fetchall()

        detections = []
        for row in result:
            detection_id = row[0]

            cursor.execute("""
                SELECT anomaly_label, anomaly_score
                FROM detection_anomalies
                WHERE detection_id = %s
                ORDER BY anomaly_score DESC;
            """, (detection_id,))
            anomaly_rows = cursor.fetchall()
            anomalies = [{"label": a[0], "score": a[1]} for a in anomaly_rows]

            detections.append({
                'id': detection_id,
                'video_id': row[1],
                'start_frame': row[2],
                'end_frame': row[3],
                'class_id': row[4],
                'confidence': row[5],
                'track_id': row[6],
                'video_object_detection_path': row[7],
                'anomalies': anomalies 
            })

        self.release_connection(conn)
        return detections

    def fetch_detections_by_video_id_and_duration(self, video_id, duration):
        """Získa všetky detekcie pre dané video_id."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, video_id, start_frame, end_frame, class_id, confidence, track_id, video_object_detection_path
            FROM detections WHERE video_id = %s AND (end_frame - start_frame) > %s;
        """
        cursor.execute(query, (video_id, duration,))
        result = cursor.fetchall()
        self.release_connection(conn)

        detections = []
        for row in result:
            detections.append({
                'id': row[0],
                'video_id': row[1],
                'start_frame': row[2],
                'end_frame': row[3],
                'class_id': row[4],
                'confidence': row[5],
                'track_id': row[6],
                'video_object_detection_path': row[7]
            })

        return detections
    
    def insert_anomaly_recognition_data(self, video_id, detection_id, logits_per_video):
        query = """
            INSERT INTO anomaly_recognition_data (video_id, detection_id, logits_per_video)
            VALUES (%s, %s, %s);
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, (video_id, detection_id, logits_per_video))
        conn.commit()

        self.release_connection(conn)

    def get_anomaly_recognition_data_by_video_id(self, video_id):
        query = """
            SELECT logits_per_video, detection_id
            FROM anomaly_recognition_data
            WHERE video_id = %s;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query, (video_id,))
        result = cursor.fetchall()

        self.release_connection(conn)

        anomaly_recognition_data = []
        for row in result:
            anomaly_recognition_data.append({
                'detection_id': row[1],
                'logits_per_video': row[0]
            })

        return anomaly_recognition_data

    def fetch_anomalies_by_video_id(self, video_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                d.id, d.video_id, d.start_frame, d.end_frame,
                da.anomaly_label, da.anomaly_score
            FROM detections d
            JOIN detection_anomalies da ON d.id = da.detection_id
            WHERE d.video_id = %s AND da.anomaly_score = (
                SELECT MAX(sub.anomaly_score)
                FROM detection_anomalies sub
                WHERE sub.detection_id = d.id
            )
            ORDER BY d.id;
        """

        cursor.execute(query, (video_id,))
        rows = cursor.fetchall()
        self.release_connection(conn)

        anomalies = []
        for row in rows:
            anomalies.append({
                'id': row[0],
                'video_id': row[1],
                'start_frame': row[2],
                'end_frame': row[3],
                'top_anomaly_label': row[4],
                'top_anomaly_score': row[5],
            })

        return anomalies
    
    def fetch_video_path(self, video_id: int) -> str:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT video_path FROM videos WHERE id = %s", (video_id,))
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else None
    
    def fetch_video_by_id(self, video_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, video_path, duration, fps, date_processed, name_of_analysis
            FROM videos
            WHERE id = %s;
        """
        cursor.execute(query, (video_id,))
        result = cursor.fetchone()

        self.release_connection(conn)

        if result:
            return {
                'id': result[0],
                'video_path': result[1],
                'duration': result[2],
                'fps': result[3],
                'date_processed': result[4],
                'name_of_analysis': result[5],
            }
        return None

    def insert_analysis_configuration(self, name: str, categories: list[str], settings: dict) -> int:
        query = """
            INSERT INTO analysis_configurations (name, categories, settings)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query, (name, categories, json.dumps(settings)))
        config_id = cursor.fetchone()[0]
        conn.commit()
        self.release_connection(conn)
        
        return config_id
    
    def fetch_videos(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT v.id, v.video_path, v.duration, v.fps, v.date_processed, v.name_of_analysis,
                acl.config_id
            FROM videos v
            LEFT JOIN analysis_configurations_link acl ON v.id = acl.video_id;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        videos = []
        for row in results:
            video_data = {
                'id': row[0],
                'video_path': row[1],
                'duration': row[2],
                'fps': row[3],
                'date_processed': row[4],
                'name_of_analysis': row[5],
            }

            config_id = row[6]
            if config_id is not None:
                config = self.fetch_analysis_configuration_by_id(config_id)
                video_data['config'] = config
            else:
                video_data['config'] = None

            videos.append(video_data)

        self.release_connection(conn)
        return videos if videos else None

    def fetch_all_analysis_configurations(self):
        query = """
            SELECT id, name, categories, settings, created_at
            FROM analysis_configurations
            ORDER BY created_at DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query)
        configs = cursor.fetchall()
        self.release_connection(conn)

        return [
            {
                "id": row[0],
                "name": row[1],
                "categories": row[2],
                "settings": row[3],
                "created_at": row[4]
            }
            for row in configs
        ]

    def fetch_analysis_configuration_by_id(self, config_id: int):
        query = """
            SELECT id, name, categories, settings, created_at
            FROM analysis_configurations
            WHERE id = %s;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query, (config_id,))
        row = cursor.fetchone()
        self.release_connection(conn)

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "categories": row[2],
                "settings": row[3],
                "created_at": row[4]
            }
        return None
    
    def delete_analysis_configuration_by_id(self, config_id: int):
        """Deletes an analysis configuration by ID and returns the deleted row."""
        query = """
            DELETE FROM analysis_configurations
            WHERE id = %s
            RETURNING id, name, categories, settings, created_at;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query, (config_id,))
        deleted = cursor.fetchone()
        conn.commit()
        self.release_connection(conn)

        if deleted:
            return {
                "id": deleted[0],
                "name": deleted[1],
                "categories": deleted[2],
                "settings": deleted[3],
                "created_at": deleted[4]
            }
        return None

    def update_analysis_configuration(self, config_id: int, name: str, categories: list[str], settings: dict) -> bool:
        query = """
            UPDATE analysis_configurations
            SET name = %s, categories = %s, settings = %s
            WHERE id = %s
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name, categories, json.dumps(settings), config_id))
        conn.commit()
        updated = cursor.rowcount > 0
        self.release_connection(conn)
        return updated
    
    def delete_video_by_id(self, video_id: int) -> bool:
        """Deletes a video and cascades to related detections, boxes, and anomaly data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = %s;", (video_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        self.release_connection(conn)
        return deleted
    
    def link_analysis_with_config(self, video_id: int, config_id: int):
        query = """
            INSERT INTO analysis_configurations_link (video_id, config_id)
            VALUES (%s, %s)
            RETURNING video_id, config_id;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query, (video_id, config_id))
        conn.commit()
        result = cursor.fetchone()
        self.release_connection(conn)

        return {
            "video_id": result[0],
            "config_id": result[1]
        }
    
    def insert_detection_anomalies(self, detection_id: int, anomalies: list[dict]):
        query = """
            INSERT INTO detection_anomalies (detection_id, anomaly_label, anomaly_score)
            VALUES (%s, %s, %s)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        for anomaly in anomalies:
            cursor.execute(query, (detection_id, anomaly["label"], anomaly["score"]))
        
        conn.commit()
        self.release_connection(conn)

    def fetch_detection_anomalies(self, detection_id: int) -> list[dict]:
        query = """
            SELECT anomaly_label, anomaly_score
            FROM detection_anomalies
            WHERE detection_id = %s
            ORDER BY anomaly_score DESC;
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query, (detection_id,))
        rows = cursor.fetchall()
        self.release_connection(conn)

        return [{"label": row[0], "score": row[1]} for row in rows]
    
    def fetch_all_anomalies_by_video_id(self, video_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                d.id, d.video_id, d.start_frame, d.end_frame,
                da.anomaly_label, da.anomaly_score
            FROM detections d
            JOIN detection_anomalies da ON d.id = da.detection_id
            WHERE d.video_id = %s
            ORDER BY d.id, da.anomaly_score DESC;
        """

        cursor.execute(query, (video_id,))
        rows = cursor.fetchall()
        self.release_connection(conn)

        detection_map = {}
        for row in rows:
            detection_id = row[0]
            if detection_id not in detection_map:
                detection_map[detection_id] = {
                    'id': detection_id,
                    'video_id': row[1],
                    'start_frame': row[2],
                    'end_frame': row[3],
                    'anomalies': []
                }

            detection_map[detection_id]['anomalies'].append({
                'label': row[4],
                'score': row[5]
            })

        return list(detection_map.values())