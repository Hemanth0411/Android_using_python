## 📱 Android Automation Utilities

This repository contains a collection of scripts and tools to **automate Android device interactions** using ADB (Android Debug Bridge). These utilities are helpful for:

* UI testing and validation
* App navigation and prototyping
* Building AI agents that simulate human interaction on Android devices
* Generating annotated views of app UIs for programmatic interaction

---

### 🔧 Available Scripts

#### 1. **ADB Controller Script (`adb_controller.py`)**

📂 [`adb_controller.py`](./adb_controller.py)

This core script provides a Python interface to send basic ADB commands for emulating touchscreen interactions and key presses on a connected Android device. It includes functions to:

* Retrieve device screen resolution.
* Tap, long-tap, and swipe across the screen (custom coordinates and duration).
* Perform directional swipes (up, down, left, right).
* Type text directly into focused input fields.
* Send common key events like Home, Back, Enter, Power, Volume controls, Media controls, Delete, Tab, and App Switch.

✅ Robust error handling is included for common issues like device connection problems, screen resolution parsing failures, and ADB command execution errors.

🧪 **Example Use Cases**:

* Automate login flows
* Scroll through apps for testing
* Simulate touch interactions for mobile AI agents

---

#### 2. **Interactive ADB Controller (`interactive_adb.py`)**

📂 [`interactive_adb.py`](./interactive_adb.py)

This script offers an interactive command-line menu to utilize the functionalities of `adb_controller.py`. It allows users to:

* Choose from a list of actions (e.g., tap, type, swipe, press specific keys).
* Input necessary parameters like coordinates or text when prompted.
* See immediate feedback as actions are performed on the device.

This is useful for manually testing ADB commands or exploring app interactions without writing a full script.

---

#### 3. **Annotated Screenshot Generator (`annotated_screenshot_generator.py`)**

📂 [`annotated_screenshot_generator.py`](./annotated_screenshot_generator.py)

This script captures the current screen and its UI layout (XML hierarchy) from the Android device. It then:

* Parses the XML to identify specified UI elements (e.g., all "clickable" elements).
* Assigns unique IDs to these elements (using logic similar to some UI automation agents).
* Draws bounding boxes and numerical labels on the captured screenshot around the identified elements.
* Saves the annotated screenshot to an output directory.

This utility is crucial for developing systems that need to visually understand and interact with specific UI components, forming a basis for more advanced UI automation and AI agents.

---

#### 4. **Example Automation Script (`my_automation.py`)**

📂 [`my_automation.py`](./my_automation.py)

This script serves as a practical example demonstrating how to use the `adb_controller.py` module to create a simple automation workflow. It illustrates:

* Importing and using functions from `adb_controller.py`.
* Sequencing actions like tapping, typing, and swiping with appropriate delays.
* A basic example of navigating an app (e.g., opening search, typing, and swiping).

Users can adapt this script as a template for their own custom automation tasks.

---

### 🚀 Getting Started

1.  **Prerequisites**:
    *   Ensure ADB (Android Debug Bridge) is installed on your system and added to your system's PATH.
    *   Connect your Android device via USB or ensure it's connected via Wi-Fi ADB.
    *   Enable Developer Options and USB Debugging on your Android device.
    *   Authorize the ADB connection on your device when prompted.

2.  **Verify Device Connection**:
    Open a terminal or command prompt and run:
    ```bash
    adb devices
    ```
    You should see your device listed.

3.  **Install Dependencies (if any)**:
    The `annotated_screenshot_generator.py` script uses `pyshine` and `opencv-python`. Install them if you haven't already:
    ```bash
    pip install pyshine opencv-python
    ```

4.  **Running the Scripts**:

    *   **ADB Controller (`adb_controller.py`)**: This script is primarily a module to be imported by other scripts. It can be run directly, but it won't perform any actions on its own without being called from another script (like `my_automation.py` or `interactive_adb.py`).

    *   **Interactive ADB Controller (`interactive_adb.py`)**:
        ```bash
        python new/interactive_adb.py 
        ```
        Then follow the on-screen menu.

    *   **Annotated Screenshot Generator (`annotated_screenshot_generator.py`)**:
        ```bash
        python new/annotated_screenshot_generator.py
        ```
        Check the `output_annotated` directory for the result.

    *   **Example Automation (`my_automation.py`)**:
        ```bash
        python new/my_automation.py
        ```
        Observe your connected device to see the automation steps.

--- 

For `adb_controller.py`, the script itself is a library of functions. To see it in action, you would typically run `interactive_adb.py` or `my_automation.py` which import and use its functions.


