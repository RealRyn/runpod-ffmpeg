FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install RunPod SDK
RUN pip install runpod

# Copy handler
COPY handler.py /handler.py

# Set the entrypoint
CMD ["python", "-u", "/handler.py"]
