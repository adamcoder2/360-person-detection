from io import BytesIO

import requests
from flask import Flask, request
import base64
import cv2
import numpy as np
import os
from datetime import datetime
from PIL import Image

app = Flask(__name__)
os.makedirs("received_images", exist_ok=True)

RASPBERRY_PI_IPS = [
    '192.168.1.101',
    '192.168.1.102',
    '192.168.1.103',
    '192.168.1.104',
    '192.168.1.105',
    '192.168.1.106',
    '192.168.1.107',
    '192.168.1.108',
]

def fetch_images():
    images = []
    for ip in RASPBERRY_PI_IPS:
        try:
            print(f"Requesting image from {ip}")
            response = requests.get(f"http://{ip}:8080/capture", timeout=5)
            img = Image.open(BytesIO(response.content))
            img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            images.append(img_np)
        except Exception as e:
            print(f"Error fetching from {ip}: {e}")
    return images

@app.route("/stitch", methods=["POST"])
def stitch_endpoint():
    images = fetch_images()
    if len(images) == 8:
        pano = stitch_images(images)
        if pano is not None:
            cv2.imwrite("final_pano.jpg", pano)
            return send_file("final_pano.jpg", mimetype='image/jpeg')
    return "Failed", 500


# @app.route('/upload', methods=['POST'])
# def upload():
#     try:
#         data = request.json
#         cam_id = data['camera_id']
#         timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#         image_b64 = data['image']
#
#
#         #Decode Image
#         img_data = base64.b64decode(image_b64)
#         nparr = np.frombuffer(img_data, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#         filename = f"received_images/cam_{cam_id}_{timestamp}.jpg"
#         cv2.imwrite(filename, img)
#         print(f"Image saved: {filename}")
#         return {'status': 'success'}
#     except Exception as e:
#         print(f"Error: {e}")
#         return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)  # Accessible to Pis over local network
