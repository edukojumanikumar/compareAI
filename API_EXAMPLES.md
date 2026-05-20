"""
API Usage Examples
Real-world examples for using the Room Inspection API
"""

# ============================================================================
# EXAMPLE 1: Python Requests Library
# ============================================================================

import requests
import json

def compare_room_images_example():
    """Example: Compare room images using requests"""
    
    url = "http://localhost:8000/compare"
    
    # Prepare files
    with open("reference_room.jpg", "rb") as ref:
        with open("inspection_room.jpg", "rb") as insp:
            files = {
                "reference_image": ref,
                "inspection_image": insp
            }
            
            # Send request
            response = requests.post(url, files=files)
    
    # Parse response
    if response.status_code == 200:
        result = response.json()
        print(f"Score: {result['score']}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Issues: {result['issues']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


# ============================================================================
# EXAMPLE 2: Using Python async
# ============================================================================

import asyncio
import aiohttp

async def compare_async():
    """Example: Async comparison request"""
    
    async with aiohttp.ClientSession() as session:
        with open("reference_room.jpg", "rb") as ref:
            with open("inspection_room.jpg", "rb") as insp:
                data = aiohttp.FormData()
                data.add_field("reference_image", ref)
                data.add_field("inspection_image", insp)
                
                async with session.post(
                    "http://localhost:8000/compare",
                    data=data
                ) as resp:
                    result = await resp.json()
                    print(json.dumps(result, indent=2))


# ============================================================================
# EXAMPLE 3: Image Validation
# ============================================================================

def validate_image_example():
    """Example: Validate single image quality"""
    
    url = "http://localhost:8000/validate"
    
    with open("room_photo.jpg", "rb") as img:
        files = {"image": img}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Quality Score: {result['quality_score']}/100")
        print(f"Is Valid: {result['is_valid']}")
        
        if result['issues']:
            print(f"Issues: {', '.join(result['issues'])}")
        
        if result['recommendations']:
            print(f"Recommendations:")
            for rec in result['recommendations']:
                print(f"  - {rec}")


# ============================================================================
# EXAMPLE 4: Batch Processing
# ============================================================================

def batch_compare_rooms():
    """Example: Process multiple room comparisons"""
    
    rooms = [
        {"ref": "room1_ref.jpg", "insp": "room1_insp.jpg", "name": "Master Bedroom"},
        {"ref": "room2_ref.jpg", "insp": "room2_insp.jpg", "name": "Living Room"},
        {"ref": "room3_ref.jpg", "insp": "room3_insp.jpg", "name": "Kitchen"},
    ]
    
    results = []
    
    for room in rooms:
        print(f"Processing: {room['name']}...")
        
        with open(room['ref'], 'rb') as ref:
            with open(room['insp'], 'rb') as insp:
                files = {
                    "reference_image": ref,
                    "inspection_image": insp
                }
                
                response = requests.post(
                    "http://localhost:8000/compare",
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        "room": room['name'],
                        "score": result['score'],
                        "status": result['status']
                    })
                    print(f"  ✓ Score: {result['score']}, Status: {result['status']}")
                else:
                    print(f"  ✗ Error: {response.status_code}")
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    passed = len([r for r in results if r['status'] == 'PASS'])
    failed = len([r for r in results if r['status'] == 'FAIL'])
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {len(results)}")
    
    return results


# ============================================================================
# EXAMPLE 5: Error Handling
# ============================================================================

def compare_with_error_handling():
    """Example: Proper error handling"""
    
    try:
        # Validate files exist
        import os
        
        if not os.path.exists("reference_room.jpg"):
            raise FileNotFoundError("Reference image not found")
        if not os.path.exists("inspection_room.jpg"):
            raise FileNotFoundError("Inspection image not found")
        
        # Make request
        with open("reference_room.jpg", "rb") as ref:
            with open("inspection_room.jpg", "rb") as insp:
                files = {
                    "reference_image": ref,
                    "inspection_image": insp
                }
                
                response = requests.post(
                    "http://localhost:8000/compare",
                    files=files,
                    timeout=30
                )
        
        # Handle response
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            print("Bad request - check image format")
            print(response.json())
        elif response.status_code == 500:
            print("Server error - check logs")
            print(response.json())
        else:
            print(f"Unexpected status: {response.status_code}")
    
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except requests.exceptions.Timeout:
        print("Request timeout - server taking too long")
    except requests.exceptions.ConnectionError:
        print("Connection error - cannot reach server")
    except Exception as e:
        print(f"Unexpected error: {e}")


# ============================================================================
# EXAMPLE 6: cURL Commands
# ============================================================================

"""
CURL EXAMPLES:

1. Compare two images:
   curl -X POST "http://localhost:8000/compare" \
     -F "reference_image=@reference_room.jpg" \
     -F "inspection_image=@inspection_room.jpg"

2. Validate single image:
   curl -X POST "http://localhost:8000/validate" \
     -F "image=@room_photo.jpg"

3. Health check:
   curl http://localhost:8000/health

4. Get API info:
   curl http://localhost:8000/

5. Pretty print response:
   curl -s http://localhost:8000/health | python -m json.tool

6. Save response to file:
   curl -X POST "http://localhost:8000/compare" \
     -F "reference_image=@reference_room.jpg" \
     -F "inspection_image=@inspection_room.jpg" \
     > comparison_result.json

7. With timeout:
   curl --max-time 30 http://localhost:8000/health

8. Verbose output:
   curl -v http://localhost:8000/health
"""


