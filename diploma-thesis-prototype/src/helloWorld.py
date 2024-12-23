from ultralytics import YOLO
import os

image_path = "../data/people.jpg"
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image not found at {image_path}")

model = YOLO("yolo11n.pt")  # initialize model
results = model(image_path)  # perform inference
results[0].show()  # display results for the first image