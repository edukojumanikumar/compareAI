"""
Image Comparison Engine
Handles image validation, alignment, comparison, and explainability outputs for room inspection
"""

import cv2
import numpy as np
import time
import uuid
from pathlib import Path
from typing import Dict, List, Tuple
import logging

import config

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

        self.blur_threshold = config.IMAGE_VALIDATION["blur_threshold"]
        self.brightness_min = config.IMAGE_VALIDATION["brightness_min"]
        self.brightness_max = config.IMAGE_VALIDATION["brightness_max"]
        self.pixel_diff_threshold = config.CHANGE_DETECTION["pixel_diff_threshold"]
        self.min_contour_area = config.MIN_CONTOUR_AREA
        self.morph_kernel_size = config.MORPH_KERNEL_SIZE
        self.overlay_alpha = config.OVERLAY_ALPHA
        self.bounding_box_color = config.BOUNDING_BOX_COLOR
        self.bounding_box_thickness = config.BOUNDING_BOX_THICKNESS

        self.output_dir = Path(config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
            aligned_insp, alignment_success = self.align_images(ref_img, insp_img)
            
            # Step 4: Compare images
            comparison_result = self.compare_aligned_images(ref_img, aligned_insp)
            
            # Step 5: Generate explainability outputs
            inspection_id = f"inspection_{int(time.time() * 1000)}"
            visual_outputs = self.generate_visual_outputs(
                ref_img,
                aligned_insp,
                comparison_result["diff_mask"],
                inspection_id
            )
            changed_regions = self.detect_changed_regions(comparison_result["diff_mask"])
            
            # Step 6: Generate result
            result = self.generate_result(
                comparison_result,
                changed_regions,
                visual_outputs,
                alignment_success
            )
            
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
            brightness = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2LAB)[:, :, 0])
            
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
            if height < config.IMAGE_VALIDATION["min_height"] or width < config.IMAGE_VALIDATION["min_width"]:
                issues.append("Image resolution is too low")
                recommendations.append("Use higher resolution camera")
                size_score = 50
            else:
                size_score = 100
            scores.append(size_score)
            
            # Calculate overall quality score
            quality_score = int(np.mean(scores))
            is_valid = quality_score >= config.IMAGE_VALIDATION["quality_threshold"] and len(issues) == 0
            
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
    
    def align_images(self, ref_img: np.ndarray, insp_img: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Align inspection image to reference image using feature matching
        
        Args:
            ref_img: Reference image
            insp_img: Inspection image
        
        Returns:
            Tuple of aligned inspection image and alignment success flag
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
                return insp_img, False
            
            # Match features
            matches = self.bf.knnMatch(des1, des2, k=2)
            
            # Apply Lowe's ratio test to filter good matches
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < config.COMPARISON["match_ratio_threshold"] * n.distance:
                        good_matches.append(m)
            
            logger.info(f"Total matches: {len(matches)}, Good matches after ratio test: {len(good_matches)}")
            
            if len(good_matches) < config.COMPARISON["min_matches"]:
                logger.warning(f"Not enough good matches found: {len(good_matches)}")
                return insp_img, False
            
            # Extract coordinates of good matches
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # Compute homography
            H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, config.COMPARISON["ransac_threshold"])
            
            if H is None:
                logger.warning("Could not compute homography")
                return insp_img, False
            
            logger.info("Homography computed successfully. Transforming image...")
            
            # Warp inspection image to align with reference
            aligned = cv2.warpPerspective(insp_img, H, (ref_w, ref_h))
            
            logger.info("Image alignment complete")
            return aligned, True
        
        except Exception as e:
            logger.error(f"Error aligning images: {str(e)}")
            return insp_img, False
    
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
            diff_per_channel = [float(diff[:, :, i].mean()) for i in range(3)]
            overall_diff = float(np.mean(diff_per_channel))
            
            # Generate difference mask and changed region mask
            diff_mask = self.generate_difference_mask(ref_img, aligned_insp)
            
            # Count changed pixels
            changed_pixels = int(np.count_nonzero(diff_mask))
            total_pixels = int(diff_mask.size)
            change_percentage = float((changed_pixels / total_pixels) * 100)
            
            # Compute structural similarity
            ssim = self._compute_ssim(cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY),
                                      cv2.cvtColor(aligned_insp, cv2.COLOR_BGR2GRAY))
            
            # Create a combined similarity score from SSIM and region change
            score_from_ssim = int(ssim * 100)
            score_from_change = max(0, int(100 - change_percentage * 0.2))
            similarity_score = int((score_from_ssim * 0.85) + (score_from_change * 0.15))
            
            return {
                "similarity_score": similarity_score,
                "overall_diff": overall_diff,
                "change_percentage": change_percentage,
                "diff_per_channel": diff_per_channel,
                "changed_pixels": changed_pixels,
                "total_pixels": total_pixels,
                "diff_mask": diff_mask
            }
        
        except Exception as e:
            logger.error(f"Error comparing images: {str(e)}")
            return {
                "similarity_score": 0,
                "overall_diff": 255.0,
                "change_percentage": 100.0,
                "diff_mask": np.ones((ref_img.shape[0], ref_img.shape[1]), dtype=np.uint8) * 255,
                "diff_per_channel": [255.0, 255.0, 255.0],
                "changed_pixels": int(ref_img.shape[0] * ref_img.shape[1]),
                "total_pixels": int(ref_img.shape[0] * ref_img.shape[1])
            }

    def generate_difference_mask(self, reference_img: np.ndarray, inspection_img: np.ndarray) -> np.ndarray:
        """
        Generate a normalized difference mask for explainability
        
        Args:
            reference_img: Reference image
            inspection_img: Inspection image
        
        Returns:
            Grayscale difference mask
        """
        # Convert to LAB color space for better perceptual difference
        lab_ref = cv2.cvtColor(reference_img, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab_insp = cv2.cvtColor(inspection_img, cv2.COLOR_BGR2LAB).astype(np.float32)

        # Compute Euclidean distance across LAB channels (approximate deltaE)
        delta = np.linalg.norm(lab_ref - lab_insp, axis=2)
        delta = cv2.GaussianBlur(delta, (5, 5), 0)
        delta_norm = cv2.normalize(delta, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Use SSIM map to suppress uniform illumination or texture differences
        gray_ref = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
        gray_insp = cv2.cvtColor(inspection_img, cv2.COLOR_BGR2GRAY)
        ssim_map = self._compute_ssim_map(gray_ref, gray_insp)
        ssim_diff = ((1.0 - ssim_map) * 255).astype(np.uint8)

        combined = cv2.addWeighted(delta_norm, 0.6, ssim_diff, 0.4, 0)

        # Adaptive threshold based on the strongest differences in the frame
        adaptive_threshold = int(np.percentile(combined.flatten(), 99.5))
        threshold_value = max(self.pixel_diff_threshold, adaptive_threshold)
        _, diff_mask = cv2.threshold(combined, threshold_value, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.morph_kernel_size, self.morph_kernel_size))
        diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_CLOSE, kernel)
        diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_OPEN, kernel)

        # Remove noise and keep only meaningful changed regions
        contours, _ = cv2.findContours(diff_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cleaned_mask = np.zeros_like(diff_mask)
        for contour in contours:
            if cv2.contourArea(contour) >= self.min_contour_area:
                cv2.drawContours(cleaned_mask, [contour], -1, 255, thickness=cv2.FILLED)

        if np.count_nonzero(cleaned_mask) > 0:
            return cleaned_mask

        return diff_mask
    
    def generate_heatmap(self, reference_img: np.ndarray, inspection_img: np.ndarray, output_path: str) -> str:
        """
        Generate a heatmap image showing differences between two images
        """
        diff_mask = self.generate_difference_mask(reference_img, inspection_img)
        heatmap = cv2.applyColorMap(diff_mask, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(reference_img, 0.6, heatmap, 0.4, 0)
        cv2.imwrite(output_path, overlay)
        return output_path
    
    def detect_changed_regions(self, diff_mask: np.ndarray) -> List[Dict]:
        """
        Detect changed regions and return bounding boxes
        """
        contours, _ = cv2.findContours(diff_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_contour_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            boxes.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "area": int(area)
            })

        boxes.sort(key=lambda item: item["area"], reverse=True)
        return boxes
    
    def generate_bounding_box_image(self, inspection_img: np.ndarray, bounding_boxes: List[Dict], output_path: str) -> str:
        """
        Generate an image with bounding boxes around changed regions
        
        Args:
            inspection_img: Aligned inspection image
            bounding_boxes: List of boxes to draw
            output_path: Output file path
        
        Returns:
            Path to saved bounding box image
        """
        image_with_boxes = inspection_img.copy()

        for box in bounding_boxes:
            top_left = (box["x"], box["y"])
            bottom_right = (box["x"] + box["width"], box["y"] + box["height"])
            cv2.rectangle(
                image_with_boxes,
                top_left,
                bottom_right,
                self.bounding_box_color,
                self.bounding_box_thickness
            )

        cv2.imwrite(output_path, image_with_boxes)
        return output_path
    
    def generate_overlay_image(self, inspection_img: np.ndarray, diff_mask: np.ndarray, bounding_boxes: List[Dict], output_path: str) -> str:
        """
        Generate a semi-transparent overlay image highlighting changed regions
        
        Args:
            inspection_img: Aligned inspection image
            diff_mask: Binary difference mask
            bounding_boxes: List of boxes to draw
            output_path: Output file path
        
        Returns:
            Path to saved overlay image
        """
        overlay = np.zeros_like(inspection_img)
        overlay[diff_mask > 0] = (0, 0, 255)

        blended = cv2.addWeighted(inspection_img, 1.0 - self.overlay_alpha, overlay, self.overlay_alpha, 0)

        for box in bounding_boxes:
            top_left = (box["x"], box["y"])
            bottom_right = (box["x"] + box["width"], box["y"] + box["height"])
            cv2.rectangle(
                blended,
                top_left,
                bottom_right,
                self.bounding_box_color,
                self.bounding_box_thickness
            )

        cv2.imwrite(output_path, blended)
        return output_path
    
    def generate_visual_outputs(self, reference_img: np.ndarray, inspection_img: np.ndarray, diff_mask: np.ndarray, inspection_id: str) -> Dict:
        """
        Create visual explainability outputs: heatmap, bounding boxes, overlay
        """
        heatmap_path = str(self.output_dir / f"{inspection_id}_heatmap.png")
        bounding_boxes_path = str(self.output_dir / f"{inspection_id}_bounding_boxes.png")
        overlay_path = str(self.output_dir / f"{inspection_id}_overlay.png")

        self.generate_heatmap(reference_img, inspection_img, heatmap_path)
        changed_regions = self.detect_changed_regions(diff_mask)
        self.generate_bounding_box_image(inspection_img, changed_regions, bounding_boxes_path)
        self.generate_overlay_image(inspection_img, diff_mask, changed_regions, overlay_path)

        return {
            "heatmap": heatmap_path,
            "bounding_boxes": bounding_boxes_path,
            "overlay": overlay_path
        }
    
    def _compute_ssim_map(self, img1: np.ndarray, img2: np.ndarray, window_size: int = 11) -> np.ndarray:
        """
        Compute SSIM map for two grayscale images
        """
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)

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
            (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
        )

        return np.clip(ssim_map, 0, 1)

    def _compute_ssim(self, img1: np.ndarray, img2: np.ndarray, window_size: int = 11) -> float:
        """
        Compute Structural Similarity Index (SSIM)
        """
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)

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
            (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
        )

        return float(np.clip(ssim_map.mean(), 0, 1))
    
    def generate_result(
        self,
        comparison_result: Dict,
        changed_regions: List[Dict],
        visual_outputs: Dict,
        alignment_success: bool
    ) -> Dict:
        """
        Generate final inspection result from comparison metrics
        """
        similarity_score = comparison_result.get("similarity_score", 0)
        change_percentage = comparison_result.get("change_percentage", 100)
        
        if similarity_score >= config.STATUS_THRESHOLDS["pass_threshold"]:
            status = "PASS"
            message = "Room inspection PASSED. Room is in expected condition."
        elif similarity_score >= config.STATUS_THRESHOLDS["minor_issues_threshold"]:
            status = "MINOR_ISSUES"
            message = "Minor issues detected. Room is mostly in expected condition but review recommended."
        elif similarity_score >= config.STATUS_THRESHOLDS["review_threshold"]:
            status = "REVIEW"
            message = "Significant differences detected. Manual review required."
        else:
            status = "FAIL"
            message = "Room inspection FAILED. Significant differences detected."

        issues = self._detect_issues(similarity_score, change_percentage)

        if changed_regions:
            issues.insert(0, f"Visible changes detected in {len(changed_regions)} regions")

        return {
            "score": similarity_score,
            "status": status,
            "message": message,
            "issues": issues,
            "visual_outputs": visual_outputs,
            "changed_regions": changed_regions,
            "metadata": {
                "changed_region_count": len(changed_regions),
                "pixel_change_percentage": round(change_percentage, 2),
                "alignment_success": alignment_success,
                "comparison_confidence": "MEDIUM"
            }
        }
    
    def _detect_issues(self, similarity_score: int, change_percentage: float) -> List[str]:
        """
        Detect generic issues based on comparison metrics
        """
        issues = []

        if change_percentage > config.CHANGE_DETECTION["major_change_threshold"]:
            issues.append("Major layout changes detected")
        elif change_percentage > config.CHANGE_DETECTION["moderate_change_threshold"]:
            issues.append("Moderate changes detected in room layout")

        if similarity_score < 70:
            issues.append("Significant visual differences from reference")

        if similarity_score < 50:
            issues.append("Room may not meet inspection standards")

        return issues if issues else ["No major issues detected"]
