import os
import subprocess
import xml.etree.ElementTree as ET
import cv2
import pyshine # For putBText, ensure you have run: pip install pyshine opencv-python
import time

# --- Configuration ---
ADB_PATH = "adb"  # Path to adb executable or just "adb" if in PATH

# Directories on the Android device (used by adb commands)
# Note: /data/local/tmp/ is generally accessible for temporary files
ANDROID_DEVICE_TEMP_DIR = "/data/local/tmp" 

# Local directories for storing files
LOCAL_TEMP_DIR = "temp_capture" # For storing raw screenshot and XML
OUTPUT_DIR = "output_annotated" # For storing the annotated screenshot

MIN_DIST_ELEMENTS = 10 # Minimum pixel distance between centers of elements to be considered separate
ELEMENT_ATTRIB_TO_FIND = "clickable" # Attribute to identify elements (e.g., "clickable", "focusable", "enabled")
IMAGE_PREFIX = "capture" # Prefix for the output files

# --- ADB Helper ---
def execute_adb_command(command_parts, device_id=None, check_error=True):
    """Executes an ADB command and returns its output or raises an error."""
    full_command = [ADB_PATH]
    if device_id:
        full_command.extend(["-s", device_id])
    full_command.extend(command_parts)
    
    # print(f"Executing: {' '.join(full_command)}")
    try:
        result = subprocess.run(full_command, capture_output=True, text=True, check=False)
        if check_error and result.returncode != 0:
            error_message = f"ADB Command Failed: {' '.join(full_command)}\nError: {result.stderr.strip()}"
            # print_with_color(error_message, "red") # Assuming print_with_color is not defined here
            print(error_message)
            return None # Indicate error
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"Error: '{ADB_PATH}' command not found. Is ADB installed and in your PATH?")
        raise
    except Exception as e:
        print(f"An error occurred while executing ADB command: {e}")
        raise
    return None


# --- Data Structure for UI Elements ---
class AndroidElement:
    def __init__(self, uid, bbox, attrib_name, attrib_value, text=None, desc=None):
        self.uid = uid
        self.bbox = bbox  # ((x1, y1), (x2, y2))
        self.attrib_name = attrib_name
        self.attrib_value = attrib_value
        self.text = text
        self.desc = desc

    def __repr__(self):
        return (f"AndroidElement(uid='{self.uid}', bbox={self.bbox}, "
                f"{self.attrib_name}='{self.attrib_value}', text='{self.text}', desc='{self.desc}')")

# --- XML Parsing and Element Extraction (Adapted from AppAgent.and_controller) ---
def get_id_from_element_appagent_logic(elem, parent_elem=None):
    """Generates an ID for an element, similar to AppAgent's logic."""
    elem_id_parts = []

    if parent_elem is not None:
        parent_id_parts = []
        if "resource-id" in parent_elem.attrib and parent_elem.attrib["resource-id"]:
            parent_id_parts.append(parent_elem.attrib["resource-id"].replace(":", ".").replace("/", "_"))
        else:
            parent_id_parts.append(parent_elem.attrib.get('class', 'UnknownClass'))
            bounds = parent_elem.attrib.get("bounds", "[0,0][0,0]")[1:-1].split("][")
            x1_p, y1_p = map(int, bounds[0].split(","))
            x2_p, y2_p = map(int, bounds[1].split(","))
            parent_id_parts.append(f"{x2_p-x1_p}_{y2_p-y1_p}")
        
        if "content-desc" in parent_elem.attrib and parent_elem.attrib["content-desc"] and len(parent_elem.attrib["content-desc"]) < 20:
            content_desc = parent_elem.attrib['content-desc'].replace("/", "_").replace(" ", "").replace(":", "_")
            parent_id_parts.append(content_desc)
        elem_id_parts.append("_".join(parent_id_parts))


    if "resource-id" in elem.attrib and elem.attrib["resource-id"]:
        elem_id_parts.append(elem.attrib["resource-id"].replace(":", ".").replace("/", "_"))
    else:
        elem_id_parts.append(elem.attrib.get('class', 'UnknownClass'))
        bounds = elem.attrib.get("bounds", "[0,0][0,0]")[1:-1].split("][")
        x1, y1 = map(int, bounds[0].split(","))
        x2, y2 = map(int, bounds[1].split(","))
        elem_id_parts.append(f"{x2-x1}_{y2-y1}") # width_height

    if "content-desc" in elem.attrib and elem.attrib["content-desc"] and len(elem.attrib["content-desc"]) < 20:
        content_desc = elem.attrib['content-desc'].replace("/", "_").replace(" ", "").replace(":", "_")
        elem_id_parts.append(content_desc)
    
    # Add index to differentiate siblings if needed, AppAgent sometimes does this
    # if 'index' in elem.attrib:
    #     elem_id_parts.append(f"idx{elem.attrib['index']}")

    return "_".join(filter(None, elem_id_parts)) if elem_id_parts else "unidentified_element"

