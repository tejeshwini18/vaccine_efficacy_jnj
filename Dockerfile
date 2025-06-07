# Use Python 3.9 as base image
FROM python:3.9-slim

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set Tesseract path
ENV TESSERACT_CMD=/usr/bin/tesseract

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p Upload_Folder/debug_images

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "new_backend/zipped_extraction.py"] 