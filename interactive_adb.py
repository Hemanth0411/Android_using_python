import adb_controller as adb
import sys
import time

def get_coordinates(prompt):
    """Prompts the user for x, y coordinates and validates them."""
    while True:
        try:
            coord_input = input(prompt)
            if ',' not in coord_input:
                print("Invalid format. Please enter as 'x,y'.")
                continue
            x_str, y_str = coord_input.split(',')
            x = int(x_str.strip())
            y = int(y_str.strip())
            return x, y
        
        except ValueError:
            print("Invalid input. Please enter numeric coordinates separated by a comma (e.g., 100,200).")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None

def main():
    print("Interactive ADB Controller")
    print("=========================")
    print("Ensure an Android device is connected via ADB and authorized.")
    
    print("\nChecking device connection and resolution...")
    width, height = adb.get_screen_resolution()
    if not width or not height:
        print("Warning: Could not get screen resolution. Some features might be limited.")

    else:
        print(f"Device found with resolution: {width}x{height}")

    while True:
        print("\nAvailable Actions:")
        print("  1: Type text")
        print("  2: Tap coordinates (x,y)")
        print("  3: Swipe Up")
        print("  4: Swipe Down")
        print("  5: Swipe Left")
        print("  6: Swipe Right")
        print("  7: Long Tap coordinates (x,y)")
        print("  8: Custom Swipe (start_x,start_y end_x,end_y)")
        print("  9: Press Home")
        print("  10: Press Back")
        print("  11: Press Enter/Go")
        print("  12: Volume Up")
        print("  13: Volume Down")
        print("  14: Open Notifications")
        print("  15: Press Power")
        print("  16: Press Delete/Backspace")
        print("  17: Press Tab")
        print("  18: Press Media Play/Pause")
        print("  19: Press Media Next")
        print("  20: Press Media Previous")
        print("  21: Press Mute")
        print("  22: Press App Switch (Recents)")
        print("  q: Quit")

        choice = input("Enter action number (or 'q' to quit): ").strip().lower()

        if choice == 'q':
            print("Exiting...")
            sys.exit()
        elif choice == '1':
            text_to_type = input("Enter text to type: ")
            adb.type_text(text_to_type)
            print(f"Typed: '{text_to_type}'")
        elif choice == '2':
            x, y = get_coordinates("Enter coordinates to tap (e.g., 100,200): ")
            if x is not None and y is not None:
                adb.tap(x, y)
                print(f"Tapped at ({x},{y})")
        elif choice == '3':
            adb.swipe_up()
            print("Swiped Up")
        elif choice == '4':
            adb.swipe_down()
            print("Swiped Down")
        elif choice == '5':
            adb.swipe_left()
            print("Swiped Left")
        elif choice == '6':
            adb.swipe_right()
            print("Swiped Right")
        elif choice == '7':
            x, y = get_coordinates("Enter coordinates for long tap (e.g., 100,200): ")
            if x is not None and y is not None:
                duration_input = input("Enter duration in milliseconds (default 500): ")
                try:
                    duration_ms = int(duration_input) if duration_input else 500
                except ValueError:
                    print("Invalid duration, using default 500ms.")
                    duration_ms = 500
                adb.long_tap(x, y, duration_ms=duration_ms)
                print(f"Long tapped at ({x},{y}) for {duration_ms}ms")
        elif choice == '8':
             print("Enter start coordinates first.")
             start_x, start_y = get_coordinates("Enter start coordinates (e.g., 100,200): ")
             if start_x is not None and start_y is not None:
                 print("\nEnter end coordinates now.")
                 end_x, end_y = get_coordinates("Enter end coordinates (e.g., 100,800): ")
                 if end_x is not None and end_y is not None:
                     duration_input = input("Enter duration in milliseconds (default 300): ")
                     try:
                         duration_ms = int(duration_input) if duration_input else 300
                     except ValueError:
                         print("Invalid duration, using default 300ms.")
                         duration_ms = 300
                     adb.swipe(start_x, start_y, end_x, end_y, duration_ms=duration_ms)
                     print(f"Swiped from ({start_x},{start_y}) to ({end_x},{end_y}) in {duration_ms}ms")
        elif choice == '9':
            adb.press_home()
            print("Pressed Home")
        elif choice == '10':
            adb.press_back()
            print("Pressed Back")
        elif choice == '11':
            adb.press_enter()
            print("Pressed Enter/Go")
        elif choice == '12':
            adb.volume_up()
            print("Volume Up")
        elif choice == '13':
            adb.volume_down()
            print("Volume Down")
        elif choice == '14':
            adb.open_notifications()
            print("Opened Notifications")
        elif choice == '15':
            adb.press_power()
            print("Pressed Power")
        elif choice == '16':
            adb.press_delete()
            print("Pressed Delete/Backspace")
        elif choice == '17':
            adb.press_tab()
            print("Pressed Tab")
        elif choice == '18':
            adb.press_media_play_pause()
            print("Pressed Media Play/Pause")
        elif choice == '19':
            adb.press_media_next()
            print("Pressed Media Next")
        elif choice == '20':
            adb.press_media_previous()
            print("Pressed Media Previous")
        elif choice == '21':
            adb.press_mute()
            print("Pressed Mute")
        elif choice == '22':
            adb.press_app_switch()
            print("Pressed App Switch (Recents)")
        else:
            print("Invalid choice. Please try again.")

        time.sleep(0.5) 

if __name__ == "__main__":
    main() 