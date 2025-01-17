from decord import VideoReader, cpu
import torch
import numpy as np
from transformers import XCLIPProcessor, XCLIPModel
from PIL import Image

class XCLIPHandler:
    def __init__(self, closed_set_categories=None):
        """
        closed_set_categories: Zoznam kategórií pre uzavretý set. Ak nie je zadaný, použije sa otvorený set.
        """
        # Načítanie modelu a processoru (tokenizer)
        self.model_name = "microsoft/xclip-base-patch16-zero-shot"
        self.processor = XCLIPProcessor.from_pretrained(self.model_name)
        self.model = XCLIPModel.from_pretrained(self.model_name)
        
        # Uzavretý set kategórií, ak je zadaný
        self.closed_set_categories = closed_set_categories

    def sample_frame_indices(self, clip_len, frame_sample_rate, seg_len):
        converted_len = int(clip_len * frame_sample_rate)
        end_idx = np.random.randint(converted_len, seg_len)
        start_idx = end_idx - converted_len
        indices = np.linspace(start_idx, end_idx, num=clip_len)
        indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)
        return indices

    def process_video(self, video_path, clip_len=32, frame_sample_rate=4):
        """
        Spracuje video a vráti dávky snímok vo formáte požadovanom modelom XCLIP.
        """
        np.random.seed(0)
        videoreader = VideoReader(video_path, num_threads=1, ctx=cpu(0))
        videoreader.seek(0)
        seg_len = len(videoreader)
        indices = self.sample_frame_indices(clip_len, frame_sample_rate, seg_len)
        frames = videoreader.get_batch(indices).asnumpy()
        
        # Skontroluj rozmery snímok
        print(f"Original frame shape: {frames.shape}")
        
        return frames


    def extract_descriptions(self):
        """
        Získa popisy pre snímky videa. Môže byť doplnené o detekciu objektov.
        """
        return self.closed_set_categories  # Príklad popisov, mal by byť dynamický

    def classify_batch(self, frames, descriptions):
        """
        Klasifikuje dávku snímok a textových popisov pomocou X-CLIP.
        """
        # Predspracovanie snímok a popisov
        inputs = self.processor(text=descriptions, videos=list(frames), return_tensors="pt", padding=True)

        # Predikcia
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Získanie podobnosti medzi obrázkami a textom
        logits_per_video = outputs.logits_per_video  # Similarity score medzi obrázkami a textom
        probs = logits_per_video.softmax(dim=1)  # Softmax pre pravdepodobnosti

        return probs

    def analyze_video(self, video_path, batch_size=32):
        """
        Analyzuje celé video, rozdelí ho na dávky snímok, vykoná klasifikáciu a vráti výsledky.
        """
        frames = self.process_video(video_path)
        results = []

        # Pre každú dávku snímok vo videu
        descriptions = self.extract_descriptions()
        probs = self.classify_batch(frames, descriptions)
        results.append(probs)

        return results