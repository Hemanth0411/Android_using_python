## 📱 Android Automation Utilities

This repository contains a collection of scripts and tools to **automate Android device interactions** using ADB (Android Debug Bridge). These utilities are helpful for:

* UI testing and validation
* App navigation and prototyping
* Building AI agents that simulate human interaction on Android devices

---

### 🔧 Available Scripts

#### 1. **ADB Controller Script**

📂 [`adb_controller.py`](./adb_controller.py)

This script allows you to automate basic touchscreen interactions on a connected Android device. It includes functions to:

* Retrieve device screen resolution
* Tap, long-tap, and swipe across the screen
* Swipe in specific directions (up, down, left, right)
* Type text directly into focused input fields

✅ Robust error handling is included for:

* Device connection issues
* Screen resolution parsing
* ADB availability

🧪 **Example Use Cases**:

* Automate login flows
* Scroll through apps for testing
* Simulate touch interactions for mobile AI agents

---

### 🚀 Getting Started

Make sure ADB is installed and your device is connected via USB or Wi-Fi with USB debugging enabled.

```bash
adb devices
```

Then run the script:

```bash
python adb_controller.py
```


