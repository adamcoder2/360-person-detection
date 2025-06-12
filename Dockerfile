FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV (minimal)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgtk2.0-dev libgl1 \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose the port the Flask app runs on
EXPOSE 5001

# Run the app
CMD ["python", "run.py"]
