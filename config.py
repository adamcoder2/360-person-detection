class Config:
    """Configuration settings for the 360 person detection application"""
    # Raspberry Pi IP addresses
    RASPBERRY_PI_IPS = [
        # Add your Raspberry Pi IP addresses here
        # "192.168.1.100",
        # "192.168.1.101",
        # "192.168.1.102",
        # "192.168.1.103",
        # "192.168.1.104",
        # "192.168.1.105",
        # "192.168.1.106",
        # "192.168.1.107",
    ]

    # Flask settings
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5001
    DEBUG = False

    # Image capture settings
    REQUEST_TIMEOUT = 10
    CAPTURE_ENDPOINT = "/capture"
    EXPECTED_IMAGE_COUNT = 8

    # Stitching settings
    SMOOTHING_WINDOW_PERCENT = 0.10
    MIN_MATCH_COUNT = 4
    REPROJ_THRESHOLD = 4.0

    # Output settings
    OUTPUT_DIR = "outputs"
    PANORAMA_FILENAME = "panorama_image.jpg"
    MAPPED_FILENAME = "mapped_image.jpg"
    FINAL_PANO_FILENAME = "final_pano.jpg"

