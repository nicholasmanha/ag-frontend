from freepik_gemini import two_step_gemini_image
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get("FREEPIK_API_KEY")
if not api_key:
    print(f"❌ Error: no api key")
    exit()

base_prompt = "modern minimalist wireless earbuds on white background, studio lighting"
ad_prompt = "make a 5-second cinematic ad video of these earbuds rotating on a reflective surface with glowing blue light"

base_path = "outputs/earbuds.jpg"
video_path = "outputs/earbuds_ad.mp4"

two_step_gemini_image(api_key, base_prompt, ad_prompt, base_path, video_path)
