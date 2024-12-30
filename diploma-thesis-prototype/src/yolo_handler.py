from ultralytics import YOLO

class YOLOHandler:
    def __init__(self, model_path: str, classes_to_detect=None, verbose=False):
        """
        Inicializuje YOLO model a nastaví triedy na detekciu.
        
        :param model_path: Cesta k modelu YOLO.
        :param classes_to_detect: Zoznam tried, ktoré chcete detekovať (napr. ['person']).
        """
        self.classes_to_detect = classes_to_detect if classes_to_detect is not None else []
        self.verbose = verbose
        self.model = YOLO(model_path)

    def detect(self, frame, confidence_threshold=0.5):
        """
        Detekuje objekty na zadanom frame.
        
        :param frame: Obrazový rámec na analýzu.
        :param confidence_threshold: Prahová hodnota pre pravdepodobnosť detekcie.
        :return: Výsledky detekcie pre vybrané triedy.
        """
        results = self.model(frame, classes=self.classes_to_detect, verbose=self.verbose)
        filtered_results = []

        for result in results[0].boxes:
            class_id = int(result.cls[0])  # Trieda detekcie
            confidence = float(result.conf[0])  # Pravdepodobnosť detekcie

            # Filtrujeme detekcie podľa vybraných tried a prahovej hodnoty
            if confidence >= confidence_threshold:
                filtered_results.append({
                    'class_id': class_id,
                    'confidence': confidence,
                    'bbox': result.xyxy[0].tolist()  # Bounding box súradnice
                })

        return filtered_results
