"""
Configuration file for Room Inspection API
Adjust these settings based on your requirements
"""

# Image Quality Validation Settings
IMAGE_VALIDATION = {
    "blur_threshold": 100,  # Laplacian variance threshold for blur detection
    "brightness_min": 30,   # Minimum brightness (0-255 LAB scale)
    "brightness_max": 225,  # Maximum brightness (0-255 LAB scale)
    "min_width": 640,       # Minimum image width
    "min_height": 480,      # Minimum image height
    "quality_threshold": 70  # Minimum quality score (0-100)
}

# Image Comparison Settings
COMPARISON = {
    "feature_matcher": "SIFT",  # Feature detection method (SIFT recommended)
    "match_ratio_threshold": 0.75,  # Lowe's ratio test threshold
    "min_matches": 4,           # Minimum matches required for homography
    "ransac_threshold": 5.0,    # RANSAC threshold for homography
    "ssim_window_size": 11      # Window size for SSIM calculation
}

# Threshold Settings for Status Determination
STATUS_THRESHOLDS = {
    "pass_threshold": 90,         # PASS if score >= 90
    "minor_issues_threshold": 60, # MINOR_ISSUES if >= 60 (lowered from 75)
    "review_threshold": 40,       # REVIEW if >= 40 (lowered from 60)
}

# Change Detection Settings
CHANGE_DETECTION = {
    "major_change_threshold": 40,    # Percentage - major layout changes
    "moderate_change_threshold": 20, # Percentage - moderate changes
    "pixel_diff_threshold": 30       # Pixel value difference threshold
}

# API Settings
API = {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 1,
    "reload": True
}

# File Upload Settings
UPLOAD = {
    "max_file_size_mb": 50,
    "allowed_extensions": {".jpg", ".jpeg", ".png", ".bmp", ".tiff"},
    "upload_dir": "uploads/"
}

# Logging
LOGGING = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
