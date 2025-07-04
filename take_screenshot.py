import pyautogui
import time

# Wait a few seconds to allow you to focus the Streamlit window
print("You have 5 seconds to focus the Streamlit UI window...")
time.sleep(5)

# Take screenshot
screenshot = pyautogui.screenshot()
screenshot.save("screenshot.png")
print("Screenshot saved as screenshot.png")
