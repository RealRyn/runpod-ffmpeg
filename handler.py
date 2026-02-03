import runpod
import subprocess
import base64
import os
import tempfile
import urllib.request
from typing import List, Dict, Any

def download_video(url: str, output_path: str) -> bool:
    """Download video from URL."""
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def extract_frame(video_path: str, timestamp: float, output_path: str, width: int = 640, height: int = 360) -> bool:
    """Extract a single frame from video at given timestamp."""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-vf', f'scale={width}:{height}',
            '-q:v', '2',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"FFmpeg error at {timestamp}s: {e}")
        return False

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """Main handler for RunPod serverless."""
    job_input = job.get("input", {})
    
    video_url = job_input.get("video_url")
    timestamps = job_input.get("timestamps", [])
    output_width = job_input.get("output_width", 640)
    output_height = job_input.get("output_height", 360)
    
    if not video_url:
        return {"error": "video_url is required"}
    
    if not timestamps or len(timestamps) == 0:
        return {"error": "timestamps array is required"}
    
    # Limit to 10 frames
    timestamps = timestamps[:10]
    
    frames = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "video.mp4")
        
        print(f"Downloading video: {video_url}")
        if not download_video(video_url, video_path):
            return {"error": "Failed to download video"}
        
        print(f"Extracting {len(timestamps)} frames...")
        
        for ts in timestamps:
            frame_path = os.path.join(tmpdir, f"frame_{ts}.jpg")
            
            if extract_frame(video_path, ts, frame_path, output_width, output_height):
                with open(frame_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                frames.append({
                    "timestamp": ts,
                    "image_base64": image_base64
                })
                print(f"Extracted frame at {ts}s")
            else:
                print(f"Failed to extract frame at {ts}s")
    
    print(f"Successfully extracted {len(frames)} frames")
    
    return {"frames": frames}

runpod.serverless.start({"handler": handler})
