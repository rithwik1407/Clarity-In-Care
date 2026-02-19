"""
Example usage of the Clarity in Care API

This script demonstrates how to:
1. Create a patient
2. Upload a retinal image for prediction
3. Retrieve scan history
"""

import requests
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")


def check_health():
    """Check if API is running."""
    print_section("1. Checking API Health")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✓ API is running{Colors.END}")
            print(f"  Status: {data['status']}")
            print(f"  Version: {data['version']}")
            print(f"  Model Loaded: {data['model_loaded']}")
            return True
        else:
            print(f"{Colors.RED}✗ API returned status {response.status_code}{Colors.END}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to API at {API_BASE_URL}{Colors.END}")
        print(f"   Make sure to run: {Colors.YELLOW}python main.py{Colors.END}")
        return False


def create_patient():
    """Create a patient."""
    print_section("2. Creating Patient")
    
    patient_data = {
        "name": "Jane Smith",
        "age": 52,
        "email": "jane@example.com",
        "phone": "+1-555-0123",
        "medical_history": "Type 2 Diabetes, Hypertension"
    }
    
    print(f"Creating patient with data:")
    print(json.dumps(patient_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/patients/",
            json=patient_data
        )
        
        if response.status_code == 200:
            patient = response.json()
            print(f"\n{Colors.GREEN}✓ Patient created successfully{Colors.END}")
            print(f"  Patient ID: {Colors.BOLD}{patient['id']}{Colors.END}")
            print(f"  Name: {patient['name']}")
            print(f"  Age: {patient['age']}")
            return patient['id']
        else:
            print(f"{Colors.RED}✗ Failed to create patient: {response.text}{Colors.END}")
            return None
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {str(e)}{Colors.END}")
        return None


def predict_dr(patient_id, image_path="example_retinal_image.jpg"):
    """Predict DR from retinal image."""
    print_section("3. Predicting DR from Image")
    
    # Check if example image exists
    if not Path(image_path).exists():
        print(f"{Colors.YELLOW}⚠ Image file not found: {image_path}{Colors.END}")
        print(f"\nTo test predictions:")
        print(f"  1. Download a retinal image from a DR dataset")
        print(f"  2. Place it in the backend directory")
        print(f"  3. Update image_path in this script")
        print(f"\nSupported datasets:")
        print(f"  - Messidor-2: https://www.adcis.net/en/third-party/messidor2/")
        print(f"  - EyePACS: https://www.kaggle.com/datasets/mariaherrerot/eyepacs")
        return None
    
    print(f"Uploading image: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'patient_id': patient_id,
                'visit_type': 'pre-treatment',
                'notes': 'Initial screening for DR'
            }
            
            response = requests.post(
                f"{API_BASE_URL}/predict/",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            prediction = response.json()
            print(f"{Colors.GREEN}✓ Prediction completed{Colors.END}")
            print(f"  DR Severity: {Colors.BOLD}{prediction['dr_severity']}{Colors.END}")
            print(f"  Confidence: {Colors.BOLD}{prediction['confidence_score']:.1%}{Colors.END}")
            print(f"  Scan ID: {prediction['scan_id']}")
            print(f"  Heatmap URL: {prediction['heatmap_url']}")
            return prediction
        else:
            print(f"{Colors.RED}✗ Prediction failed: {response.text}{Colors.END}")
            return None
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {str(e)}{Colors.END}")
        return None


def get_scan_history(patient_id):
    """Get patient scan history."""
    print_section("4. Retrieving Scan History")
    
    print(f"Fetching history for patient: {patient_id}\n")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/predict/patient/{patient_id}/history"
        )
        
        if response.status_code == 200:
            scans = response.json()
            
            if scans:
                print(f"{Colors.GREEN}✓ Found {len(scans)} scan(s){Colors.END}\n")
                
                for i, scan in enumerate(scans, 1):
                    print(f"{Colors.BOLD}Scan {i}:{Colors.END}")
                    print(f"  ID: {scan['id']}")
                    print(f"  Date: {scan['scan_timestamp']}")
                    print(f"  Type: {scan['visit_type']}")
                    print(f"  DR Severity: {Colors.BOLD}{scan['dr_severity']}{Colors.END}")
                    print(f"  Confidence: {scan['confidence_score']:.1%}")
                    print()
            else:
                print(f"{Colors.YELLOW}⚠ No scans found for this patient{Colors.END}")
            
            return scans
        else:
            print(f"{Colors.RED}✗ Failed to retrieve history: {response.text}{Colors.END}")
            return None
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {str(e)}{Colors.END}")
        return None


def main():
    """Run example workflow."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   Clarity in Care - API Example Usage                   ║")
    print("║   Diabetic Retinopathy Detection System                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # Step 1: Health check
    if not check_health():
        return
    
    # Step 2: Create patient
    patient_id = create_patient()
    if not patient_id:
        return
    
    # Step 3: Predict (if image available)
    prediction = predict_dr(patient_id)
    
    # Step 4: Get history
    if patient_id:
        get_scan_history(patient_id)
    
    # Summary
    print_section("Example Complete")
    print(f"\n{Colors.GREEN}✓ API is working correctly!{Colors.END}")
    print(f"\nNext steps:")
    print(f"  1. Visit API docs: {Colors.CYAN}http://localhost:8000/docs{Colors.END}")
    print(f"  2. Train model: {Colors.CYAN}python scripts/train_model.py{Colors.END}")
    print(f"  3. Deploy to cloud: See {Colors.CYAN}DEPLOYMENT.md{Colors.END}")
    print()


if __name__ == "__main__":
    main()
