import new.adb_controller as adb
import time

print("Starting custom automation...")

# Get resolution first (optional but good practice for coordinates)
width, height = adb.get_screen_resolution()

if width and height:

    print("Tapping to open search (example coordinates)...")
    adb.tap(width // 2, 150) 
    time.sleep(2) 

    print("Typing 'display'...")
    adb.type_text("display")
    time.sleep(2) # Wait for search results

    print("Swiping down...")
    adb.swipe_down()
    time.sleep(1)

    print("Tapping at (300, 500)...")
    adb.tap(300, 500)
    time.sleep(1)

else:
    print("Could not get screen resolution. Cannot run automation.")

print("Custom automation finished.") 
