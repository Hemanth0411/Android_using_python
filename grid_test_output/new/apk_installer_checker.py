import os
import sys
import time
from adb_controller import run_adb_command
from apk_info import get_apk_info
from install_apk import install_apk
from check_package import is_package_installed, get_package_version

def install_and_verify_apk(apk_path, max_retries=2, wait_time=5):
    """
    Install an APK and verify its installation with retries.
    
    Args:
        apk_path (str): Path to the APK file
        max_retries (int): Maximum number of installation attempts
        wait_time (int): Time to wait between checks in seconds
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    if not os.path.exists(apk_path):
        print(f"Error: APK file not found at {apk_path}")
        return False

    # Get APK info first
    try:
        package_name, app_name = get_apk_info(apk_path)
        print(f"\nAPK Information:")
        print(f"Package Name: {package_name}")
        print(f"App Name: {app_name}")
    except Exception as e:
        print(f"Error getting APK info: {e}")
        return False

    # Try installation with verification
    for attempt in range(max_retries):
        print(f"\nInstallation attempt {attempt + 1}/{max_retries}")
        
        # Install the APK
        if install_apk(apk_path):
            print(f"\nWaiting {wait_time} seconds for installation to complete...")
            time.sleep(wait_time)
            
            # Verify installation
            if is_package_installed(package_name):
                version = get_package_version(package_name)
                if version:
                    print(f"Successfully installed {app_name} (version: {version})")
                return True
            else:
                print("Installation verification failed.")
                if attempt < max_retries - 1:
                    print("Retrying installation...")
                continue
        else:
            print("Installation failed.")
            if attempt < max_retries - 1:
                print("Retrying installation...")
            continue
    
    print("\nFailed to install and verify APK after all attempts.")
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python apk_installer_checker.py <path_to_apk>")
        sys.exit(1)
    
    apk_path = sys.argv[1]
    success = install_and_verify_apk(apk_path)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 