def traverse_xml_tree(xml_path, elements_list, target_attrib_name, min_dist_elements):
    """Parses XML and extracts elements with the target attribute."""
    path_tracker = [] # To keep track of parent elements for UID generation
    try:
        for event, elem in ET.iterparse(xml_path, ['start', 'end']):
            if event == 'start':
                path_tracker.append(elem)
                if target_attrib_name in elem.attrib and elem.attrib[target_attrib_name] == "true":
                    bounds_str = elem.attrib.get("bounds")
                    if not bounds_str:
                        continue
                    
                    try:
                        bounds_parts = bounds_str[1:-1].split("][")
                        x1, y1 = map(int, bounds_parts[0].split(","))
                        x2, y2 = map(int, bounds_parts[1].split(","))
                    except ValueError:
                        # print(f"Warning: Could not parse bounds for element: {elem.attrib}")
                        continue

                    if x1 >= x2 or y1 >= y2: # Skip elements with zero or negative area
                        # print(f"Warning: Skipping element with invalid bounds: {bounds_str}")
                        continue

                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    # Check for proximity with already added elements (AppAgent logic)
                    is_too_close = False
                    for existing_elem in elements_list:
                        ex_x1, ex_y1 = existing_elem.bbox[0]
                        ex_x2, ex_y2 = existing_elem.bbox[1]
                        existing_center_x = (ex_x1 + ex_x2) // 2
                        existing_center_y = (ex_y1 + ex_y2) // 2
                        dist_sq = (center_x - existing_center_x)**2 + (center_y - existing_center_y)**2
                        if dist_sq < min_dist_elements**2:
                            is_too_close = True
                            break
                    
                    if not is_too_close:
                        parent_elem = path_tracker[-2] if len(path_tracker) > 1 else None
                        uid = get_id_from_element_appagent_logic(elem, parent_elem)
                        text_content = elem.attrib.get("text", "")
                        content_desc = elem.attrib.get("content-desc", "")
                        
                        android_elem = AndroidElement(
                            uid=uid,
                            bbox=((x1, y1), (x2, y2)),
                            attrib_name=target_attrib_name,
                            attrib_value=elem.attrib[target_attrib_name],
                            text=text_content,
                            desc=content_desc
                        )
                        elements_list.append(android_elem)
            
            elif event == 'end':
                if path_tracker and path_tracker[-1] == elem: # ensure we pop the correct element
                    path_tracker.pop()
                elem.clear() # Free memory

    except ET.ParseError as e:
        print(f"Error parsing XML file '{xml_path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during XML traversal: {e}")


