# This script connects to a PostgreSQL database to count object detections per scene at various confidence thresholds.
# 
# Functionality:
# - Connects to the 'diploma_thesis_prototype_db' PostgreSQL database using psycopg2.
# - Iterates through a list of confidence thresholds.
# - For each threshold, retrieves the number of detections per video (joined with the video table).
# - Uses a regular expression to group detections by scene (e.g., "Scene1", "Scene2").
# - Aggregates the detection counts per scene for each threshold.
# - Prints the detection counts for each scene and threshold in a readable format.
#
# Useful for evaluating detection density and filtering effectiveness across different confidence levels.

import psycopg2
import re
from collections import defaultdict

DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'diploma_thesis_prototype_db',
    'user': 'postgres',
    'password': 'postgres',
}

conn = psycopg2.connect(**DB_CONFIG)

cur = conn.cursor()

confidence_thresholds = [0.3, 0.45, 0.6, 0.75]
results = {}

for thresh in confidence_thresholds:
    cur.execute("""
        SELECT v.id, v.video_path, COUNT(d.id)
        FROM videos v
        JOIN detections d ON d.video_id = v.id
        WHERE d.confidence >= %s AND v.video_path ~ 'Scene\\d+'
        GROUP BY v.id, v.video_path
    """, (thresh,))

    scene_counts = defaultdict(int)

    for video_id, path, count in cur.fetchall():
        match = re.search(r"Scene(\d+)", path)
        if match:
            scene = f"Scene{match.group(1)}"
            scene_counts[scene] += count

    results[thresh] = dict(scene_counts)

cur.close()
conn.close()

for thresh in confidence_thresholds:
    print(f"\nConfidence threshold: {thresh}")
    for scene in sorted(results[thresh].keys(), key=lambda x: int(x.replace("Scene", ""))):
        print(f"{scene}: {results[thresh][scene]} detekcií")