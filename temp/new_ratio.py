import google.generativeai as genai
from PIL import Image
import io
import json
import os
import re

def get_gmail_tap_coordinates_from_gemini(image_path: str, api_key: str) -> tuple[int, int] | None:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        pil_image = Image.open(io.BytesIO(image_bytes))
        original_width, original_height = pil_image.size

        image_part = {
            "mime_type": "image/png",
            "data": image_bytes
        }

        # MODIFIED PROMPT: Ask for normalized_x and normalized_y
        prompt = f"""You are a precise Android AI agent. Your primary task is to identify UI elements in the provided screenshot and return their interaction coordinates.
The screenshot dimensions are {original_width}x{original_height} pixels.

TASK: Identify the icon for the app specified in the 'target_app_name' field within the output JSON. For this specific request, the target app is 'Youtube'.

OUTPUT REQUIREMENTS:
Your response MUST be a single, valid JSON object. Do NOT include any text, explanations, or markdown formatting outside of this JSON object.
The JSON object MUST have the following structure:
{{
  "thought": "A concise step-by-step thought process for how you identified the icon and its center.",
  "action_type": "tap",
  "target_app_name": "Youtube", // Or the app you are targeting
  "parameters": {{
    "normalized_x": <float>, // Normalized X-coordinate (0.0 to 1.0) of the center of the Youtube icon.
    "normalized_y": <float>  // Normalized Y-coordinate (0.0 to 1.0) of the center of the Youtube icon.
  }}
}}

Here are some examples of correct output format for different scenarios:

Example 1 (Targeting Gmail):
Image: [Conceptually, you'd be sending an image here if it was text-only few shotting, but with multimodal, the current image serves this role]
Output:
```json
{{
  "thought": "The Gmail icon is the second icon in the first row of apps. Its center appears to be roughly 1/4 of the way across the screen horizontally and 1/2 way down vertically based on the app grid.",
  "action_type": "tap",
  "target_app_name": "Gmail",
  "parameters": {{
    "normalized_x": 0.35,
    "normalized_y": 0.49
  }}
}}

Ensure 'normalized_x' and 'normalized_y' are floating-point numbers strictly between 0.0 and 1.0.
Do not provide pixel coordinates; only provide normalized coordinates.
"""
        response = model.generate_content(
            [prompt, image_part],
            generation_config=genai.types.GenerationConfig(
                # candidate_count=1, # Usually default
                # stop_sequences=['...'],
                # max_output_tokens=256, # Adjust if your JSON is larger
                temperature=0.1,  # Lower temperature = less randomness, more deterministic
                # top_p=0.9, # Consider adjusting if needed
                # top_k=10   # Consider adjusting if needed
            )
        )
        if not response.candidates or not response.candidates[0].content.parts:
            # print("Gemini response blocked or empty.") # Debugging print
            return None
            
        response_text = response.candidates[0].content.parts[0].text
        # print(f"LLM Raw Response: {response_text}") # Debugging print
        
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = response_text[first_brace : last_brace+1]
            else:
                # print(f"No valid JSON object found in response: {response_text}") # Debugging print
                return None
        
        # print(f"Extracted JSON: {json_str}") # Debugging print
        data = json.loads(json_str)
        
        if data.get("action_type") == "tap" and "parameters" in data:
            params = data["parameters"]
            # MODIFIED PARSING: Expect normalized_x and normalized_y
            if "normalized_x" in params and "normalized_y" in params:
                norm_x = float(params["normalized_x"])
                norm_y = float(params["normalized_y"])

                # Ensure they are within expected range before scaling
                if not (0.0 <= norm_x <= 1.0 and 0.0 <= norm_y <= 1.0):
                    # print(f"Normalized coordinates out of range: nx={norm_x}, ny={norm_y}") # Debug print
                    return None

                # Scale normalized coordinates to original image dimensions
                pixel_x = int(norm_x * original_width)
                pixel_y = int(norm_y * original_height)
                return pixel_x, pixel_y
            else:
                # print(f"Missing normalized_x or normalized_y in parameters: {params}") # Debug print
                return None
        else:
            # print(f"Response not a tap action or missing parameters: {data}") # Debug print
            return None

    except FileNotFoundError:
        # print(f"Error: Image file not found at {image_path}") # Debug print
        return None
    except Exception as e:
        # print(f"An error occurred: {e}") # Debug print
        return None

if __name__ == '__main__':
    YOUR_GEMINI_API_KEY = ""
    if not YOUR_GEMINI_API_KEY:
        # print("Error: GEMINI_API_KEY environment variable not set.")
        # print("Please set it before running the script.")
        exit()
    
    # Ensure this path points to your image where Youtube is visible
    test_image_path = r"output_annotated\capture_annotated_clickable.png" # UPDATE THIS PATH

    if not os.path.exists(test_image_path):
        # print(f"Test image not found: {test_image_path}")
        # print("Please create a test image and update the 'test_image_path'.")
        exit()

    coordinates = get_gmail_tap_coordinates_from_gemini(test_image_path, YOUR_GEMINI_API_KEY)

    if coordinates:
        print(f"Gemini suggests tapping at: X={coordinates[0]}, Y={coordinates[1]} to open Youtube.")
    else:
        print("Could not determine coordinates to open Youtube.")