"""
Test script for Room Inspection API
Run this script to test the API with sample images
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /health")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_compare(ref_image_path: str, insp_image_path: str):
    """Test image comparison endpoint"""
    print("\n" + "="*60)
    print("Testing: POST /compare")
    print("="*60)
    
    # Check if test images exist
    if not Path(ref_image_path).exists():
        print(f"⚠️  Reference image not found: {ref_image_path}")
        print("Please provide sample room images to test")
        return False
    
    if not Path(insp_image_path).exists():
        print(f"⚠️  Inspection image not found: {insp_image_path}")
        print("Please provide sample room images to test")
        return False
    
    print(f"Reference Image: {ref_image_path}")
    print(f"Inspection Image: {insp_image_path}")
    
    with open(ref_image_path, 'rb') as ref_file, \
         open(insp_image_path, 'rb') as insp_file:
        
        files = {
            'reference_image': ref_file,
            'inspection_image': insp_file
        }
        
        response = requests.post(f"{BASE_URL}/compare", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_validate(image_path: str):
    """Test image validation endpoint"""
    print("\n" + "="*60)
    print("Testing: POST /validate")
    print("="*60)
    
    if not Path(image_path).exists():
        print(f"⚠️  Image not found: {image_path}")
        return False
    
    print(f"Image: {image_path}")
    
    with open(image_path, 'rb') as img_file:
        files = {'image': img_file}
        response = requests.post(f"{BASE_URL}/validate", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def main():
    """Run all tests"""
    print("\n" + "🔍 "*20)
    print("Room Inspection API - Test Suite")
    print("🔍 "*20)
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Validate image (if sample exists)
    sample_image = "sample_room.jpg"
    if Path(sample_image).exists():
        test_validate(sample_image)
    else:
        print("\n⚠️  Sample image not found")
        print("To test with real images:")
        print("1. Place 'sample_room.jpg' in this directory")
        print("2. Place 'sample_room_after.jpg' for comparison test")
    
    # Test 3: Compare images (if samples exist)
    ref_image = "sample_room.jpg"
    insp_image = "sample_room_after.jpg"
    if Path(ref_image).exists() and Path(insp_image).exists():
        test_compare(ref_image, insp_image)
    else:
        print("\n⚠️  Sample images not found for comparison test")
        print("To test comparison:")
        print("1. Place 'sample_room.jpg' (reference) in this directory")
        print("2. Place 'sample_room_after.jpg' (inspection) in this directory")
    
    print("\n" + "="*60)
    print("✅ Test suite completed")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Make sure the API is running at http://localhost:8000")
    print("   Start it with: python app.py\n")
    
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API at {BASE_URL}")
        print("Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
