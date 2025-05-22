import argparse
import os
import sys
import time

# python workflow_manager.py "checklist.apk" "Perform a specific action in this app, like searching for X."

# Assuming these helper scripts are in the same directory or accessible in PYTHONPATH
# And that adb_controller.py provides the necessary run_adb_command function
try:
    from apk_info import get_apk_info
    from install_apk import install_apk # This script itself calls run_adb_command
    from check_package import is_package_installed, get_package_version
    # We'll assume adb_controller.py and its run_adb_command are implicitly used by the above
except ImportError as e:
    print(f"Error importing helper modules: {e}")
    print("Please ensure apk_info.py, install_apk.py, check_package.py, and adb_controller.py are accessible.")
    sys.exit(1)

def main_workflow(apk_file_path, task_description, max_install_retries=2, install_wait_time=5):
    """
    Manages the workflow:
    1. Gets APK info (package name, app name).
    2. Installs the APK on the device.
    3. Verifies installation.
    4. Prepares to pass info to the agent (currently prints it).
    """
    print("--- Starting APK Processing and Installation Workflow ---")

    # --- Step 1 & 2: Get APK Info ---
    if not os.path.exists(apk_file_path):
        print(f"Error: APK file not found at '{apk_file_path}'")
        return

    print(f"\n[INFO] Getting information for APK: {apk_file_path}")
    try:
        package_name, app_name = get_apk_info(apk_file_path)
        if not package_name or not app_name: # get_apk_info should raise error, but defensive check
            print("[ERROR] Failed to retrieve valid package name or app name.")
            return
        print(f"[SUCCESS] APK Info Retrieved:")
        print(f"  App Name: {app_name}")
        print(f"  Package Name: {package_name}")
    except Exception as e:
        print(f"[ERROR] Could not get APK info: {e}")
        return

    # --- Step 3: Install APK and Verify ---
    print(f"\n[INFO] Attempting to install '{app_name}' ({package_name})...")
    installed_successfully = False
    for attempt in range(max_install_retries):
        print(f"  Installation attempt {attempt + 1}/{max_install_retries}...")
        if install_apk(apk_file_path): # install_apk prints its own success/failure
            print(f"  Waiting {install_wait_time} seconds for installation to settle...")
            time.sleep(install_wait_time)
            if is_package_installed(package_name):
                installed_version = get_package_version(package_name)
                version_str = f" (Version: {installed_version})" if installed_version else ""
                print(f"[SUCCESS] '{app_name}'{version_str} is installed and verified.")
                installed_successfully = True
                break
            else:
                print(f"  [WARNING] Installation reported success, but package '{package_name}' not found after waiting.")
        else:
            print(f"  [INFO] Installation attempt {attempt + 1} failed.")

        if attempt < max_install_retries - 1:
            print(f"  Retrying in {install_wait_time // 2} seconds...")
            time.sleep(install_wait_time // 2)
        else:
            print(f"[ERROR] Failed to install and verify '{app_name}' after {max_install_retries} attempts.")
            return

    if not installed_successfully:
        # This case should ideally be caught by the loop's exit condition
        print(f"[ERROR] Unknown error: Installation loop completed without success for '{app_name}'.")
        return

    # --- Step 4: Prepare to Pass Info to Agent ---
    print("\n--- Workflow Step 4: Information for Agent ---")
    print("The following information would be passed to the agent:")
    print(f"  App Name to Target: {app_name}")
    print(f"  Package Name to Open: {package_name}")
    print(f"  Task Description: {task_description}")

    # Here, you would eventually call your agent's main function
    # Example (commented out for now):
    # print("\n[INFO] Launching agent (simulated)...")
    # try:
    #     from scripts.self_explorer import main as agent_main # Or however your agent is invoked
    #     # You'll need to modify how agent_main takes these inputs
    #     # agent_main(app_name=app_name, package_name=package_name, task_description=task_description)
    # except ImportError:
    #     print("[ERROR] Could not import agent's main function. Agent step skipped.")
    # except Exception as e:
    #     print(f"[ERROR] Error during (simulated) agent execution: {e}")

    print("\n--- Workflow Completed ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install an APK and prepare for agent interaction.")
    parser.add_argument("apk_path", help="Path to the .apk file.")
    parser.add_argument("task_description", help="The task or description for the agent.")
    parser.add_argument("--retries", type=int, default=2, help="Maximum installation retries.")
    parser.add_argument("--wait", type=int, default=5, help="Wait time in seconds after installation attempt.")

    args = parser.parse_args()

    # Basic validation for apk_path
    if not os.path.isfile(args.apk_path):
        print(f"Error: Provided APK path is not a file or does not exist: {args.apk_path}")
        sys.exit(1)
    if not args.apk_path.lower().endswith(".apk"):
        print(f"Error: Provided file does not seem to be an APK (expected .apk extension): {args.apk_path}")
        sys.exit(1)

    main_workflow(args.apk_path, args.task_description, args.retries, args.wait)