from numpy import *
import cv2
import os
from config import Config
from .utils import ImageStitching

def stitch_images(images):
    """
    Main stitching function that processes multiple images into a panorama

    Args:
        images (list): List of OpenCV images (BGR format)

    Returns:
        tuple: (result_image, mapped_image) or (None, None) if failed
    """
    if not images or len(images) < 2:
        print("Need at least 2 images for stitching")
        return None, None

    try:
        print(f"Starting panorama stitching with {len(images)} images...")

        # Convert BGR to RGB for processing
        images_rgb = []
        for img in images:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images_rgb.append(img_rgb)

        # Use recursive stitching approach
        result, mapped_image = recurse_stitch(images_rgb, len(images_rgb))

        if result is not None:
            # Save intermediate results
            cv2.imwrite(os.path.join(Config.OUTPUT_DIR, Config.PANORAMA_FILENAME), result)
            if mapped_image is not None:
                cv2.imwrite(os.path.join(Config.OUTPUT_DIR, Config.MAPPED_FILENAME), mapped_image)

            print("✓ Panorama stitching completed successfully")
            return result, mapped_image
        else:
            print("✗ Panorama stitching failed")
            return None, None

    except Exception as e:
        print(f"✗ Error during stitching: {e}")
        return None, None


def forward_stitch(query_photo, train_photo):
    """
    Stitches two images together using SIFT features and homography

    Args:
        query_photo (numpy array): Left/query image (RGB)
        train_photo (numpy array): Right/train image (RGB)

    Returns:
        tuple: (result_image, mapped_feature_image)
    """
    try:
        image_stitching = ImageStitching(query_photo, train_photo)

        # Convert to grayscale
        _, query_photo_gray = image_stitching.give_gray(query_photo)
        _, train_photo_gray = image_stitching.give_gray(train_photo)

        # Detect SIFT features
        keypoints_train_image, features_train_image = image_stitching._sift_detector(train_photo_gray)
        keypoints_query_image, features_query_image = image_stitching._sift_detector(query_photo_gray)

        if features_train_image is None or features_query_image is None:
            print("Failed to detect features in one or both images")
            return None, None

        # Match keypoints
        matches = image_stitching.create_and_match_keypoints(features_train_image, features_query_image)

        if len(matches) < Config.MIN_MATCH_COUNT:
            print(f"Not enough matches found: {len(matches)} < {Config.MIN_MATCH_COUNT}")
            return None, None

        # Draw matches for visualization
        mapped_feature_image = cv2.drawMatches(
            train_photo, keypoints_train_image,
            query_photo, keypoints_query_image,
            matches[:100], None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )

        # Compute homography
        M = image_stitching.compute_homography(
            keypoints_train_image, keypoints_query_image, matches,
            reprojThresh=Config.REPROJ_THRESHOLD
        )

        if M is None:
            print("Failed to compute homography")
            return None, None

        (matches, homography_matrix, status) = M

        # Blend and stitch images
        result = image_stitching.blending_smoothing(query_photo, train_photo, homography_matrix)

        if result is None:
            print("Blending/smoothing failed")
            return None, None

        # Convert to proper format
        result_float32 = float32(result)
        mapped_float_32 = float32(mapped_feature_image)

        result_rgb = cv2.cvtColor(result_float32, cv2.COLOR_BGR2RGB)
        mapped_feature_image_rgb = cv2.cvtColor(mapped_float_32, cv2.COLOR_BGR2RGB)

        return result_rgb, mapped_feature_image_rgb

    except Exception as e:
        print(f"Error in forward_stitch: {e}")
        return None, None

def recurse_stitch(image_list, no_of_images):
    """
    Recursively stitch multiple images into a panorama

    Args:
        image_list (list): List of images to stitch
        no_of_images (int): Number of images

    Returns:
        tuple: (result_image, mapped_image)
    """
    if no_of_images == 2:
        result, mapped_image = forward_stitch(
            query_photo=image_list[no_of_images - 2],
            train_photo=image_list[no_of_images - 1],
        )
        return result, mapped_image

    elif no_of_images > 2:
        # Stitch the last two images
        result, _ = forward_stitch(
            query_photo=image_list[no_of_images - 2],
            train_photo=image_list[no_of_images - 1],
        )

        if result is None:
            print(f"Failed to stitch images at step {no_of_images}")
            return None, None

        # Convert result back to uint8 and RGB
        result_int8 = uint8(result)
        result_rgb = cv2.cvtColor(result_int8, cv2.COLOR_BGR2RGB)

        # Replace the second-to-last image with the stitched result
        image_list[no_of_images - 2] = result_rgb

        # Recursively stitch with remaining images
        return recurse_stitch(image_list, no_of_images - 1)

    else:
        print("Invalid number of images for stitching")
        return None, None
