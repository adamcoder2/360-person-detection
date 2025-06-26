import cv2
from numpy import *
from config import Config

class ImageStitching:
    """Contains the utilities required to stitch images"""

    def __init__(self, query_photo, train_photo):
        """
        Initialize ImageStitching with two photos

        Args:
            query_photo (numpy array): Query/left image
            train_photo (numpy array): Train/right image
        """
        super().__init__()
        width_query_photo = query_photo.shape[1]
        width_train_photo = train_photo.shape[1]
        lowest_width = min(width_query_photo, width_train_photo)

        # Calculate smoothing window size
        self.smoothing_window_size = max(
            100,
            min(Config.SMOOTHING_WINDOW_PERCENT * lowest_width, 1000)
        )
        print(f"Smoothing window size: {self.smoothing_window_size}")

    def give_gray(self, image):
        """
        Convert image to grayscale

        Args:
            image (numpy array): Input image

        Returns:
            tuple: (original_image, grayscale_image)
        """
        if len(image.shape) == 3:
            photo_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            photo_gray = image
        return image, photo_gray

    @staticmethod
    def _sift_detector(image):
        """
        Apply SIFT algorithm to detect keypoints and features

        Args:
            image (numpy array): Input grayscale image

        Returns:
            tuple: (keypoints, features)
        """
        try:
            descriptor = cv2.SIFT_create()
            keypoints, features = descriptor.detectAndCompute(image, None)

            if keypoints is None or features is None:
                print("SIFT detection failed")
                return None, None

            print(f"Found {len(keypoints)} keypoints")
            return keypoints, features

        except Exception as e:
            print(f"Error in SIFT detection: {e}")
            return None, None

    def create_and_match_keypoints(self, features_train_image, features_query_image):
        """
        Create and match keypoints using Brute Force matcher

        Args:
            features_train_image: SIFT features of train image
            features_query_image: SIFT features of query image

        Returns:
            list: Sorted matches
        """
        try:
            bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
            best_matches = bf.match(features_train_image, features_query_image)
            raw_matches = sorted(best_matches, key=lambda x: x.distance)

            print(f"Found {len(raw_matches)} matches")
            return raw_matches

        except Exception as e:
            print(f"Error in keypoint matching: {e}")
            return []

    def compute_homography(self, keypoints_train_image, keypoints_query_image, matches, reprojThresh):
        """
        Compute homography matrix using RANSAC

        Args:
            keypoints_train_image: Keypoints from train image
            keypoints_query_image: Keypoints from query image
            matches: Feature matches
            reprojThresh: RANSAC reprojection threshold

        Returns:
            tuple: (matches, homography_matrix, status) or None
        """
        try:
            keypoints_train_image = float32([kp.pt for kp in keypoints_train_image])
            keypoints_query_image = float32([kp.pt for kp in keypoints_query_image])

            if len(matches) >= Config.MIN_MATCH_COUNT:
                points_train = float32([keypoints_train_image[m.queryIdx] for m in matches])
                points_query = float32([keypoints_query_image[m.trainIdx] for m in matches])

                H, status = cv2.findHomography(
                    points_train, points_query, cv2.RANSAC, reprojThresh
                )

                if H is not None:
                    print("✓ Homography computed successfully")
                    return (matches, H, status)
                else:
                    print("✗ Failed to compute homography")
                    return None
            else:
                print(f"✗ Insufficient matches: {len(matches)} < {Config.MIN_MATCH_COUNT}")
                return None

        except Exception as e:
            print(f"Error computing homography: {e}")
            return None

    def create_mask(self, query_image, train_image, version):
        """
        Create blending mask for seamless stitching

        Args:
            query_image (numpy array): Query image
            train_image (numpy array): Train image
            version (str): 'left_image' or 'right_image'

        Returns:
            numpy array: Blending mask
        """
        try:
            height_query_photo = query_image.shape[0]
            width_query_photo = query_image.shape[1]
            width_train_photo = train_image.shape[1]
            height_panorama = height_query_photo
            width_panorama = width_query_photo + width_train_photo

            offset = int(self.smoothing_window_size / 2)
            barrier = query_image.shape[1] - int(self.smoothing_window_size / 2)
            mask = zeros((height_panorama, width_panorama))

            if version == "left_image":
                mask[:, barrier - offset: barrier + offset] = tile(
                    linspace(1, 0, 2 * offset).T, (height_panorama, 1)
                )
                mask[:, : barrier - offset] = 1
            else:
                mask[:, barrier - offset: barrier + offset] = tile(
                    linspace(0, 1, 2 * offset).T, (height_panorama, 1)
                )
                mask[:, barrier + offset:] = 1

            return cv2.merge([mask, mask, mask])

        except Exception as e:
            print(f"Error creating mask: {e}")
            return None

    def blending_smoothing(self, query_image, train_image, homography_matrix):
        """
        Blend images using homography transformation and masks

        Args:
            query_image (numpy array): Query image
            train_image (numpy array): Train image
            homography_matrix (numpy array): Homography transformation matrix

        Returns:
            numpy array: Blended panoramic image
        """
        try:
            height_img1 = query_image.shape[0]
            width_img1 = query_image.shape[1]
            width_img2 = train_image.shape[1]
            height_panorama = height_img1
            width_panorama = width_img1 + width_img2

            # Create panorama canvas
            panorama1 = zeros((height_panorama, width_panorama, 3))

            # Create masks
            mask1 = self.create_mask(query_image, train_image, version="left_image")
            mask2 = self.create_mask(query_image, train_image, version="right_image")

            if mask1 is None or mask2 is None:
                print("Failed to create masks")
                return None

            # Place first image
            panorama1[0:query_image.shape[0], 0:query_image.shape[1], :] = query_image
            panorama1 *= mask1

            # Warp and place second image
            panorama2 = cv2.warpPerspective(
                train_image, homography_matrix, (width_panorama, height_panorama)
            ) * mask2

            # Blend images
            result = panorama1 + panorama2

            # Crop out black borders
            rows, cols = where(result[:, :, 0] != 0)
            if len(rows) > 0 and len(cols) > 0:
                min_row, max_row = min(rows), max(rows) + 1
                min_col, max_col = min(cols), max(cols) + 1
                final_result = result[min_row:max_row, min_col:max_col, :]
            else:
                final_result = result

            return final_result

        except Exception as e:
            print(f"Error in blending/smoothing: {e}")
            return None

def cleanup_old_files(max_age_hours=24):
    """Clean up old panorama files"""
    import os
    import time

    current_time = time.time()

    for filename in os.listdir(Config.OUTPUT_DIR):
        if filename.endswith('.jpg'):
            filepath = os.path.join(Config.OUTPUT_DIR, filename)
            file_time = os.path.getmtime(filepath)
            if (current_time - file_time) > (max_age_hours * 3600):
                try:
                    os.remove(filepath)
                    print(f"Cleaned up old file: {filename}")
                except OSError:
                    pass

