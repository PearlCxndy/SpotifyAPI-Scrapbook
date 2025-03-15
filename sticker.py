import time
import threading
import os
from queue import Queue
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO
from rembg import remove  # Import rembg for background removal

# Load API keys from API.env
load_dotenv("API.env")
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

# Queue for receiving keywords
keyword_queue = Queue()

# Correct Hugging Face API Endpoint
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/artificialguybr/StickersRedmond"

headers = {
    "Authorization": f"Bearer {HUGGING_FACE_API_KEY}"
}

def add_keyword_to_queue(keyword):
    """Receives keywords and adds them to the queue."""
    keyword_queue.put(keyword)

def generate_ai_image(prompt):
    """Generates an AI image using Hugging Face API."""
    try:
        response = requests.post(
            HUGGING_FACE_API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            print(f"✅ AI Image Generated for prompt: {prompt}")
            return image  # Return the PIL.Image object
        else:
            print(f"❌ Image Generation Failed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"❌ Image Generation Failed: {e}")
        return None

def remove_image_background(image):
    """Removes background from the image using rembg."""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    # Process image to remove background
    output_bytes = remove(img_bytes)
    result_image = Image.open(BytesIO(output_bytes))
    return result_image

def sticker_generation_loop():
    """Generates stickers based on received keywords."""
    while True:
        if not keyword_queue.empty():
            keyword = keyword_queue.get()
            print(f"🎨 Generating AI image for keyword: {keyword}")
            generate_ai_image(keyword)
        time.sleep(10)  # Check every 10 seconds

# Start the sticker generation loop in a separate thread
sticker_thread = threading.Thread(target=sticker_generation_loop, daemon=True)
sticker_thread.start()