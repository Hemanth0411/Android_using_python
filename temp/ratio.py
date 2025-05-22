import google.generativeai as genai
from PIL import Image
import io
import json
import os
import re

def get_gmail_tap_coordinates_with_scaling_from_gemini(image_path: str, api_key: str) -> tuple[int, int] | None:
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

        # MODIFIED PROMPT
        prompt = f"""You are an AI agent with the ability to perform actions in an Android environment by providing coordinates for tap operations.
The provided image is a screenshot of an Android screen.
You will analyze this image. When providing coordinates, you MUST also specify the width and height of the image you effectively analyzed to determine those coordinates (this might be the original size or an internally perceived/resized version).

Your current task is to identify the Gmail app icon and provide:
1. The X and Y pixel coordinates to tap on it to open the Gmail app. These coordinates should be relative to the 'analyzed_image_width' and 'analyzed_image_height' you report.
2. The 'analyzed_image_width' and 'analyzed_image_height' you used.

Output Format:
Your response MUST be a single JSON object. Do not include any text outside this JSON object.
The JSON object should have the following fields:
- "thought": "Your brief reasoning for choosing the coordinates."
- "action_type": "tap"
- "parameters": {{
    "x": <int_x_coord_for_gmail_icon_relative_to_analyzed_dims>,
    "y": <int_y_coord_for_gmail_icon_relative_to_analyzed_dims>,
    "analyzed_image_width": <int_width_of_image_model_based_coords_on>,
    "analyzed_image_height": <int_height_of_image_model_based_coords_on>
  }}
"""
        response = model.generate_content([prompt, image_part])

        if not response.candidates or not response.candidates[0].content.parts:
            print("Gemini response blocked or empty.")
            return None
            
        response_text = response.candidates[0].content.parts[0].text
        print(f"DEBUG: Raw Gemini Response Text:\n{response_text}") # For debugging the full response
        
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        json_str = ""
        if match:
            json_str = match.group(1)
        else:
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = response_text[first_brace : last_brace+1]
            else:
                print(f"No valid JSON object found in response: {response_text}")
                return None
        
        print(f"DEBUG: Extracted JSON String:\n{json_str}")
        data = json.loads(json_str)
        
        if data.get("action_type") == "tap" and "parameters" in data:
            params = data["parameters"]
            if "x" in params and "y" in params and \
               "analyzed_image_width" in params and "analyzed_image_height" in params:
                
                llm_x = int(params["x"])
                llm_y = int(params["y"])
                analyzed_width = int(params["analyzed_image_width"])
                analyzed_height = int(params["analyzed_image_height"])

                print(f"DEBUG: LLM reports: x={llm_x}, y={llm_y} for analyzed_dims={analyzed_width}x{analyzed_height}")

                if analyzed_width <= 0 or analyzed_height <= 0:
                    print(f"Error: LLM reported invalid analyzed dimensions: {analyzed_width}x{analyzed_height}")
                    return None

                # Scale coordinates back to the original image dimensions
                final_x = int((llm_x / analyzed_width) * original_width)
                final_y = int((llm_y / analyzed_height) * original_height)
                
                return final_x, final_y
            else:
                print(f"Missing x, y, or analyzed dimensions in parameters: {params}")
                return None
        else:
            print(f"Response not a tap action or missing parameters: {data}")
            return None

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except json.JSONDecodeError as je:
        print(f"Error decoding JSON from LLM response: {je}")
        print(f"Problematic JSON string was: {json_str}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    YOUR_GEMINI_API_KEY =  ""
    if not YOUR_GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        exit()
    
    # This should be the path to your original 1280x2856 PNG image
    test_image_path = r"output_annotated\capture_annotated_clickable.png" # MAKE SURE THIS FILE EXISTS AND IS THE CORRECT ONE

    if not os.path.exists(test_image_path):
        print(f"Test image not found: {test_image_path}")
        print("Please ensure the image exists at this path.")
        exit()

    coordinates = get_gmail_tap_coordinates_with_scaling_from_gemini(test_image_path, YOUR_GEMINI_API_KEY)

    if coordinates:
        print(f"Final scaled coordinates for Gmail tap: X={coordinates[0]}, Y={coordinates[1]}")
    else:
        print("Could not determine coordinates to open Gmail with scaling.")