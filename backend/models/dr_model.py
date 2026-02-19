import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Dict
from config.settings import INPUT_IMAGE_SIZE, DR_CLASSES, MODEL_PATH


class DRDetectionModel:
    """Wrapper for DR detection model."""
    
    def __init__(self, model_path: str = MODEL_PATH):
        """
        Initialize DR detection model.
        
        Args:
            model_path: Path to trained model weights
        """
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()
        self.model.eval()
    
    def _load_model(self) -> nn.Module:
        """Load model from checkpoint."""
        try:
            # For MVP, we'll use ResNet-50 pretrained
            from torchvision import models
            
            model = models.resnet50(pretrained=True)
            
            # Modify final layer for DR classification (5 classes)
            num_classes = len(DR_CLASSES)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
            
            # Load weights if they exist
            try:
                checkpoint = torch.load(self.model_path, map_location=self.device)
                model.load_state_dict(checkpoint)
            except FileNotFoundError:
                print(f"No pretrained weights found at {self.model_path}. Using pretrained ResNet-50 only.")
            
            model = model.to(self.device)
            return model
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def predict(self, image_array: np.ndarray) -> Tuple[str, float, int]:
        """
        Predict DR severity for an image.
        
        Args:
            image_array: Preprocessed image array (C, H, W)
        
        Returns:
            Tuple of (DR_severity_class, confidence_score, class_index)
        """
        with torch.no_grad():
            # Convert to tensor and add batch dimension
            image_tensor = torch.from_numpy(image_array).float().unsqueeze(0)
            image_tensor = image_tensor.to(self.device)
            
            # Forward pass
            output = self.model(image_tensor)
            
            # Get probabilities
            probabilities = torch.softmax(output, dim=1)
            
            # Get prediction
            class_idx = probabilities.argmax(dim=1).item()
            confidence = probabilities[0, class_idx].item()
            severity_class = DR_CLASSES[class_idx]
            
            return severity_class, confidence, class_idx
    
    def get_target_layer(self) -> nn.Module:
        """Get the target layer for Grad-CAM (last residual block of ResNet-50)."""
        return self.model.layer4[-1]
