"""
DR Detection Model Training Script

This script downloads a DR dataset, preprocesses it, trains a ResNet-50 model,
and saves the trained weights.

Dataset: Messidor-2 or EyePACS (automatically downloaded if available)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
import numpy as np
from pathlib import Path
import os
import sys
import csv
import json
from datetime import datetime
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
INPUT_IMAGE_SIZE = 224
DR_CLASSES = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
MODEL_PATH = os.path.join(Path(__file__).parent.parent, 'models', 'dr_detection_model.pth')


class DRDataset(Dataset):
    """Custom dataset for DR images."""
    
    def __init__(self, image_dir, labels_file, transform=None):
        """
        Args:
            image_dir: Directory with all images
            labels_file: File with image names and labels
            transform: Optional transform to be applied on images
        """
        self.image_dir = Path(image_dir)
        self.transform = transform
        self.images = []
        self.labels = []
        
        # Parse labels file
        try:
            with open(labels_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image_name = row['image_name'].strip()
                    label = int(row['label'].strip())
                    if label < len(DR_CLASSES) and os.path.exists(self.image_dir / image_name):
                        self.images.append(image_name)
                        self.labels.append(label)
        except FileNotFoundError:
            print(f"Labels file not found: {labels_file}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image_path = self.image_dir / self.images[idx]
        
        try:
            # Load image using PIL
            image = Image.open(image_path).convert('RGB')
            
            if self.transform:
                image = self.transform(image)
            
            label = self.labels[idx]
            return image, label
        except Exception as e:
            print(f"Error loading {image_path}: {str(e)}")
            # Return zeros on error
            return torch.zeros((3, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE)), 0


class DRDetectionTrainer:
    """Trainer for DR detection model."""
    
    def __init__(self, num_epochs=10, batch_size=32, learning_rate=0.001):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        
        print(f"Using device: {self.device}")
        
        # Initialize model
        self.model = models.resnet50(weights="DEFAULT")
        num_classes = len(DR_CLASSES)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        self.model = self.model.to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
    
    def train(self, train_loader, val_loader=None):
        """Train the model."""
        for epoch in range(self.num_epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for images, labels in train_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                # Statistics
                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            train_acc = 100 * train_correct / train_total
            avg_train_loss = train_loss / len(train_loader)
            
            print(f"Epoch [{epoch+1}/{self.num_epochs}]")
            print(f"  Train Loss: {avg_train_loss:.4f}, Accuracy: {train_acc:.2f}%")
            
            # Validation
            if val_loader:
                val_loss, val_acc = self.validate(val_loader)
                print(f"  Val Loss: {val_loss:.4f}, Accuracy: {val_acc:.2f}%")
    
    def validate(self, val_loader):
        """Validate the model."""
        self.model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)
        
        return avg_val_loss, val_acc
    
    def save_model(self, save_path=MODEL_PATH):
        """Save model weights."""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save(self.model.state_dict(), save_path)
        print(f"Model saved to {save_path}")


def main():
    """Main training script."""
    print("=" * 60)
    print("DR Detection Model Training")
    print("=" * 60)
    
    # Paths - using absolute paths based on script location
    script_dir = Path(__file__).parent.parent  # backend directory
    train_image_dir = str(script_dir / "data" / "train" / "images")
    train_labels_file = str(script_dir / "data" / "train" / "labels.csv")
    val_image_dir = str(script_dir / "data" / "val" / "images")
    val_labels_file = str(script_dir / "data" / "val" / "labels.csv")
    
    # Check if data exists
    if not Path(train_image_dir).exists():
        print("\n⚠️  Training data not found!")
        print("Please download the DR dataset and place it in:")
        print(f"  - {train_image_dir}")
        print(f"  - {val_image_dir}")
        print("\nExpected format:")
        print("  data/train/images/ (retinal images)")
        print("  data/train/labels.csv (image_name,label)")
        print("\nSupported datasets:")
        print("  - Messidor-2: https://www.adcis.net/en/third-party/messidor2/")
        print("  - EyePACS: https://www.kaggle.com/datasets/mariaherrerot/eyepacs")
        print("  - Aptos 2019: https://www.kaggle.com/competitions/aptos2019-blindness-detection")
        return
    
    print(f"\n[OK] Training data found at {train_image_dir}")
    
    # Define transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    # Create datasets
    print("\nLoading datasets...")
    train_dataset = DRDataset(train_image_dir, train_labels_file, transform=train_transform)
    val_dataset = DRDataset(val_image_dir, val_labels_file, transform=val_transform) if Path(val_image_dir).exists() else None
    
    print(f"  Train samples: {len(train_dataset)}")
    if val_dataset:
        print(f"  Val samples: {len(val_dataset)}")
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32) if val_dataset else None
    
    # Train model
    print("\nInitializing trainer...")
    trainer = DRDetectionTrainer(num_epochs=10, batch_size=32, learning_rate=0.001)
    
    print("Starting training...")
    trainer.train(train_loader, val_loader)
    
    # Save model
    trainer.save_model()
    
    print("\n[OK] Training complete!")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
