import os
import uuid
from pathlib import Path
from typing import TypedDict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from dotenv import load_dotenv
from personalization_client import PersonalizationClient

# Import Freepik functions
# Add parent directories to path to import freepik_gemini
import sys
backend_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_root))
from freepik_gemini import (
    _create_gemini_task,
    _wait_for_gemini_task,
    _create_video_task,
    _wait_for_video_task,
    _download_file,
    FreepikGeminiError
)

load_dotenv()

client = PersonalizationClient()
model = ChatOpenAI(model="gpt-4o-mini")

# Configuration
# Use backend root for output directory to match app.py
OUTPUT_DIR = backend_root / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class VideoGenAgent(TypedDict):
    user_id: str
    prompt: str
    base_prompt: Optional[str]  # Prompt for image generation
    ad_prompt: Optional[str]  # Prompt for video animation
    image_path: Optional[str]  # Path to generated image
    video_path: Optional[str]  # Path to generated video
    image_url: Optional[str]  # URL of generated image
    video_url: Optional[str]  # URL of generated video
    error: Optional[str]  # Error message if any


def get_freepik_api_key() -> str:
    """Get Freepik API key from environment"""
    api_key = os.environ.get('FREEPIK_API_KEY')
    if not api_key:
        raise ValueError("FREEPIK_API_KEY environment variable is not set")
    return api_key


SYSTEM_PROMPT = """
You are a creative video generation assistant. Your role is to help users create engaging video content by:
1. Understanding their video generation request
2. Creating an optimized prompt for generating a base image
3. Creating an optimized prompt for animating that image into a video

When given a user prompt, split it into two parts:
- Base Image Prompt: Describe the static scene/image that should be generated
- Video Animation Prompt: Describe how the image should be animated/moved in the video

Return your response in a structured format that clearly separates the base image description from the video animation description.
"""


def improve_prompts(state: VideoGenAgent) -> VideoGenAgent:
    """
    Use LLM to improve and split the user prompt into base image and video animation prompts.
    """
    try:
        user_message = f"""
User request: {state["prompt"]}

Please provide:
1. A detailed prompt for generating a base image
2. A detailed prompt for animating that image into a video

Format your response as:
BASE_IMAGE: [your image prompt here]
VIDEO_ANIMATION: [your animation prompt here]
"""     

        summary = client.get_summary(user_id=state["user_id"])
        response = model.invoke([
            SystemMessage(content=f"User summary: {summary.summary}"),
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message)
        ])
        
        content = response.content
        
        # Parse the response to extract base_prompt and ad_prompt
        base_prompt = None
        ad_prompt = None
        
        if "BASE_IMAGE:" in content:
            parts = content.split("BASE_IMAGE:")
            if len(parts) > 1:
                remaining = parts[1]
                if "VIDEO_ANIMATION:" in remaining:
                    base_prompt = remaining.split("VIDEO_ANIMATION:")[0].strip()
                    ad_prompt = remaining.split("VIDEO_ANIMATION:")[1].strip()
                else:
                    base_prompt = remaining.strip()
        
        # Fallback: if parsing fails, use the original prompt for both
        if not base_prompt:
            base_prompt = state["prompt"]
        if not ad_prompt:
            ad_prompt = f"Animate the scene with smooth, engaging motion"
        
        return {
            "base_prompt": base_prompt,
            "ad_prompt": ad_prompt
        }
    except Exception as e:
        return {
            "error": f"Error improving prompts: {str(e)}",
            "base_prompt": state["prompt"],
            "ad_prompt": f"Animate the scene with smooth, engaging motion"
        }


def generate_image(state: VideoGenAgent) -> VideoGenAgent:
    """
    Generate an image using Freepik Gemini API.
    """
    try:
        api_key = get_freepik_api_key()
        base_prompt = state.get("base_prompt") or state["prompt"]
        
        # Create image generation task
        task_id = _create_gemini_task(api_key=api_key, prompt=base_prompt)
        
        # Wait for image generation
        generated_urls = _wait_for_gemini_task(
            api_key=api_key,
            task_id=task_id,
            timeout=120,
            poll_interval=2.0
        )
        
        if not generated_urls:
            raise FreepikGeminiError("No images generated")
        
        image_url = generated_urls[0]
        
        # Download and save the image
        image_filename = f"{uuid.uuid4()}_image.png"
        image_path = OUTPUT_DIR / image_filename
        _download_file(image_url, str(image_path))
        
        return {
            "image_url": image_url,
            "image_path": str(image_path)
        }
    except Exception as e:
        return {
            "error": f"Error generating image: {str(e)}"
        }


def generate_video(state: VideoGenAgent) -> VideoGenAgent:
    """
    Generate a video from the generated image using Freepik Video API.
    """
    try:
        if not state.get("image_url"):
            raise ValueError("Image URL is required to generate video")
        
        api_key = get_freepik_api_key()
        ad_prompt = state.get("ad_prompt") or f"Animate the scene with smooth, engaging motion"
        image_url = state["image_url"]
        
        # Create video generation task
        task_id = _create_video_task(
            api_key=api_key,
            image_url=image_url,
            prompt=ad_prompt
        )
        
        # Wait for video generation
        video_url = _wait_for_video_task(
            api_key=api_key,
            task_id=task_id,
            timeout=180,
            poll_interval=2.0
        )
        
        if not video_url:
            raise FreepikGeminiError("No video generated")
        
        # Download and save the video
        video_filename = f"{uuid.uuid4()}_video.mp4"
        video_path = OUTPUT_DIR / video_filename
        _download_file(video_url, str(video_path))
        
        return {
            "video_url": video_url,
            "video_path": str(video_path)
        }
    except Exception as e:
        return {
            "error": f"Error generating video: {str(e)}"
        }


# Create LangGraph workflow
workflow = StateGraph(VideoGenAgent)
workflow.add_node("improve_prompts", improve_prompts)
workflow.add_node("generate_image", generate_image)
workflow.add_node("generate_video", generate_video)

# Define the flow
workflow.add_edge(START, "improve_prompts")
workflow.add_edge("improve_prompts", "generate_image")
workflow.add_edge("generate_image", "generate_video")
workflow.add_edge("generate_video", END)

# Compile the agent
agent = workflow.compile()

if __name__ == "__main__":
    agent.invoke({"prompt": "A cute cat playing with a ball", "user_id": "1234567890"})