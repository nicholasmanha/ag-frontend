from freepik_gemini import two_step_gemini_image
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get("FREEPIK_API_KEY")
if not api_key:
    print(f"❌ Error: no api key")
    exit()

base_prompt = "modern minimalist tung tung tung sahur on white background, studio lighting"
ad_prompt = "make a cinematic ad video of these tung tung tung sahur running to israel"

base_path = "outputs/earbuds.jpg"
video_path = "outputs/earbuds_ad.mp4"

two_step_gemini_image(api_key, base_prompt, ad_prompt, base_path, video_path)
