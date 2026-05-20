# Quick Start Guide - Room Inspection API

## 🚀 5-Minute Setup

### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd c:\Users\manik\Desktop\app

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Test the API

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **API Docs**: http://localhost:8000/redoc

## 📝 Using the API

### Option 1: Browser (Recommended for Testing)

1. Go to http://localhost:8000/docs
2. Click on "POST /compare"
3. Click "Try it out"
4. Upload reference image and inspection image
5. Click "Execute"

### Option 2: Command Line (cURL)

```bash
curl -X POST "http://localhost:8000/compare" \
  -F "reference_image=@room_before.jpg" \
  -F "inspection_image=@room_after.jpg"
```

### Option 3: Python Script

```python
import requests

files = {
    'reference_image': open('room_before.jpg', 'rb'),
    'inspection_image': open('room_after.jpg', 'rb')
}

response = requests.post('http://localhost:8000/compare', files=files)
print(response.json())
```

## 📊 Understanding Results

### Example Response

```json
{
  "score": 82,
  "status": "MINOR_ISSUES",
  "message": "Minor issues detected. Room is mostly in expected condition but review recommended.",
  "issues": ["Moderate changes detected in room layout"],
  "metadata": {
    "change_percentage": 18.5,
    "comparison_confidence": "MEDIUM"
  }
}
```

### Status Meanings

| Status | Score | Action |
|--------|-------|--------|
| ✅ PASS | 90-100 | Room approved, no action needed |
| ⚠️ MINOR_ISSUES | 75-89 | Review recommended, minor issues found |
| 🔍 REVIEW | 60-74 | Manual review required, significant differences |
| ❌ FAIL | 0-59 | Room does not meet standards, reject |

## 🎯 Best Practices

### Taking Reference Images
- ✅ Use consistent lighting
- ✅ Capture full room from center
- ✅ Ensure 1080p+ resolution
- ✅ Avoid motion blur
- ✅ Show all key areas

### Taking Inspection Images
- ✅ Match reference image angle
- ✅ Use similar lighting conditions
- ✅ Same room orientation
- ✅ Similar distance from objects
- ✅ Same time of day if possible

## 🛠️ Configuration

Edit `config.py` to adjust:
- Similarity score thresholds
- Blur and brightness sensitivity
- Change detection sensitivity

## ❓ Troubleshooting

### "Module not found" Error
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port 8000 already in use
```bash
# Use different port
python -m uvicorn app:app --port 8001
```

### Low similarity on good images
- Check image resolution
- Verify both images show same room
- Review lighting conditions
- Adjust thresholds in `config.py`

### Images won't upload
- Check file format (JPG, PNG, BMP, TIFF only)
- Verify file is not corrupted
- Check file size (max 50MB)

## 📚 Next Steps

1. **Test with sample images** - Place your room images and run /compare
2. **Adjust thresholds** - Edit `config.py` to match your requirements
3. **Build frontend** - Create web/mobile interface for image upload
4. **Add database** - Connect PostgreSQL for storing results
5. **Integrate webhooks** - Add notification system for results

## 📞 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /compare | Compare two room images |
| POST | /validate | Check single image quality |
| GET | /health | Check API status |
| GET | / | Get API info |

## 🔗 Links

- **OpenCV Docs**: https://docs.opencv.org/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SIFT Algorithm**: https://en.wikipedia.org/wiki/Scale-invariant_feature_transform

## 📦 Project Structure

```
app/
├── app.py              ← Main API server
├── image_compare.py    ← Image processing logic
├── config.py           ← Configuration settings
├── test_api.py         ← Test script
├── requirements.txt    ← Python packages
├── README.md           ← Full documentation
└── QUICKSTART.md       ← This file
```

---

Happy inspecting! 🎉
