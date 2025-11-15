import time
import requests
from pathlib import Path

# === CONFIG ===
FREEPIK_GEMINI_ENDPOINT = "https://api.freepik.com/v1/ai/gemini-2-5-flash-image-preview"
VIDEO_MODEL = "kling-v2-5-pro"  # Change to pixverse-v5, seedance-lite-1080p, etc.
FREEPIK_VIDEO_ENDPOINT = f"https://api.freepik.com/v1/ai/image-to-video/{VIDEO_MODEL}"


class FreepikGeminiError(Exception):
    pass


# === GEMINI IMAGE GENERATION HELPERS ===

def _create_gemini_task(api_key: str, prompt: str, reference_images=None) -> str:
    """
    POST /v1/ai/gemini-2-5-flash-image-preview
    Returns task_id.
    """
    headers = {
        "Content-Type": "application/json",
        "x-freepik-api-key": api_key,
    }

    payload = {"prompt": prompt}
    if reference_images:
        payload["reference_images"] = reference_images

    resp = requests.post(FREEPIK_GEMINI_ENDPOINT, json=payload, headers=headers)
    if resp.status_code != 200:
        raise FreepikGeminiError(
            f"Error creating Gemini task: {resp.status_code} {resp.text}"
        )

    data = resp.json().get("data", {})
    task_id = data.get("task_id")
    if not task_id:
        raise FreepikGeminiError(f"Missing task_id in response: {resp.text}")

    return task_id


def _wait_for_gemini_task(api_key: str, task_id: str, timeout: int = 120, poll_interval: float = 2.0) -> list[str]:
    """
    GET /v1/ai/gemini-2-5-flash-image-preview/{task-id} in a loop
    until generated URLs are available or timeout.
    """
    headers = {"x-freepik-api-key": api_key}
    url = f"{FREEPIK_GEMINI_ENDPOINT}/{task_id}"
    start = time.time()

    while True:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise FreepikGeminiError(
                f"Error getting Gemini task status: {resp.status_code} {resp.text}"
            )

        data = resp.json().get("data", {})
        status = data.get("status")
        generated = data.get("generated") or []

        if generated:
            return generated

        if time.time() - start > timeout:
            raise FreepikGeminiError(
                f"Timeout waiting for task {task_id}, last status={status}, data={data}"
            )

        time.sleep(poll_interval)


def _download_file(url: str, output_path: str):
    """
    Download an image or video URL and save it to output_path.
    """
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise FreepikGeminiError(f"Error downloading file: {r.status_code} {r.text}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return output_path


# === VIDEO GENERATION HELPERS ===

def _create_video_task(api_key: str, image_url: str, prompt: str) -> str:
    """
    POST /v1/ai/image-to-video/{VIDEO_MODEL}
    Returns task_id.
    """
    headers = {
        "Content-Type": "application/json",
        "x-freepik-api-key": api_key,
    }

    payload = {
        "image_url": image_url,
        "prompt": prompt,
        "duration": "10"  # seconds, adjust as needed
    }

    resp = requests.post(FREEPIK_VIDEO_ENDPOINT, json=payload, headers=headers)
    if resp.status_code != 200:
        raise FreepikGeminiError(f"Error creating video task: {resp.status_code} {resp.text}")

    data = resp.json().get("data", {})
    task_id = data.get("task_id")
    if not task_id:
        raise FreepikGeminiError(f"Missing task_id in video response: {resp.text}")

    return task_id


def _wait_for_video_task(api_key: str, task_id: str, timeout: int = 180, poll_interval: float = 2.0) -> str:
    """
    GET /v1/ai/image-to-video/{VIDEO_MODEL}/{task-id}
    Waits until the video is ready, returns video URL.
    """
    headers = {"x-freepik-api-key": api_key}
    url = f"{FREEPIK_VIDEO_ENDPOINT}/{task_id}"
    start = time.time()

    while True:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise FreepikGeminiError(f"Error polling video task: {resp.status_code} {resp.text}")

        data = resp.json().get("data", {})
        status = data.get("status")
        generated = data.get("generated") or []

        if generated:
            return generated[0]

        if time.time() - start > timeout:
            raise FreepikGeminiError(f"Timeout waiting for video {task_id}, last status={status}")

        time.sleep(poll_interval)


# === MAIN PIPELINE ===

def two_step_gemini_image(api_key: str, base_prompt: str, ad_prompt: str, base_image_path: str, video_output_path: str, *, timeout: int = 180, poll_interval: float = 2.0) -> tuple[str, str]:
    """
    1) Generate a base image from `base_prompt`.
    2) Generate a short ad video from that image using `ad_prompt`.

    Returns:
        (base_image_path, video_output_path)
    """

    # Step 1: Generate base image
    task_id_1 = _create_gemini_task(api_key=api_key, prompt=base_prompt)
    generated_urls_1 = _wait_for_gemini_task(api_key=api_key, task_id=task_id_1, timeout=timeout, poll_interval=poll_interval)
    base_image_url = generated_urls_1[0]
    _download_file(base_image_url, base_image_path)

    # Step 2: Generate video ad
    task_id_2 = _create_video_task(api_key=api_key, image_url=base_image_url, prompt=ad_prompt)
    video_url = _wait_for_video_task(api_key=api_key, task_id=task_id_2, timeout=timeout, poll_interval=poll_interval)
    _download_file(video_url, video_output_path)

    return base_image_path, video_output_path