# --- Screenshot Annotation (Adapted from AppAgent.utils.draw_bbox_multi) ---
def draw_bounding_boxes_on_image(img_path, output_path, elements_list):
    """Draws bounding boxes and labels for elements on the image."""
    try:
        img_cv = cv2.imread(img_path)
        if img_cv is None:
            print(f"Error: Could not read image from {img_path}")
            return False
    except Exception as e:
        print(f"Error reading image {img_path} with OpenCV: {e}")
        return False

    for i, elem in enumerate(elements_list):
        (x1, y1), (x2, y2) = elem.bbox
        label = str(i + 1) # 1-indexed labels

        # Bounding box color (blue for clickable as an example)
        box_color = (250, 0, 0) # BGR format for OpenCV (Blue)
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), box_color, 2)

        # Label text properties
        text_color = (255, 255, 255) # White text
        bg_color = (0,0,0) # Black background for text for pyshine
        
        # Using pyshine.putBText for styled labels, similar to AppAgent
        # Calculate a position for the label (e.g., top-left corner of the box)
        # pyshine might have specific ways to place text, check its documentation if needed.
        # Simple placement:
        text_x = x1 + 5
        text_y = y1 + 20 # A bit offset from the top line
        
        try:
            # pyshine.putBText arguments:
            # image, text, text_offset_x, text_offset_y, vspace, hspace, font_scale,
            # background_RGB, text_RGB, font_thickness, alpha (for background)
            img_cv = pyshine.putBText(img_cv, label, 
                                      text_offset_x=text_x, text_offset_y=text_y,
                                      vspace=5, hspace=5, font_scale=0.7, 
                                      background_RGB=(bg_color[2], bg_color[1], bg_color[0]), # RGB for pyshine
                                      text_RGB=(text_color[2], text_color[1], text_color[0]),   # RGB for pyshine
                                      font_thickness=1, alpha=0.8)
        except Exception as e:
            # Fallback to simple cv2.putText if pyshine fails or for very small boxes
            # print(f"pyshine.putBText failed: {e}. Using cv2.putText as fallback.")
            cv2.putText(img_cv, label, (x1 + 5, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
            # Draw a small rectangle behind text for visibility if pyshine is not used
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img_cv, (x1+2, y1+2), (x1+5+w, y1+15+h-5), (bg_color[0],bg_color[1],bg_color[2]), -1) # BGR for cv2
            cv2.putText(img_cv, label, (x1 + 5, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)


    try:
        cv2.imwrite(output_path, img_cv)
        print(f"Annotated image saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving annotated image {output_path}: {e}")
        return False

# --- Core Logic ---
def get_device_screenshot_and_xml(device_id=None):
    """Captures screenshot and UI XML from the device."""
    os.makedirs(LOCAL_TEMP_DIR, exist_ok=True)

    # Define paths on the Android device
    device_screenshot_path = f"{ANDROID_DEVICE_TEMP_DIR}/{IMAGE_PREFIX}.png"
    device_xml_path = f"{ANDROID_DEVICE_TEMP_DIR}/{IMAGE_PREFIX}.xml"

    # Define local paths
    local_screenshot_path = os.path.join(LOCAL_TEMP_DIR, f"{IMAGE_PREFIX}.png")
    local_xml_path = os.path.join(LOCAL_TEMP_DIR, f"{IMAGE_PREFIX}.xml")

    # 1. Capture Screenshot
    print("Capturing screenshot...")
    # Remove old file first if it exists on device, to avoid issues with screencap
    execute_adb_command(["shell", "rm", device_screenshot_path], device_id, check_error=False) 
    time.sleep(0.2)
    if execute_adb_command(["shell", "screencap", "-p", device_screenshot_path], device_id) is None:
        return None, None
    time.sleep(0.5) # Give time for file to be written
    if execute_adb_command(["pull", device_screenshot_path, local_screenshot_path], device_id) is None:
        return None, None
    print(f"Screenshot saved to: {local_screenshot_path}")

    # 2. Get UI XML
    print("Dumping UI XML...")
    # Remove old file first
    execute_adb_command(["shell", "rm", device_xml_path], device_id, check_error=False)
    time.sleep(0.2)
    if execute_adb_command(["shell", "uiautomator", "dump", device_xml_path], device_id) is None:
        return local_screenshot_path, None # Screenshot might be valid
    time.sleep(0.5) # Give time for dump
    if execute_adb_command(["pull", device_xml_path, local_xml_path], device_id) is None:
        return local_screenshot_path, None
    print(f"UI XML saved to: {local_xml_path}")

    return local_screenshot_path, local_xml_path

def main():
    """Main function to orchestrate the process."""
    print("Starting UI annotation process...")
    
    # You can specify a device ID if you have multiple devices/emulators:
    # e.g., device_id = "emulator-5554" 
    device_id = None 

    local_screenshot_path, local_xml_path = get_device_screenshot_and_xml(device_id)

    if not local_screenshot_path or not local_xml_path:
        print("Failed to get screenshot or XML. Exiting.")
        return

    if not os.path.exists(local_screenshot_path):
        print(f"Error: Screenshot file not found at {local_screenshot_path}")
        return
    if not os.path.exists(local_xml_path):
        print(f"Error: XML file not found at {local_xml_path}")
        return

    # Extract UI elements
    ui_elements = []
    print(f"Parsing XML and finding '{ELEMENT_ATTRIB_TO_FIND}' elements...")
    traverse_xml_tree(local_xml_path, ui_elements, ELEMENT_ATTRIB_TO_FIND, MIN_DIST_ELEMENTS)

    if not ui_elements:
        print(f"No '{ELEMENT_ATTRIB_TO_FIND}' elements found in the UI XML.")
    else:
        print(f"Found {len(ui_elements)} '{ELEMENT_ATTRIB_TO_FIND}' elements:")
        for i, elem in enumerate(ui_elements):
            print(f"  {i+1}. {elem}") # Print element details

    # Annotate screenshot
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    annotated_image_filename = f"{IMAGE_PREFIX}_annotated_{ELEMENT_ATTRIB_TO_FIND}.png"
    annotated_image_path = os.path.join(OUTPUT_DIR, annotated_image_filename)
    
    print(f"Annotating screenshot: {local_screenshot_path} -> {annotated_image_path}")
    if draw_bounding_boxes_on_image(local_screenshot_path, annotated_image_path, ui_elements):
        print("Annotation successful.")
    else:
        print("Annotation failed.")
    
    print("Process finished.")

# --- Entry Point ---
if __name__ == "__main__":
    main() 