# ============================================================================
# EXAMPLE 7: PowerShell/Windows
# ============================================================================

"""
POWERSHELL EXAMPLES:

1. Compare images:
   $ref = Get-Content "reference_room.jpg" -AsByteStream
   $insp = Get-Content "inspection_room.jpg" -AsByteStream
   
   $form = @{
       reference_image = $ref
       inspection_image = $insp
   }
   
   Invoke-RestMethod -Uri "http://localhost:8000/compare" `
       -Method Post `
       -Form $form

2. Health check:
   Invoke-RestMethod -Uri "http://localhost:8000/health" `
       -Method Get

3. Save response:
   $result = Invoke-RestMethod -Uri "http://localhost:8000/health"
   $result | ConvertTo-Json | Out-File "result.json"
"""


# ============================================================================
# EXAMPLE 8: JavaScript/Node.js
# ============================================================================

"""
JAVASCRIPT EXAMPLE:

// Fetch API
async function compareRoomImages() {
    const formData = new FormData();
    
    const refFile = document.getElementById('referenceInput').files[0];
    const inspFile = document.getElementById('inspectionInput').files[0];
    
    formData.append('reference_image', refFile);
    formData.append('inspection_image', inspFile);
    
    try {
        const response = await fetch('http://localhost:8000/compare', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        console.log('Score:', result.score);
        console.log('Status:', result.status);
        console.log('Message:', result.message);
        
        return result;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Axios
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function compareWithAxios() {
    const data = new FormData();
    data.append('reference_image', fs.createReadStream('reference_room.jpg'));
    data.append('inspection_image', fs.createReadStream('inspection_room.jpg'));
    
    try {
        const response = await axios.post(
            'http://localhost:8000/compare',
            data,
            { headers: data.getHeaders() }
        );
        
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error);
    }
}
"""


# ============================================================================
# EXAMPLE 9: Response Processing
# ============================================================================

def process_comparison_result(result):
    """Example: Process and interpret comparison result"""
    
    score = result['score']
    status = result['status']
    issues = result['issues']
    
    # Interpret result
    if status == 'PASS':
        action = "✅ APPROVE - Room meets standards"
        priority = "LOW"
    elif status == 'MINOR_ISSUES':
        action = "⚠️ REVIEW - Minor issues found"
        priority = "MEDIUM"
    elif status == 'REVIEW':
        action = "🔍 INVESTIGATE - Significant differences"
        priority = "HIGH"
    else:  # FAIL
        action = "❌ REJECT - Does not meet standards"
        priority = "CRITICAL"
    
    print(f"Room Inspection Result")
    print(f"{'='*40}")
    print(f"Similarity Score: {score}/100")
    print(f"Status: {status}")
    print(f"Priority: {priority}")
    print(f"Action: {action}")
    
    if issues:
        print(f"\nDetected Issues:")
        for issue in issues:
            print(f"  • {issue}")
    
    return {
        "action": action,
        "priority": priority,
        "needs_review": status in ['MINOR_ISSUES', 'REVIEW', 'FAIL']
    }


# ============================================================================
# EXAMPLE 10: Integration with Database (Phase 2)
# ============================================================================

"""
# Future: Database integration example

def save_comparison_to_db(room_id, result):
    '''Save comparison result to database'''
    
    from sqlalchemy import create_engine
    from models import Inspection, InspectionIssue
    
    engine = create_engine('postgresql://user:pass@localhost/room_inspection')
    
    with engine.Session() as session:
        # Create inspection record
        inspection = Inspection(
            room_id=room_id,
            score=result['score'],
            status=result['status'],
            message=result['message'],
            change_percentage=result['metadata']['change_percentage']
        )
        
        session.add(inspection)
        session.flush()
        
        # Create issue records
        for issue_text in result['issues']:
            issue = InspectionIssue(
                inspection_id=inspection.id,
                issue_type='GENERIC',
                description=issue_text,
                severity='MEDIUM'
            )
            session.add(issue)
        
        session.commit()
        return inspection.id
"""


# ============================================================================
# MAIN - Run Examples
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("Room Inspection API - Usage Examples\n")
    
    examples = {
        "1": ("Basic Comparison", compare_room_images_example),
        "2": ("Image Validation", validate_image_example),
        "3": ("Batch Processing", batch_compare_rooms),
        "4": ("Error Handling", compare_with_error_handling),
    }
    
    print("Available Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\nUsage: python api_examples.py <number>")
    print("Example: python api_examples.py 1")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        if choice in examples:
            name, func = examples[choice]
            print(f"\nRunning: {name}")
            print("="*50)
            func()
        else:
            print(f"Invalid choice: {choice}")
    else:
        print("\nNote: Set up your test images first!")
        print("  - reference_room.jpg")
        print("  - inspection_room.jpg")
