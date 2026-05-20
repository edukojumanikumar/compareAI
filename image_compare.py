"""
Image Comparison Engine
Handles image validation, alignment, and comparison for room inspection
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageComparator:
    """
    Main class for comparing reference and inspection room images
    """
    
    def __init__(self):
        """Initialize the image comparator with default parameters"""
        self.sift = cv2.SIFT_create()
        self.bf = cv2.BFMatcher()
        self.blur_threshold = 100
        self.brightness_min = 30
        self.brightness_max = 225
        
    def compare(self, reference_path: str, inspection_path: str) -> Dict:
        """
        Main comparison workflow
        
        Args:
            reference_path: Path to reference image
            inspection_path: Path to inspection image
        
        Returns:
            Dict with comparison results
        """
        try:
            # Step 1: Load images
            ref_img = cv2.imread(reference_path)
            insp_img = cv2.imread(inspection_path)
            
            if ref_img is None or insp_img is None:
                return {
                    "error": "Could not load images",
                    "score": 0,
                    "status": "FAIL",
                    "message": "One or both images could not be loaded"
                }
            
            # Step 2: Validate image quality
            ref_quality = self.validate_image(reference_path)
            insp_quality = self.validate_image(inspection_path)
            
            if not ref_quality["is_valid"] or not insp_quality["is_valid"]:
                return {
                    "error": "Image quality issues detected",
                    "score": 0,
                    "status": "FAIL",
                    "message": "One or both images have quality issues",
                    "reference_quality": ref_quality,
                    "inspection_quality": insp_quality
                }
            
            # Step 3: Align images
            aligned_insp = self.align_images(ref_img, insp_img)
            
            # Step 4: Compare images
            comparison_result = self.compare_aligned_images(ref_img, aligned_insp)
            
            # Step 5: Generate result
            result = self.generate_result(comparison_result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error in comparison: {str(e)}")
            return {
                "error": str(e),
                "score": 0,
                "status": "FAIL",
                "message": "Error during image comparison"
            }
    
    def validate_image(self, image_path: str) -> Dict:
        """
        Validate single image quality
        
        Checks for:
        - Blur detection
        - Brightness validation
        - Size validation
        
        Returns:
            Dict with validation results
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {
                    "is_valid": False,
                    "quality_score": 0,
                    "issues": ["Could not load image"],
                    "recommendations": ["Check file format and integrity"]
                }
            
            issues = []
            recommendations = []
            scores = []
            
            # Check for blur
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var < self.blur_threshold:
                issues.append("Image appears blurry")
                recommendations.append("Retake photo with better focus")
                blur_score = max(0, (laplacian_var / self.blur_threshold) * 100)
            else:
                blur_score = 100
            scores.append(blur_score)
            
            # Check brightness
            brightness = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2LAB)[:,:,0])
            
            if brightness < self.brightness_min:
                issues.append("Image is too dark")
                recommendations.append("Improve lighting or increase brightness")
                brightness_score = (brightness / self.brightness_min) * 100
            elif brightness > self.brightness_max:
                issues.append("Image is too bright")
                recommendations.append("Reduce exposure or lighting")
                brightness_score = ((255 - brightness) / (255 - self.brightness_max)) * 100
            else:
                brightness_score = 100
            scores.append(brightness_score)
            
            # Check image size
            height, width = img.shape[:2]
            if height < 480 or width < 640:
                issues.append("Image resolution is too low")
                recommendations.append("Use higher resolution camera")
                size_score = 50
            else:
                size_score = 100
            scores.append(size_score)
            
            # Calculate overall quality score
            quality_score = int(np.mean(scores))
            is_valid = quality_score >= 70 and len(issues) == 0
            
            return {
                "is_valid": is_valid,
                "quality_score": quality_score,
                "blur_score": int(blur_score),
                "brightness_score": int(brightness_score),
                "size_score": size_score,
                "issues": issues,
                "recommendations": recommendations
            }
        
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            return {
                "is_valid": False,
                "quality_score": 0,
                "issues": [str(e)],
                "recommendations": ["Check image file"]
            }
    
    def align_images(self, ref_img: np.ndarray, insp_img: np.ndarray) -> np.ndarray:
        """
        Align inspection image to reference image using feature matching
        
        Args:
            ref_img: Reference image
            insp_img: Inspection image
        
        Returns:
            Aligned inspection image
        """
        try:
            # Resize images to be similar size for faster processing
            ref_h, ref_w = ref_img.shape[:2]
            insp_h, insp_w = insp_img.shape[:2]
            
            if insp_h != ref_h or insp_w != ref_w:
                insp_img = cv2.resize(insp_img, (ref_w, ref_h), interpolation=cv2.INTER_AREA)
            
            # Convert to grayscale for feature detection
            ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
            insp_gray = cv2.cvtColor(insp_img, cv2.COLOR_BGR2GRAY)
            
            # Detect and compute features
            kp1, des1 = self.sift.detectAndCompute(ref_gray, None)
            kp2, des2 = self.sift.detectAndCompute(insp_gray, None)
            
            logger.info(f"Reference keypoints: {len(kp1) if kp1 else 0}, Inspection keypoints: {len(kp2) if kp2 else 0}")
            
            if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
                logger.warning(f"Not enough features found for alignment - Ref: {len(kp1) if kp1 else 0}, Insp: {len(kp2) if kp2 else 0}")
                return insp_img
            
            # Match features
            matches = self.bf.knnMatch(des1, des2, k=2)
            
            # Apply Lowe's ratio test to filter good matches
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)
            
            logger.info(f"Total matches: {len(matches)}, Good matches after ratio test: {len(good_matches)}")
            
            if len(good_matches) < 4:
                logger.warning(f"Not enough good matches found: {len(good_matches)}")
                return insp_img
            
            # Extract coordinates of good matches
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # Compute homography
            H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
            
            if H is None:
                logger.warning("Could not compute homography")
                return insp_img
            
            logger.info(f"Homography computed successfully. Transforming image...")
            
            # Warp inspection image to align with reference
            aligned = cv2.warpPerspective(insp_img, H, (ref_w, ref_h))
            
            logger.info("Image alignment complete")
            return aligned
        
        except Exception as e:
            logger.error(f"Error aligning images: {str(e)}")
            return insp_img
    
    def compare_aligned_images(self, ref_img: np.ndarray, aligned_insp: np.ndarray) -> Dict:
        """
        Compare aligned images using structural similarity and difference detection
        
        Args:
            ref_img: Reference image
            aligned_insp: Aligned inspection image
        
        Returns:
            Dict with comparison metrics
        """
        try:
            # Convert to LAB color space for better comparison
            ref_lab = cv2.cvtColor(ref_img, cv2.COLOR_BGR2LAB)
            insp_lab = cv2.cvtColor(aligned_insp, cv2.COLOR_BGR2LAB)
            
            # Compute difference
            diff = cv2.absdiff(ref_lab, insp_lab)
            
            # Calculate mean difference per channel
            diff_per_channel = [diff[:,:,i].mean() for i in range(3)]
            overall_diff = np.mean(diff_per_channel)
            
            # Detect significant change regions using L (lightness) channel
            # Take the L channel (first channel) from LAB diff
            gray_diff = diff[:,:,0].astype(np.uint8)
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Count changed pixels
            changed_pixels = np.count_nonzero(thresh)
            total_pixels = thresh.size
            change_percentage = (changed_pixels / total_pixels) * 100
            
            # Compute structural similarity
            ssim = self._compute_ssim(cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY),
                                      cv2.cvtColor(aligned_insp, cv2.COLOR_BGR2GRAY))
            
            # Normalize similarity to 0-100 scale
            similarity_score = int(ssim * 100)
            
            return {
                "similarity_score": similarity_score,
                "overall_diff": float(overall_diff),
                "change_percentage": float(change_percentage),
                "diff_per_channel": diff_per_channel,
                "changed_pixels": int(changed_pixels),
                "total_pixels": int(total_pixels)
            }
        
        except Exception as e:
            logger.error(f"Error comparing images: {str(e)}")
            return {
                "similarity_score": 0,
                "overall_diff": 255.0,
                "change_percentage": 100.0
            }
    
    def _compute_ssim(self, img1: np.ndarray, img2: np.ndarray, window_size: int = 11) -> float:
        """
        Compute Structural Similarity Index (SSIM)
        
        Args:
            img1: First image
            img2: Second image
            window_size: Size of the window for SSIM calculation
        
        Returns:
            SSIM value between 0 and 1
        """
        try:
            # Ensure images are uint8
            img1 = img1.astype(np.float64)
            img2 = img2.astype(np.float64)
            
            # Create Gaussian kernel
            kernel = cv2.getGaussianKernel(window_size, 1.5)
            kernel = kernel @ kernel.T
            
            mu1 = cv2.filter2D(img1, -1, kernel)
            mu2 = cv2.filter2D(img2, -1, kernel)
            
            mu1_sq = mu1 ** 2
            mu2_sq = mu2 ** 2
            mu1_mu2 = mu1 * mu2
            
            sigma1_sq = cv2.filter2D(img1 ** 2, -1, kernel) - mu1_sq
            sigma2_sq = cv2.filter2D(img2 ** 2, -1, kernel) - mu2_sq
            sigma12 = cv2.filter2D(img1 * img2, -1, kernel) - mu1_mu2
            
            C1 = 6.5025
            C2 = 58.5225
            
            ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / (
                (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
            
            return float(ssim_map.mean())
        
        except Exception as e:
            logger.error(f"Error computing SSIM: {str(e)}")
            return 0.0
    
    def generate_result(self, comparison_result: Dict) -> Dict:
        """
        Generate final inspection result from comparison metrics
        
        Args:
            comparison_result: Raw comparison metrics
        
        Returns:
            Formatted inspection result
        """
        similarity_score = comparison_result.get("similarity_score", 0)
        change_percentage = comparison_result.get("change_percentage", 100)
        
        # Determine status
        if similarity_score >= 90:
            status = "PASS"
            message = "Room inspection PASSED. Room is in expected condition."
        elif similarity_score >= 75:
            status = "MINOR_ISSUES"
            message = "Minor issues detected. Room is mostly in expected condition but review recommended."
        elif similarity_score >= 60:
            status = "REVIEW"
            message = "Significant differences detected. Manual review required."
        else:
            status = "FAIL"
            message = "Room inspection FAILED. Significant differences detected."
        
        # Detect generic issues based on change percentage
        issues = self._detect_issues(similarity_score, change_percentage)
        
        return {
            "score": similarity_score,
            "status": status,
            "message": message,
            "issues": issues,
            "metadata": {
                "change_percentage": round(change_percentage, 2),
                "comparison_confidence": "MEDIUM"
            }
        }
    
    def _detect_issues(self, similarity_score: int, change_percentage: float) -> List[str]:
        """
        Detect generic issues based on comparison metrics
        
        Args:
            similarity_score: Overall similarity score
            change_percentage: Percentage of pixels that changed
        
        Returns:
            List of detected issues
        """
        issues = []
        
        if change_percentage > 40:
            issues.append("Major layout changes detected")
        elif change_percentage > 20:
            issues.append("Moderate changes detected in room layout")
        
        if similarity_score < 70:
            issues.append("Significant visual differences from reference")
        
        if similarity_score < 50:
            issues.append("Room may not meet inspection standards")
        
        return issues if issues else ["No major issues detected"]
