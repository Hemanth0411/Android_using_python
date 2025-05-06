import subprocess
import shlex
import time

def run_adb_command(command):
    """Executes an ADB command and returns the output."""
    try:
        print(f"Executing: adb {command}")
        result = subprocess.run(['adb'] + shlex.split(command), capture_output=True, text=True, check=True)
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Error: {result.stderr.strip()}")
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: 'adb' command not found. Make sure ADB is installed and in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stderr: {e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_screen_resolution():
    """Gets the screen resolution of the connected device."""
    output = run_adb_command("shell wm size")
    if output and "Physical size:" in output:
        try:
            resolution_str = output.split("Physical size:")[1].strip()
            width, height = map(int, resolution_str.split('x'))
            print(f"Detected screen resolution: {width}x{height}")
            return width, height
        except Exception as e:
            print(f"Error parsing screen resolution: {e}")
            return None, None
    print("Could not determine screen resolution.")
    return None, None


def type_text(text):
    """Types the given text using ADB."""
    # Replace spaces with %s for ADB command
    escaped_text = text.replace(' ', '%s')
    run_adb_command(f"shell input text '{escaped_text}'") # Use single quotes for safety

def tap(x, y):
    """Taps at the specified coordinates."""
    run_adb_command(f"shell input tap {x} {y}")

def long_tap(x, y, duration_ms=500):
    """Performs a long tap at the specified coordinates."""
    run_adb_command(f"shell input swipe {x} {y} {x} {y} {duration_ms}")

def swipe(start_x, start_y, end_x, end_y, duration_ms=300):
    """Swipes from start coordinates to end coordinates."""
    run_adb_command(f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}")

def swipe_direction(direction, distance_factor=0.5, duration_ms=300):
    """Swipes in a specified direction (up, down, left, right)."""
    width, height = get_screen_resolution()
    if not width or not height:
        print("Cannot perform swipe without screen resolution.")
        return

    center_x = width // 2
    center_y = height // 2
    swipe_distance_y = int(height * distance_factor / 2)
    swipe_distance_x = int(width * distance_factor / 2)

    start_x, start_y, end_x, end_y = 0, 0, 0, 0

    if direction == "up":
        start_x, start_y = center_x, center_y + swipe_distance_y
        end_x, end_y = center_x, center_y - swipe_distance_y
    elif direction == "down":
        start_x, start_y = center_x, center_y - swipe_distance_y
        end_x, end_y = center_x, center_y + swipe_distance_y
    elif direction == "left":
        start_x, start_y = center_x + swipe_distance_x, center_y
        end_x, end_y = center_x - swipe_distance_x, center_y
    elif direction == "right":
        start_x, start_y = center_x - swipe_distance_x, center_y
        end_x, end_y = center_x + swipe_distance_x, center_y
    else:
        print(f"Invalid swipe direction: {direction}")
        return

    # Ensure coordinates are within bounds
    start_x = max(0, min(width - 1, start_x))
    start_y = max(0, min(height - 1, start_y))
    end_x = max(0, min(width - 1, end_x))
    end_y = max(0, min(height - 1, end_y))

    swipe(start_x, start_y, end_x, end_y, duration_ms)

def swipe_up(duration_ms=300):
    swipe_direction("up", duration_ms=duration_ms)

def swipe_down(duration_ms=300):
    swipe_direction("down", duration_ms=duration_ms)

def swipe_left(duration_ms=300):
    swipe_direction("left", duration_ms=duration_ms)

def swipe_right(duration_ms=300):
    swipe_direction("right", duration_ms=duration_ms)


if __name__ == "__main__":
    print("ADB Controller Script")
    print("Make sure a device is connected via ADB.")

    # --- Example Usage ---
    # Uncomment the actions you want to perform

    print("\nGetting screen resolution...")
    width, height = get_screen_resolution()
    if width and height:
        center_x = width // 2
        center_y = height // 2

        # print(f"\nTyping 'hello world'...")
        # type_text("hello world")
        # time.sleep(1)

        # print(f"\nTapping at center ({center_x}, {center_y})...")
        # tap(center_x, center_y)
        # time.sleep(1)

        # print(f"\nLong tapping at (100, 200)...")
        # long_tap(100, 200, duration_ms=1000)
        # time.sleep(1)

        # print("\nSwiping down...")
        # swipe_down()
        # time.sleep(1)

        # print("\nSwiping up...")
        # swipe_up()
        # time.sleep(1)

        # print("\nSwiping left...")
        # swipe_left()
        # time.sleep(1)

        # print("\nSwiping right...")
        # swipe_right()
        # time.sleep(1)

    # else:
    #     print("\nCould not run examples without screen resolution.")

    print("\nScript finished.") 