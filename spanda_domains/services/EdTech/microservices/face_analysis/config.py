from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class VideoConfig:
    batch_size: int = 10
    output_fps: int = 4

@dataclass
class ModelConfig:
    gpu_id: int = -1

@dataclass
class AttentionConfig:
    # Head pose ranges
    pitch_range: Tuple[float, float] = (-40, 30)
    yaw_range: Tuple[float, float] = (-30, 30)
    # Attention thresholds
    t1: int = 2000  # threshold for "mostly focused" in ms
    t2: int = 4000  # threshold for "partially focused" in ms
    attention_threshold: float = 0.7

class Config:
    def __init__(self):
        load_dotenv()
        
        # Video processing configuration
        self.video = VideoConfig(
            batch_size=int(os.getenv('VIDEO_BATCH_SIZE', 10)),
            output_fps=int(os.getenv('VIDEO_OUTPUT_FPS', 4))
        )
        
        # Model configuration
        self.model = ModelConfig(
            gpu_id=int(os.getenv('MODEL_GPU_ID', -1))
        )
        
        # Attention detection configuration
        self.attention = AttentionConfig(
            pitch_range=(
                float(os.getenv('ATTENTION_PITCH_MIN', -40)),
                float(os.getenv('ATTENTION_PITCH_MAX', 30))
            ),
            yaw_range=(
                float(os.getenv('ATTENTION_YAW_MIN', -30)),
                float(os.getenv('ATTENTION_YAW_MAX', 30))
            ),
            t1=int(os.getenv('ATTENTION_T1', 2000)),
            t2=int(os.getenv('ATTENTION_T2', 4000)),
            attention_threshold=float(os.getenv('ATTENTION_THRESHOLD', 0.7))
        )

# Global config instance
config = Config()