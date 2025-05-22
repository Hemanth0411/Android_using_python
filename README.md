## 📱 Android Automation and Testing Utilities

This repository contains a comprehensive suite of tools for **Android device automation, testing, and UI analysis** using ADB (Android Debug Bridge). These utilities support:

* UI testing and validation
* APK installation and verification
* App navigation automation
* Grid-based UI analysis
* Visual AI assistance for UI interaction
* Screenshot analysis and annotation
* APK information extraction

---

### 🔧 Core Utilities

#### 1. **ADB Controller (`adb_controller.py`)**

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

#### 3. **Workflow Manager (`workflow_manager.py`)**

📂 [`workflow_manager.py`](./workflow_manager.py)

Manages the complete workflow for APK installation and preparation:
* Gets APK information (package name, app name)
* Installs APK on the device with retries
* Verifies installation
* Prepares information for agent interaction
* Supports command-line arguments for customization

Usage:
```bash
python workflow_manager.py "path/to/app.apk" "Task description" --retries 2 --wait 5
```

#### 4. **Grid Generator (`test_grid_generator.py`)**

📂 [`test_grid_generator.py`](./test_grid_generator.py)

Creates a grid overlay on device screenshots for precise UI analysis:
* Captures device screenshots
* Generates numbered grid cells
* Calculates cell boundaries and centers
* Provides quadrant information for precise tapping
* Exports grid information in JSON format

#### 5. **Points Generator (`test_points.py`)**

📂 [`test_points.py`](./test_points.py)

Generates a custom points layout for UI interaction:
* Creates labeled interaction points
* Supports primary and secondary point labeling
* Provides precise coordinate information
* Exports points data in JSON format

---

### 📸 Visual Analysis Tools

#### 1. **Annotated Screenshot Generator (`annotated_screenshot_generator.py`)**

📂 [`annotated_screenshot_generator.py`](./annotated_screenshot_generator.py)

Enhanced screenshot annotation tool:
* Captures screen and UI hierarchy
* Identifies clickable and focusable elements
* Generates unique element IDs
* Creates annotated screenshots with bounding boxes
* Supports multiple annotation modes (clickable, focusable)

#### 2. **Utils (`utils.py`)**

📂 [`utils.py`](./utils.py)

Utility functions for image processing and display:
* Color-coded console output
* Image annotation utilities
* Text overlay with background
* Image encoding utilities
* Bounding box drawing functions

---

### 📦 APK Management Tools

#### 1. **APK Information Suite**

A collection of tools for APK handling:

📂 [`apk_info.py`](./apk_info.py)
* Main APK information extractor
* Package name and app name extraction
* Automatic aapt detection
* Clean information formatting

📂 [`install_apk.py`](./install_apk.py)
* APK installation handler
* Installation verification
* Error handling and reporting

📂 [`check_package.py`](./check_package.py)
* Package installation verification
* Version information retrieval
* Package presence checking

📂 [`apk_installer_checker.py`](./apk_installer_checker.py)
* Combined installation and verification
* Multi-retry support
* Detailed status reporting

---

### 🤖 AI Integration Tools

Several utilities for AI-assisted UI interaction:

* **Ratio Analysis** (`ratio.py`, `new_ratio.py`)
* **Gemini Integration** (`gemini.py`)
* **OpenAI Integration** (`openai123.py`)

These tools provide various approaches to AI-assisted UI element detection and interaction.

---

### 🚀 Getting Started

1. **Prerequisites**:
    * Ensure ADB (Android Debug Bridge) is installed on your system and added to your system's PATH.
    * Connect your Android device via USB or ensure it's connected via Wi-Fi ADB.
    * Enable Developer Options and USB Debugging on your Android device.
    * Authorize the ADB connection on your device when prompted.
    * Install Android SDK for APK information extraction features.

2. **Project Setup**:
```bash
git clone <repository-url>
cd <project-directory>
pip install -r requirements.txt
```

3. **Environment Configuration**:
* Configure API keys for AI services (if using AI integration)
* Set up Android SDK path for APK tools
* Ensure ADB is in system PATH

4. **Basic Usage**:
Start with the interactive controller:
```bash
python interactive_adb.py
```

Or run a complete APK workflow:
```bash
python workflow_manager.py "path/to/app.apk" "Install and prepare app"
```

---

### 📝 Notes

* Most scripts support both command-line and programmatic usage
* AI integration requires appropriate API keys
* Error handling and logging is implemented throughout
* Grid and point generation tools create JSON output for automation use
* Screenshot tools support various annotation modes

For detailed API documentation and examples, see individual script headers.


