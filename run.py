from app import create_app
from config import Config
import person_detection
import os

os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

app = create_app()

if __name__ == "__main__":
    print(f"Starting 360 Person Detection server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Configured for {len(Config.RASPBERRY_PI_IPS)} Raspberry Pi devices")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.DEBUG)
