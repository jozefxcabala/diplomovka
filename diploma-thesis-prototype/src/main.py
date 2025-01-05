from video_processor import process_video
from yolo_handler import YOLOHandler

def main():
    video_path = "../data/input/street.mp4"
    output_path = "../data/output/clips/street_output.mp4"
    model_path = "../data/models/yolo11n.pt"

    # Triedy na detekciu (len 'person', ktorá zodpovedá triede [0])
    # https://gist.githubusercontent.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8/raw/43a947ccbfbcba2b404e36bb7aee7332b5fd0c89/yolo_classes.json
    classes_to_detect = [0]  # YOLO trieda pre 'person'

    yolo = YOLOHandler(model_path, classes_to_detect=classes_to_detect)

    try:
        process_video(video_path, output_path, yolo)
    except KeyboardInterrupt:
        print("\nDetekcia bola manuálne prerušená. Ukončujem program.")
    except Exception as e:
        print(f"Vyskytla sa neočakávaná chyba: {e}")
    finally:
        print("Program ukončený.")

if __name__ == "__main__":
    main()
