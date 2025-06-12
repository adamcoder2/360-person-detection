from flask import Blueprint, send_file, jsonify, request
from .pi_client import fetch_images, validate_images, check_pi_status
from .stitching import stitch_images
from .utils import cleanup_old_files
from config import Config
import cv2
import os
import time

bp = Blueprint('main', __name__)

@bp.route("/", methods=["GET"])
def index():
    """Health check endpoint"""
    return jsonify({
        "service": "360 Person Detection System",
        "status": "running",
        "configured_pis": len(Config.RASPBERRY_PI_IPS),
        "expected_images": Config.EXPECTED_IMAGE_COUNT,
        "endpoints": ["/", "/stitch", "/status", "/health"]
    })


@bp.route("/stitch", methods=["POST"])
def stitch_endpoint():
    """Main endpoint for creating panoramas"""
    start_time = time.time()

    try:
        # Clean up old files first
        cleanup_old_files()

        print("=== Starting Panorama Stitching Process ===")

        # Fetch images from all Raspberry Pi devices
        images = fetch_images()

        # Validate we have the expected number of images
        if not validate_images(images):
            return jsonify({
                "error": f"Expected {Config.EXPECTED_IMAGE_COUNT} valid images, got {len(images)}",
                "details": "Check Raspberry Pi connections and image quality"
            }), 400

        print(f"✓ All {len(images)} images validated successfully")

        # Stitch the images
        pano, mapped_image = stitch_images(images)

        if pano is not None:
            # Save the final panorama
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{Config.FINAL_PANO_FILENAME}"
            filepath = os.path.join(Config.OUTPUT_DIR, filename)

            # Convert RGB back to BGR for saving
            pano_bgr = cv2.cvtColor(pano.astype(np.uint8), cv2.COLOR_RGB2BGR)
            cv2.imwrite(filepath, pano_bgr)

            processing_time = time.time() - start_time
            print(f"✓ Panorama created successfully in {processing_time:.2f} seconds")

            # Return the image file
            return send_file(
                filepath,
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({
                "error": "Panorama stitching failed",
                "details": "Check image overlap and quality"
            }), 500

    except Exception as e:
        processing_time = time.time() - start_time
        print(f"✗ Stitching failed after {processing_time:.2f} seconds: {e}")
        return jsonify({
            "error": f"Unexpected error during stitching: {str(e)}",
            "processing_time": processing_time
        }), 500


@bp.route("/status", methods=["GET"])
def status_endpoint():
    """Check the status of connected Raspberry Pi devices"""
    pi_status = check_pi_status()
    online_count = len([pi for pi in pi_status if pi["status"] == "online"])

    return jsonify({
        "raspberry_pis": pi_status,
        "total_configured": len(Config.RASPBERRY_PI_IPS),
        "online_count": online_count,
        "expected_images": Config.EXPECTED_IMAGE_COUNT,
        "system_ready": online_count >= Config.EXPECTED_IMAGE_COUNT
    })


@bp.route("/health", methods=["GET"])
def health_endpoint():
    """Detailed health check"""
    try:
        # Check if output directory exists
        output_dir_exists = os.path.exists(Config.OUTPUT_DIR)

        # Check Pi status
        pi_status = check_pi_status()
        online_count = len([pi for pi in pi_status if pi["status"] == "online"])

        health_status = {
            "status": "healthy" if online_count >= Config.EXPECTED_IMAGE_COUNT and output_dir_exists else "degraded",
            "output_directory": output_dir_exists,
            "raspberry_pis": {
                "total": len(Config.RASPBERRY_PI_IPS),
                "online": online_count,
                "required": Config.EXPECTED_IMAGE_COUNT
            },
            "configuration": {
                "smoothing_window_percent": Config.SMOOTHING_WINDOW_PERCENT,
                "min_match_count": Config.MIN_MATCH_COUNT,
                "reproj_threshold": Config.REPROJ_THRESHOLD
            }
        }

        return jsonify(health_status)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
