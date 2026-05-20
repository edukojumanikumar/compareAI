# Development Guide - Room Inspection Platform

## Project Overview

This is a **Proof of Concept (POC)** for an AI-powered room inspection platform. The MVP (Phase 1) focuses on core image comparison functionality without database integration.

## Architecture

### Current Stack (Phase 1)
```
┌─────────────────────────────────────┐
│      FastAPI Web Server             │
│  (app.py - Port 8000)               │
└──────────┬──────────────────────────┘
           │
           ├─────────────────────────────────────────┐
           │                                         │
    ┌──────▼──────┐                          ┌──────▼──────┐
    │   Image     │                          │   Result    │
    │ Comparison  │                          │ Generation  │
    │ Engine      │                          │             │
    │ (image_     │                          └─────────────┘
    │  compare.py)│
    └─────────────┘
           │
           ├─────────────────────────────────────────┐
           │                                         │
    ┌──────▼──────┐                          ┌──────▼──────┐
    │  Temporary  │                          │    File     │
    │   Memory    │                          │   Upload    │
    │ Processing  │                          │   Storage   │
    └─────────────┘                          └─────────────┘
```

### Future Stack (Phase 2+)
```
Mobile App (React Native/Flutter)
            │
            ▼
┌───────────────────────────┐
│  FastAPI Backend          │
├───────────────────────────┤
│ - Authentication          │
│ - API Endpoints           │
│ - WebSocket Support       │
└──────────┬────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
PostgreSQL    AWS S3
Database      Storage
```

## Code Structure

### app.py - Main API Server
**Responsibilities:**
- FastAPI application setup
- CORS middleware configuration
- API endpoint definitions
- File upload handling
- Request validation

**Key Endpoints:**
```python
POST /compare          # Main comparison endpoint
POST /validate         # Image quality validation
GET  /health           # Health check
GET  /                 # API info
```

**Dependencies:**
- FastAPI, Uvicorn
- Pydantic (validation)
- Python multipart (file uploads)

### image_compare.py - Computer Vision Engine
**Responsibilities:**
- Image loading and validation
- Feature detection and matching
- Image alignment and transformation
- Similarity calculation
- Issue detection

**Key Classes:**
```python
class ImageComparator:
    - compare(ref_path, insp_path)
    - validate_image(image_path)
    - align_images(ref_img, insp_img)
    - compare_aligned_images(ref_img, aligned_insp)
    - generate_result(comparison_result)
```

**Algorithm Flow:**
1. **Image Validation** → Quality checks
2. **Image Alignment** → Feature matching + homography
3. **Image Comparison** → SSIM + difference detection
4. **Result Generation** → Score + status + issues

## Workflow

### Request Flow
```
1. Client uploads reference + inspection images
   ↓
2. app.py receives POST /compare request
   ↓
3. Temporary files created
   ↓
4. ImageComparator.compare() called
   ↓
5. Validation → Alignment → Comparison → Generation
   ↓
6. JSON response returned
   ↓
7. Temporary files cleaned up
```

## Computer Vision Techniques

### 1. Image Alignment
**Purpose**: Normalize perspective differences between images

**Method**: SIFT + Homography
```
Reference Image → SIFT Features
Inspection Image → SIFT Features
               ↓
         Feature Matching
               ↓
        Compute Homography
               ↓
    Warp Inspection Image
```

**Parameters:**
- SIFT keypoints: Scale-invariant features
- BFMatcher: Brute-force feature matching
- Lowe's ratio test: Filter good matches (0.75 threshold)
- RANSAC: Robust homography estimation

### 2. Image Comparison
**Purpose**: Quantify visual differences

**Methods:**
- **SSIM (Structural Similarity Index)**
  - Considers luminance, contrast, structure
  - Range: 0.0 (different) to 1.0 (identical)
  - More perceptually relevant than MSE

- **Pixel Difference Analysis**
  - LAB color space (perceptually uniform)
  - Per-channel difference calculation
  - Change region detection

### 3. Result Generation
**Purpose**: Convert metrics to actionable results

**Logic:**
```
Similarity Score (0-100)
         ↓
    Threshold Check
    ├─ >= 90 → PASS
    ├─ >= 75 → MINOR_ISSUES
    ├─ >= 60 → REVIEW
    └─ < 60  → FAIL
         ↓
    Issue Detection
    └─ Generate human-readable messages
```

## Key Technologies

| Technology | Purpose | Why Chosen |
|-----------|---------|-----------|
| OpenCV | Image processing | Industry standard, well-documented |
| SIFT | Feature detection | Robust to scale/rotation changes |
| NumPy | Numerical computing | Fast array operations |
| FastAPI | Web framework | Modern, type-safe, auto-docs |
| Uvicorn | ASGI server | High-performance, async-ready |
| scikit-image | Image utilities | Complementary to OpenCV |

