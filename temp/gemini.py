import google.generativeai as genai
import PIL.Image
import io
import json
import re
from typing import Optional, Tuple, Dict

genai.configure(api_key="")
GEMINI_MODEL_NAME = "gemini-1.5-flash"

def get_resolution_and_coordinates(
    image_bytes: bytes,
    element_description: str,
) -> Optional[Dict[str, int]]:
    img = PIL.Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    prompt = f"""Analyze the provided screenshot of an Android device.

1. Determine and return the resolution (width and height in pixels).
2. Identify the visual element described as: "{element_description}".
3. If found, provide the estimated pixel coordinates (X, Y) of the *center* of the element.

Return a JSON object like this:
{{
  "image_width": <integer_width>,
  "image_height": <integer_height>,
  "element_found": true/false,
  "x_coordinate": <integer_x_or_null>,
  "y_coordinate": <integer_y_or_null>
}}
"""

    contents = [img, prompt]
    response = model.generate_content(contents)

    if not response.candidates or not response.candidates[0].content.parts:
        return None

    response_text = response.candidates[0].content.parts[0].text

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        first_brace = response_text.find('{')
        last_brace = response_text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_str = response_text[first_brace : last_brace+1]
        else:
            return None

    try:
        data = json.loads(json_str)
        if (
            isinstance(data.get("image_width"), int)
            and isinstance(data.get("image_height"), int)
        ):
            return data
    except:
        return None

    return None

# Example Usage
if __name__ == "__main__":
    with open(r"temp_capture\capture.png", "rb") as image_file:
        screenshot_bytes = image_file.read()

    description = "Chrome icon which is a circle with a red, green, and yellow color scheme, below the center of the screen"
    # description = "Chrome icon which is a circle with a red, green, and yellow color scheme, below the center of the screen"
    result = get_resolution_and_coordinates(screenshot_bytes, description)

    if result:
        print(f"Image Resolution: {result['image_width']}x{result['image_height']}")
        if result.get("element_found"):
            print(f"Found '{description}' at X={result['x_coordinate']}, Y={result['y_coordinate']}")
        else:
            print(f"'{description}' not found in the image.")
    else:
        print("Failed to parse Gemini response.")
