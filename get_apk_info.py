from apk_info import get_apk_info

# Get package name and app name
package_name, app_name = get_apk_info("checklist.apk")

print(f"Package Name: {package_name}")
print(f"App Name: {app_name}")