## Configuration

Edit `config.py` to adjust:

```python
# Image validation thresholds
blur_threshold = 100
brightness_min = 30
brightness_max = 225

# Comparison settings
match_ratio_threshold = 0.75
min_matches = 4

# Status thresholds
pass_threshold = 90
minor_issues_threshold = 75
review_threshold = 60
```

## Performance Considerations

### Optimization Areas
1. **Image Resizing**: Reduce to 1920x1440 for faster processing
2. **Grayscale Conversion**: Used where color not needed
3. **Async Processing**: FastAPI handles concurrent requests
4. **Memory Management**: Temporary file cleanup

### Typical Performance
- Average processing time: 2-5 seconds
- Max supported resolution: 4K
- Max file size: 50MB
- Concurrent connections: Limited by server

## Error Handling

### HTTP Status Codes
```python
200 - Success
400 - Invalid input (bad file format)
500 - Server error (processing failure)
```

### Error Response Format
```json
{
  "error": "Error message",
  "message": "Human-readable description"
}
```

## Testing

### Unit Test Areas (Phase 2)
- Image validation logic
- Feature matching accuracy
- SSIM calculation
- Threshold logic

### Integration Test Areas
- File upload handling
- End-to-end comparison
- API response format
- Error handling

### Sample Test Script
```bash
# Run test_api.py with sample images
python test_api.py
```

## Debugging

### Enable Debug Logging
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Low scores on good images**
```
→ Check image angle/perspective
→ Review lighting conditions
→ Verify room hasn't actually changed
→ Adjust thresholds in config.py
```

**Images won't align**
```
→ Ensure images show same room
→ Check for sufficient features
→ Verify image quality
→ Review feature matching results
```

**Slow processing**
```
→ Reduce image resolution
→ Check system resources
→ Monitor CPU/Memory usage
→ Consider image preprocessing
```

## Code Quality

### Style Guide
- Follow PEP 8
- Type hints for functions
- Docstrings for modules/classes
- Comments for complex logic

### Current Code Quality
- ✅ Well-documented
- ✅ Clear function signatures
- ✅ Modular design
- ⚠️ No unit tests (Phase 2)
- ⚠️ No database integration (Phase 2)

## Future Enhancements

### Phase 2 (Database & Analytics)
- [ ] PostgreSQL integration
- [ ] Inspection history tracking
- [ ] Staff performance metrics
- [ ] Trend analysis
- [ ] Web dashboard

### Phase 3 (Advanced AI)
- [ ] YOLOv8 object detection
- [ ] Specific item identification
- [ ] Cleanliness scoring
- [ ] Damage detection
- [ ] Missing item alerts

### Phase 4 (Platform Expansion)
- [ ] Mobile app (React Native)
- [ ] Multi-room support
- [ ] Custom thresholds per room type
- [ ] Automated scheduling
- [ ] Integration with property management systems

### Phase 5 (Multi-Domain)
- [ ] Car rental inspections
- [ ] Fleet management
- [ ] Insurance applications
- [ ] Dispute resolution

## Deployment

### Local Development
```bash
python app.py
```

### Docker
```bash
docker build -t room-inspection .
docker run -p 8000:8000 room-inspection
```

### Cloud (AWS/Azure)
- Containerize with Docker
- Deploy to ECS/App Service
- Use S3/Blob for storage
- Setup CloudFront/CDN

## Security Considerations

### Current Implementation
- File type validation
- File size limits
- CORS configuration

### Future Improvements (Phase 2+)
- [ ] Authentication/Authorization
- [ ] Rate limiting
- [ ] API key validation
- [ ] HTTPS enforcement
- [ ] Input sanitization
- [ ] Audit logging

## Contributing Guidelines

1. **Code Style**: Follow PEP 8
2. **Documentation**: Update docstrings
3. **Testing**: Add unit tests for new features
4. **Commits**: Clear, descriptive messages
5. **Branches**: feature/*, bugfix/*, etc.

## References

### Academic Papers
- SIFT: Distinctive Image Features from Scale-Invariant Keypoints
- SSIM: Image Quality Assessment: From Error Visibility to Structural Similarity

### Library Documentation
- OpenCV: https://docs.opencv.org/
- FastAPI: https://fastapi.tiangolo.com/
- NumPy: https://numpy.org/doc/

### Useful Articles
- Feature Matching: https://docs.opencv.org/
- Homography: https://en.wikipedia.org/wiki/Homography

---

**Version**: 0.1.0 (POC/MVP)
**Last Updated**: 2026-05-20
**Maintainers**: Development Team
