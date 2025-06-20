import cv2
import os
from app.stitching import stitch_images

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_images_dir = os.path.join(BASE_DIR, "test_images")
image_filenames = [
"room01.jpeg",
"room02.jpeg",
]

# Load images
images = []
for filename in image_filenames:
    img_path = os.path.join(test_images_dir, filename)
    img = cv2.imread(img_path)
    if img is not None:
        images.append(img)
    else:
        print(f"Failed to load {filename}")

# Run stitching
if images:
    pano, mapped_image = stitch_images(images)
    if pano is not None:
        cv2.imwrite("panorama_result.jpg", cv2.cvtColor(pano, cv2.COLOR_RGB2BGR))
        print("✓ Panorama stitched and saved to panorama_result.jpg")
    else:
        print("✗ Stitching failed")
else:
    print("No images loaded.")
