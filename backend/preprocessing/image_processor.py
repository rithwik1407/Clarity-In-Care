import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from config.settings import (
    INPUT_IMAGE_SIZE,
    CLAHE_CLIP_LIMIT,
    CLAHE_TILE_GRID_SIZE,
    NORMALIZE_MEAN,
    NORMALIZE_STD,
)


class ImagePreprocessor:
    """Handles image preprocessing for DR detection model."""
    
    @staticmethod
    def validate_image(file_content: bytes, filename: str) -> bool:
        """Validate image format and size."""
        try:
            img = Image.open(BytesIO(file_content))
            file_ext = filename.split(".")[-1].lower()
            return file_ext in {"jpg", "jpeg", "png"}
        except Exception:
            return False
    
    @staticmethod
    def resize_image(image: np.ndarray, size: tuple = INPUT_IMAGE_SIZE) -> np.ndarray:
        """Resize image to standard input size."""
        return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def apply_clahe(image: np.ndarray) -> np.ndarray:
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(
            clipLimit=CLAHE_CLIP_LIMIT,
            tileGridSize=CLAHE_TILE_GRID_SIZE
        )
        l_channel = clahe.apply(l_channel)
        
        # Merge channels back
        lab = cv2.merge([l_channel, a_channel, b_channel])
        
        # Convert back to RGB
        enhanced_image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        return enhanced_image
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """Normalize image using ImageNet statistics."""
        # Convert to float32 and normalize to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Apply mean and std normalization
        mean = np.array(NORMALIZE_MEAN, dtype=np.float32).reshape(1, 1, 3)
        std = np.array(NORMALIZE_STD, dtype=np.float32).reshape(1, 1, 3)
        image = (image - mean) / std
        
        return image
    
    @staticmethod
    def preprocess(file_content: bytes, filename: str) -> np.ndarray:
        """Complete preprocessing pipeline."""
        # Read image from bytes
        image = cv2.imdecode(
            np.frombuffer(file_content, np.uint8),
            cv2.IMREAD_COLOR
        )
        
        if image is None:
            raise ValueError("Failed to read image file")
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        image = ImagePreprocessor.resize_image(image)
        
        # Apply CLAHE enhancement
        image = ImagePreprocessor.apply_clahe(image)
        
        # Normalize
        image = ImagePreprocessor.normalize_image(image)
        
        # Convert to torch format (C, H, W)
        image = np.transpose(image, (2, 0, 1))
        
        return image
    
    @staticmethod
    def load_image_for_visualization(file_content: bytes) -> np.ndarray:
        """Load image for visualization (without normalization)."""
        image = cv2.imdecode(
            np.frombuffer(file_content, np.uint8),
            cv2.IMREAD_COLOR
        )
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = ImagePreprocessor.resize_image(image)
        return image
