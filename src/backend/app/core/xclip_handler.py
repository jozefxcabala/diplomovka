from decord import VideoReader, cpu
import torch
import numpy as np
from transformers import XCLIPProcessor, XCLIPModel
from PIL import Image

# This class, `XCLIPHandler`, is designed to handle video processing and zero-shot classification using the XCLIP model.
# It includes methods for:
# - Initializing the XCLIP model and processor with a pre-trained version.
# - Sampling a set of frame indices from the video based on clip length and frame sample rate.
# - Processing the video by extracting frames and preparing them for input into the XCLIP model.
# - Extracting descriptions (categories) to be used in the classification process.
# - Classifying a batch of frames along with descriptions using the XCLIP model, and calculating the similarity between images and text.
# - Analyzing the entire video by splitting it into batches of frames, performing classification, and returning the results.
# The class uses a pre-trained XCLIP model to analyze videos and classify them based on textual descriptions in a zero-shot manner.
class XCLIPHandler:
    def __init__(self, list_of_categories=None):
        self.model_name = "microsoft/xclip-base-patch16-zero-shot"
        self.processor = XCLIPProcessor.from_pretrained(self.model_name)
        self.model = XCLIPModel.from_pretrained(self.model_name)
        
        self.list_of_categories = list_of_categories

    def sample_frame_indices(self, clip_len, frame_sample_rate, seg_len):
        converted_len = int(clip_len * frame_sample_rate)
        if converted_len >= seg_len:
            start_idx = 0
            end_idx = seg_len
            indices = np.linspace(start_idx, end_idx - 1, num=min(clip_len, seg_len)).astype(np.int64)
        else:
            end_idx = np.random.randint(converted_len, seg_len)
            start_idx = end_idx - converted_len
            indices = np.linspace(start_idx, end_idx, num=clip_len)
            indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)

        return indices

    def process_video(self, video_path, clip_len=32, frame_sample_rate=4):
        """
        Processes the video and returns batches of frames in the format required by the XCLIP model.
        """
        np.random.seed(0)
        videoreader = VideoReader(video_path, num_threads=1, ctx=cpu(0))
        videoreader.seek(0)
        seg_len = len(videoreader)
        indices = self.sample_frame_indices(clip_len, frame_sample_rate, seg_len)
        frames = videoreader.get_batch(indices).asnumpy()
        
        return frames


    def extract_descriptions(self):
        return self.list_of_categories

    def classify_batch(self, frames, descriptions):
        # Preprocessing of frames and descriptions
        inputs = self.processor(text=descriptions, videos=list(frames), return_tensors="pt", padding=True, truncation=True)

        # Prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Calculating similarity between images and text
        logits_per_video = outputs.logits_per_video  # Similarity score between images and text
        return logits_per_video

    def analyze_video(self, video_path, batch_size=32, frame_sample_rate = 4):
        """
        Analyzes the entire video, splits it into batches of frames, performs classification, and returns the results.
        """
        frames = self.process_video(video_path, 32, frame_sample_rate)

        descriptions = self.extract_descriptions()
        logits_per_video = self.classify_batch(frames, descriptions)

        return logits_per_video
    
# Sources:
# https://github.com/NielsRogge/Transformers-Tutorials/blob/master/X-CLIP/Zero_shot_classify_a_YouTube_video_with_X_CLIP.ipynb