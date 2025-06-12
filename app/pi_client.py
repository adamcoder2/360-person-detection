import requests
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from config import Config


def fetch_images():
    """Fetch images from all configured Raspberry Pi devices"""
    images = []
    successful_fetches = 0

    print(f"Fetching images from {len(Config.RASPBERRY_PI_IPS)} Raspberry Pi devices...")

    for i, ip in enumerate(Config.RASPBERRY_PI_IPS):
        try:
            print(f"Fetching image {i + 1}/{len(Config.RASPBERRY_PI_IPS)} from {ip}")
            url = f"http://{ip}:8080{Config.CAPTURE_ENDPOINT}"
            response = requests.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()

            # Convert PIL image to OpenCV format (BGR)
            img = Image.open(BytesIO(response.content))
            img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            images.append(img_np)
            successful_fetches += 1
            print(f"✓ Successfully fetched from {ip} - Image shape: {img_np.shape}")

        except requests.exceptions.Timeout:
            print(f"✗ Timeout fetching from {ip}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error fetching from {ip}: {e}")
        except Exception as e:
            print(f"✗ Error processing image from {ip}: {e}")

    print(f"Successfully fetched {successful_fetches}/{len(Config.RASPBERRY_PI_IPS)} images")
    return images


def validate_images(images):
    """Validate that we have the expected number of images"""
    if len(images) != Config.EXPECTED_IMAGE_COUNT:
        return False

    # Additional validation - check if images have reasonable dimensions
    for i, img in enumerate(images):
        if img is None or len(img.shape) != 3:
            print(f"Invalid image at index {i}")
            return False
        if img.shape[0] < 100 or img.shape[1] < 100:
            print(f"Image {i} too small: {img.shape}")
            return False

    return True


def check_pi_status():
    """Check the status of all configured Raspberry Pi devices"""
    pi_status = []
    for ip in Config.RASPBERRY_PI_IPS:
        try:
            response = requests.get(f"http://{ip}:8080/status", timeout=3)
            pi_status.append({
                "ip": ip,
                "status": "online",
                "response_time": response.elapsed.total_seconds()
            })
        except:
            pi_status.append({"ip": ip, "status": "offline"})

    return pi_status
