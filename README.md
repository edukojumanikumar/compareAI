# AI Room Inspection & Consistency Verification Platform

AI-powered visual inspection platform designed to compare reference room images with inspection images to verify room consistency and cleanliness.

## Overview

This POC (Proof of Concept) backend provides core image comparison functionality for:
- **Airbnb rooms** - Guest turnover verification
- **Hotels** - Housekeeping quality assurance
- **Vacation rentals** - Property condition verification
- **Future**: Car rental and fleet inspections

## Core Workflow

```
Reference Image Upload
         ↓
Inspection Image Upload
         ↓
Image Quality Validation
         ↓
Feature Alignment
         ↓
Image Comparison
         ↓
Result & Issue Detection
```

## MVP Features (Phase 1)

✅ **Image Validation**
- Blur detection
- Brightness validation
- Resolution checks

✅ **Image Alignment**
- SIFT feature matching
- Perspective correction
- Homography transformation

✅ **Image Comparison**
- Structural similarity (SSIM) analysis
- Change region detection
- Layout difference analysis

✅ **Result Generation**
- Similarity scoring (0-100)
- Status determination (PASS/MINOR_ISSUES/REVIEW/FAIL)
- Issue detection

## Project Structure

```
app/
├── app.py              # FastAPI application & API endpoints
├── image_compare.py    # Image comparison engine
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── uploads/            # Temporary upload directory (created at runtime)
```

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone or navigate to project**
```bash
cd c:\Users\manik\Desktop\app
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the API server
```bash
python app.py
```

The API will be available at `http://localhost:8000`

### Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /compare
Compare reference image with inspection image

**Request:**
```bash
curl -X POST "http://localhost:8000/compare" \
  -F "reference_image=@reference.jpg" \
  -F "inspection_image=@inspection.jpg"
```

**Response:**
```json
{
  "score": 82,
  "status": "MINOR_ISSUES",
  "message": "Minor issues detected. Room is mostly in expected condition but review recommended.",
  "issues": [
    "Moderate changes detected in room layout"
  ],
  "metadata": {
    "change_percentage": 18.5,
    "comparison_confidence": "MEDIUM"
  }
}
```

### POST /validate
Validate single image quality

**Request:**
```bash
curl -X POST "http://localhost:8000/validate" \
  -F "image=@room.jpg"
```

**Response:**
```json
{
  "is_valid": true,
  "quality_score": 92,
  "blur_score": 95,
  "brightness_score": 90,
  "size_score": 100,
  "issues": [],
  "recommendations": []
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Room Inspection API"
}
```

## Result Status Codes

| Status | Score Range | Meaning |
|--------|-------------|---------|
| **PASS** | 90-100 | Room is in expected condition |
| **MINOR_ISSUES** | 75-89 | Minor issues detected, review recommended |
| **REVIEW** | 60-74 | Significant differences, manual review required |
| **FAIL** | 0-59 | Room does not meet inspection standards |

## How It Works

### Step 1: Image Quality Validation
- **Blur Detection**: Uses Laplacian variance to detect blurry images
- **Brightness Check**: Validates brightness is within acceptable range
- **Size Validation**: Ensures minimum resolution for reliable comparison

### Step 2: Image Alignment
- **SIFT Feature Detection**: Finds distinctive keypoints in both images
- **Feature Matching**: Matches features using BFMatcher
- **Homography Estimation**: Computes perspective transformation matrix
- **Image Warping**: Aligns inspection image to reference coordinate system

### Step 3: Image Comparison
- **Color Space Analysis**: Uses LAB color space for perceptual comparison
- **Pixel Difference Calculation**: Computes per-channel differences
- **SSIM Computation**: Calculates structural similarity index
- **Change Detection**: Identifies regions with significant changes

### Step 4: Result Generation
- **Similarity Scoring**: Converts SSIM to 0-100 score
- **Status Determination**: Applies threshold-based logic
- **Issue Detection**: Identifies problems based on metrics
- **Metadata**: Provides detailed comparison information

## Key Technologies

- **FastAPI**: Modern web framework for building APIs
- **OpenCV**: Computer vision library for image processing
- **NumPy**: Numerical computing library
- **SIFT**: Scale-Invariant Feature Transform for robust feature matching
- **Homography**: Perspective transformation for image alignment
- **SSIM**: Structural Similarity Index for perceptual image quality

## Limitations (Current POC)

- Single room type per deployment
- Limited to 2-image comparison (reference + inspection)
- No custom AI training
- Generic issue detection (not object-specific)
- No cleanliness/damage scoring yet
- No database persistence

## Future Enhancements (Phase 2+)

- [ ] YOLOv8 object detection for specific item identification
- [ ] Cleanliness scoring system
- [ ] Missing item detection
- [ ] Damage identification and localization
- [ ] Multiple reference images per room
- [ ] Room type classification
- [ ] Database integration (PostgreSQL)
- [ ] Cloud storage (AWS S3)
- [ ] Frontend mobile app (React Native/Flutter)
- [ ] Batch inspection processing
- [ ] Historical trend analysis
- [ ] AI-generated detailed inspection reports
- [ ] Insurance/dispute verification

## Configuration

Edit `image_compare.py` to adjust comparison parameters:

```python
# Blur detection threshold
self.blur_threshold = 100

# Brightness range (0-255 LAB scale)
self.brightness_min = 30
self.brightness_max = 225

# Feature matching parameters
self.sift = cv2.SIFT_create()
self.bf = cv2.BFMatcher()
```

## Troubleshooting

### ImportError: No module named 'fastapi'
```bash
pip install -r requirements.txt
```

### Images not aligning properly
- Ensure images show the same room
- Try improving image quality (better lighting, focus)
- Check that room layout is similar between images

### Low similarity scores on good images
- Images may be taken from different angles
- Lighting conditions may differ significantly
- Try adjusting comparison thresholds in `image_compare.py`

## Error Handling

The API returns appropriate HTTP status codes:
- **200**: Success
- **400**: Invalid input (unsupported file format)
- **500**: Server error (image processing failure)

All errors include descriptive messages for debugging.

## Testing

### Quick test with sample images:
```bash
# Using curl
curl -X POST "http://localhost:8000/compare" \
  -F "reference_image=@test_ref.jpg" \
  -F "inspection_image=@test_insp.jpg"
```

### Validate image quality:
```bash
curl -X POST "http://localhost:8000/validate" \
  -F "image=@test.jpg"
```

## Performance

- Average comparison time: 2-5 seconds (depends on image resolution)
- Recommended max resolution: 4K
- Minimum recommended resolution: 1080p

## License

Internal use for Airbnb, hotel, and vacation rental inspections

## Support

For issues or questions, contact the development team.

---

**Version**: 0.1.0 (MVP/POC)  
**Last Updated**: 2026-05-20
