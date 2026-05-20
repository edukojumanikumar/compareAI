"""
Room Inspection & Consistency Verification Platform - Backend API
Main FastAPI application entry point
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path

from image_compare import ImageComparator

# Initialize FastAPI app
app = FastAPI(
    title="Room Inspection API",
    description="AI-powered visual inspection platform for room consistency verification",
    version="0.1.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize image comparator
comparator = ImageComparator()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "operational",
        "service": "Room Inspection API",
        "version": "0.1.0"
    }


@app.post("/compare")
async def compare_images(
    reference_image: UploadFile = File(...),
    inspection_image: UploadFile = File(...)
):
    """
    Compare reference image with inspection image
    
    Args:
        reference_image: The reference/baseline image of the room
        inspection_image: The inspection image to compare against reference
    
    Returns:
        {
            "score": similarity_score (0-100),
            "status": "PASS" | "MINOR_ISSUES" | "REVIEW" | "FAIL",
            "message": human_readable_description,
            "issues": list of detected issues,
            "metadata": comparison metadata
        }
    """
    try:
        # Validate file types
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        ref_ext = Path(reference_image.filename).suffix.lower()
        insp_ext = Path(inspection_image.filename).suffix.lower()
        
        if ref_ext not in valid_extensions or insp_ext not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Supported: JPG, PNG, BMP, TIFF"
            )
        
        # Save temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            ref_path = Path(temp_dir) / reference_image.filename
            insp_path = Path(temp_dir) / inspection_image.filename
            
            # Write uploaded files
            ref_content = await reference_image.read()
            insp_content = await inspection_image.read()
            
            ref_path.write_bytes(ref_content)
            insp_path.write_bytes(insp_content)
            
            # Perform comparison
            result = comparator.compare(str(ref_path), str(insp_path))
            
            return JSONResponse(content=result, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            content={
                "error": str(e),
                "message": "Error processing images"
            },
            status_code=500
        )


@app.post("/validate")
async def validate_image(image: UploadFile = File(...)):
    """
    Validate a single image for quality issues
    
    Checks for:
    - Blur detection
    - Brightness validation
    - Framing checks
    
    Returns:
        {
            "is_valid": bool,
            "quality_score": 0-100,
            "issues": list of detected issues,
            "recommendations": list of improvement suggestions
        }
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            img_path = Path(temp_dir) / image.filename
            img_content = await image.read()
            img_path.write_bytes(img_content)
            
            result = comparator.validate_image(str(img_path))
            return JSONResponse(content=result, status_code=200)
    
    except Exception as e:
        return JSONResponse(
            content={
                "error": str(e),
                "message": "Error validating image"
            },
            status_code=500
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Room Inspection API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
