import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import threading

# Import the functions from the original code
from freepik_gemini import (
    two_step_gemini_image,
    _create_gemini_task,
    _wait_for_gemini_task,
    _download_file,
    FreepikGeminiError
)

app = Flask(__name__)
CORS(app)

# Configuration
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Store task statuses in memory (use Redis/database for production)
task_status = {}


def get_api_key():
    """Get API key from environment or request header"""
    api_key = request.headers.get('X-Freepik-API-Key')
    if not api_key:
        api_key = os.environ.get('FREEPIK_API_KEY')
    return api_key


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    Generate an image using Gemini.
    
    Request body:
    {
        "prompt": "your image prompt",
        "reference_images": [...] (optional)
    }
    """
    try:
        api_key = get_api_key()
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        data = request.json
        prompt = data.get('prompt')
        reference_images = data.get('reference_images')
        
        if not prompt:
            return jsonify({"error": "prompt is required"}), 400

        # Create task
        task_id = _create_gemini_task(api_key, prompt, reference_images)
        
        # Wait for completion
        generated_urls = _wait_for_gemini_task(api_key, task_id)
        
        # Download the first image
        image_filename = f"{uuid.uuid4()}.png"
        image_path = OUTPUT_DIR / image_filename
        _download_file(generated_urls[0], str(image_path))
        
        return jsonify({
            "success": True,
            "image_url": generated_urls[0],
            "local_path": f"/api/download/{image_filename}",
            "all_urls": generated_urls
        }), 200
        
    except FreepikGeminiError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/api/create-video-ad', methods=['POST'])
def create_video_ad():
    """
    Generate a base image and then create a video ad from it.
    
    Request body:
    {
        "base_prompt": "prompt for base image",
        "ad_prompt": "prompt for video animation",
        "timeout": 180 (optional),
        "poll_interval": 2.0 (optional)
    }
    """
    try:
        api_key = get_api_key()
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        data = request.json
        base_prompt = data.get('base_prompt')
        ad_prompt = data.get('ad_prompt')
        timeout = data.get('timeout', 180)
        poll_interval = data.get('poll_interval', 2.0)
        
        if not base_prompt or not ad_prompt:
            return jsonify({"error": "base_prompt and ad_prompt are required"}), 400

        # Generate unique filenames
        image_filename = f"{uuid.uuid4()}.png"
        video_filename = f"{uuid.uuid4()}.mp4"
        image_path = OUTPUT_DIR / image_filename
        video_path = OUTPUT_DIR / video_filename
        
        # Run the two-step pipeline
        base_image_path, video_output_path = two_step_gemini_image(
            api_key=api_key,
            base_prompt=base_prompt,
            ad_prompt=ad_prompt,
            base_image_path=str(image_path),
            video_output_path=str(video_path),
            timeout=timeout,
            poll_interval=poll_interval
        )
        
        return jsonify({
            "success": True,
            "base_image": f"/api/download/{image_filename}",
            "video": f"/api/download/{video_filename}",
            "message": "Video ad created successfully"
        }), 200
        
    except FreepikGeminiError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/api/create-video-ad-async', methods=['POST'])
def create_video_ad_async():
    """
    Async version - returns a task ID immediately, check status with /api/task-status/{task_id}
    
    Request body:
    {
        "base_prompt": "prompt for base image",
        "ad_prompt": "prompt for video animation"
    }
    """
    try:
        api_key = get_api_key()
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        data = request.json
        base_prompt = data.get('base_prompt')
        ad_prompt = data.get('ad_prompt')
        
        if not base_prompt or not ad_prompt:
            return jsonify({"error": "base_prompt and ad_prompt are required"}), 400

        # Generate task ID
        task_id = str(uuid.uuid4())
        task_status[task_id] = {"status": "processing", "progress": "Starting..."}
        
        # Generate unique filenames
        image_filename = f"{task_id}_image.png"
        video_filename = f"{task_id}_video.mp4"
        image_path = OUTPUT_DIR / image_filename
        video_path = OUTPUT_DIR / video_filename
        
        # Run in background thread
        def background_task():
            try:
                task_status[task_id]["progress"] = "Generating base image..."
                base_image_path, video_output_path = two_step_gemini_image(
                    api_key=api_key,
                    base_prompt=base_prompt,
                    ad_prompt=ad_prompt,
                    base_image_path=str(image_path),
                    video_output_path=str(video_path)
                )
                task_status[task_id] = {
                    "status": "completed",
                    "base_image": f"/api/download/{image_filename}",
                    "video": f"/api/download/{video_filename}"
                }
            except Exception as e:
                task_status[task_id] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        thread = threading.Thread(target=background_task)
        thread.start()
        
        return jsonify({
            "task_id": task_id,
            "status_url": f"/api/task-status/{task_id}"
        }), 202
        
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/api/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the status of an async task"""
    if task_id not in task_status:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task_status[task_id]), 200


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a generated file"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=False)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Set your API key as environment variable or pass in headers
    # export FREEPIK_API_KEY=your_key_here
    app.run(debug=True, host='0.0.0.0', port=5000)