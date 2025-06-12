
# 📷 360° Person Detection System

This project captures synchronized images from 8 Raspberry Pi cameras positioned in a circle, stitches them into a 360° panoramic view, and serves the final stitched image via a Flask API. Built with Python, OpenCV, and Docker.

---

## 🧩 Features

- 📡 Capture images from 8 Raspberry Pi nodes over the network
- 🧵 Stitch the images into a panoramic scene
- 🔌 Flask API to trigger stitching and retrieve the final image
- 🐳 Dockerized for portable deployment

---

## 🖼️ Architecture Overview

```
+-------------+      +-------------+      +-------------+
|   Pi Cam 1  | ---> |             |      |             |
|   Pi Cam 2  | ---> |  Flask API  | ---> | Final Pano  |
|   Pi Cam 3  | ---> | (Main PC)   |      |   Output    |
|     ...     |      |             |      |             |
|   Pi Cam 8  | ---> |             |      |             |
+-------------+      +-------------+      +-------------+
```

---

## 🛠️ Tech Stack

- Python
- OpenCV
- Flask
- Docker
- Raspberry Pi (8 nodes)
- HTTP/REST (for image capture)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/360-person-detection.git
cd 360-person-detection
```

### 2. Configure Raspberry Pi IPs

Edit `app/pi_client.py` and update:

```python
RASPBERRY_PI_IPS = [
    '192.168.1.101',
    '192.168.1.102',
    ...
]
```

Ensure each Pi is hosting a `/capture` endpoint that returns a JPEG image.

---

### 3. Run with Docker

```bash
docker build -t panorama-server .
docker run -p 5001:5001 panorama-server
```

---

### 4. Access the API

To trigger stitching and get the result:

```bash
curl -X POST http://<YOUR_MAC_IP>:5001/stitch --output final_pano.jpg
```
---

## 📄 License

[MIT License](LICENSE)

