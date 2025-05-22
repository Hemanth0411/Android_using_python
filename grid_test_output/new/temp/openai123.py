import cv2
import numpy as np
import uiautomator2 as u2
import base64
import os
import google.generativeai as genai
from PIL import Image

# === CONFIG ===
LLM_SIZE = 800
REAL_SCREEN_WIDTH = 1280
REAL_SCREEN_HEIGHT = 2856
tmp_img_path = 'screen_for_gemini.png'
GOOGLE_API_KEY = ""

# === Initialize Gemini Client ===
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Connect to Android device ===
print("[*] Connecting to device...")
d = u2.connect()

# === Capture screenshot ===
print("[*] Capturing screenshot...")
img_bgr = d.screenshot(format='opencv')
orig_h, orig_w = img_bgr.shape[:2]

print(f"[*] Original screenshot size: {orig_w}x{orig_h}")

# === Resize and Save ===
print(f"[*] Resizing to {LLM_SIZE}x{LLM_SIZE} for Gemini input...")
resized = cv2.resize(img_bgr, (LLM_SIZE, LLM_SIZE))
cv2.imwrite(tmp_img_path, resized)

# === Load as PIL Image ===
img = Image.open(tmp_img_path)

# === Prompt with image context ===
prompt = (
    f"This image is exactly {LLM_SIZE}x{LLM_SIZE} pixels. "
    "It is a screenshot from Chrome showing Wikipedia's main page. "
    "Locate the search input box or magnifying-glass icon. "
    "Return only its coordinates as 'x,y' integers within this image."
)

# === Send multimodal prompt to Gemini ===
print("[*] Sending image to Gemini 1.5 Flash...")
response = model.generate_content(
    [prompt, img],
    stream=False
)

response_text = response.text.strip()
print(f"[+] Gemini Response: {response_text}")

try:
    llm_x, llm_y = map(int, response_text.replace("(", "").replace(")", "").replace(" ", "").split(','))
except Exception as e:
    raise ValueError(f"Could not parse coordinates from Gemini: '{response_text}'") from e

# === Validate / Clamp to image bounds ===
llm_x = max(0, min(llm_x, LLM_SIZE - 1))
llm_y = max(0, min(llm_y, LLM_SIZE - 1))
print(f"[+] Coordinates from Gemini (resized image): x={llm_x}, y={llm_y}")

# === Map back to original screenshot ===
x_scale = orig_w / LLM_SIZE
y_scale = orig_h / LLM_SIZE
screenshot_x = int(llm_x * x_scale)
screenshot_y = int(llm_y * y_scale)

# === Map to real screen ===
real_x = int(screenshot_x * (REAL_SCREEN_WIDTH / orig_w))
real_y = int(screenshot_y * (REAL_SCREEN_HEIGHT / orig_h))
print(f"[+] Tapping at: ({real_x}, {real_y})")

# === Tap the screen ===
d.click(real_x, real_y)
print("[*] Tap complete.")
