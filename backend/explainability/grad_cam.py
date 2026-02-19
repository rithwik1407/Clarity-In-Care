import numpy as np
import cv2
import torch
import torch.nn.functional as F
from typing import Tuple


class GradCAM:
    """Grad-CAM implementation for model explainability."""
    
    def __init__(self, model, target_layer):
        """
        Initialize Grad-CAM.
        
        Args:
            model: PyTorch model
            target_layer: Layer to compute gradients for
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self._save_activations)
        self.target_layer.register_full_backward_hook(self._save_gradients)
    
    def _save_activations(self, module, input, output):
        """Hook to save activations."""
        self.activations = output.detach()
    
    def _save_gradients(self, module, grad_input, grad_output):
        """Hook to save gradients."""
        self.gradients = grad_output[0].detach()
    
    def generate_cam(
        self,
        input_tensor: torch.Tensor,
        target_class: int = None
    ) -> np.ndarray:
        """
        Generate Grad-CAM heatmap.
        
        Args:
            input_tensor: Input image tensor (1, C, H, W)
            target_class: Target class index (if None, uses predicted class)
        
        Returns:
            CAM heatmap (normalized to 0-255)
        """
        # Forward pass
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Zero gradients
        self.model.zero_grad()
        
        # Backward pass
        class_score = output[0, target_class]
        class_score.backward()
        
        # Compute Grad-CAM
        gradients = self.gradients[0]  # (C, H, W)
        activations = self.activations[0]  # (C, H, W)
        
        weights = gradients.mean(dim=(1, 2))  # (C,)
        cam = torch.zeros_like(activations[0])
        
        for i in range(gradients.shape[0]):
            cam += weights[i] * activations[i]
        
        # ReLU to keep only positive contributions
        cam = F.relu(cam)
        
        # Normalize to 0-1
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max - cam_min > 0:
            cam = (cam - cam_min) / (cam_max - cam_min)
        
        return cam.cpu().numpy()
    
    @staticmethod
    def overlay_heatmap(
        image: np.ndarray,
        heatmap: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Overlay heatmap on original image.
        
        Args:
            image: Original image (H, W, 3)
            heatmap: Grad-CAM heatmap (H, W)
            alpha: Overlay transparency
        
        Returns:
            Overlayed image
        """
        h, w = heatmap.shape
        
        # Resize heatmap to match image size
        heatmap = cv2.resize(heatmap, (w, h))
        
        # Convert heatmap to 0-255 range
        heatmap_colored = cv2.applyColorMap(
            (heatmap * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        
        # Resize if needed
        if image.shape[:2] != heatmap_colored.shape[:2]:
            heatmap_colored = cv2.resize(
                heatmap_colored,
                (image.shape[1], image.shape[0])
            )
        
        # Convert image to BGR for consistent overlay
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        
        # Overlay
        overlayed = cv2.addWeighted(image_bgr, 1 - alpha, heatmap_colored, alpha, 0)
        
        # Convert back to RGB
        overlayed = cv2.cvtColor(overlayed, cv2.COLOR_BGR2RGB)
        
        return overlayed


def heatmap_to_bytes(heatmap_image: np.ndarray) -> bytes:
    """Convert heatmap image to JPEG bytes."""
    # Convert to BGR for cv2
    if len(heatmap_image.shape) == 3 and heatmap_image.shape[2] == 3:
        image_bgr = cv2.cvtColor(heatmap_image, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = heatmap_image
    
    # Encode to JPEG
    success, buffer = cv2.imencode(".jpg", image_bgr)
    if not success:
        raise ValueError("Failed to encode heatmap to JPEG")
    
    return buffer.tobytes()
