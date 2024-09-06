import os
import time
import pyautogui
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define the devices and resolutions
devices = {
    'Desktop': ['1920x1080', '1366x768', '1536x864'],
    'Mobile': ['360x640', '414x896', '375x667']
}

browsers = {
    'Chrome': ChromeService(ChromeDriverManager().install()),
    'Firefox': FirefoxService(GeckoDriverManager().install())
}

# Define paths
output_dir = 'screenshots'
sitemap_url = 'https://www.getcalley.com/page-sitemap.xml'
page_load_timeout = 30  # Timeout for page load (in seconds)

def create_folders():
    """Create directories for each device, resolution, and browser."""
    for device in devices:
        for resolution in devices[device]:
            for browser in browsers:
                path = os.path.join(output_dir, device, resolution, browser)
                os.makedirs(path, exist_ok=True)

def capture_screenshots(driver, resolution, browser_name, device):
    """Capture screenshots for a given resolution, browser, and device."""
    try:
        # Set browser window size to the resolution
        width, height = map(int, resolution.split('x'))
        driver.set_window_size(width, height)
        driver.maximize_window()  # Ensure the browser window is maximized
        
        # Open the sitemap URL and wait for the page to load
        driver.get(sitemap_url)
        WebDriverWait(driver, page_load_timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        
        # Define the screenshot filename with timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(output_dir, device, resolution, browser_name, f'Screenshot-{timestamp}.png')
        
        # Capture and overwrite the screenshot
        driver.save_screenshot(screenshot_path)
        print(f'Screenshot saved at {screenshot_path}')
    except Exception as e:
        print(f"Error capturing screenshot for {device} at {resolution} on {browser_name}: {str(e)}")

def record_screen(output_path, duration, browser_window_region=None):
    """Record the screen for a given duration, optionally only a specific region."""
    screen_size = pyautogui.size() if browser_window_region is None else browser_window_region
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (screen_size[2], screen_size[3]))  # Adjust frame size
    
    start_time = time.time()
    while True:
        img = pyautogui.screenshot(region=browser_window_region) if browser_window_region else pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)
        
        if time.time() - start_time > duration:
            break
    
    out.release()
    print(f'Video saved at {output_path}')

def run_tests():
    """Run tests across different browsers and resolutions."""
    create_folders()

    for browser_name, service in browsers.items():
        for device, resolutions in devices.items():
            options = None
            if browser_name == 'Chrome':
                options = ChromeOptions()
            elif browser_name == 'Firefox':
                options = FirefoxOptions()

            driver = None
            try:
                # Initialize the WebDriver for Chrome or Firefox
                driver = webdriver.Chrome(service=service, options=options) if browser_name == 'Chrome' else \
                         webdriver.Firefox(service=service, options=options)

                driver.maximize_window()
                driver.get(sitemap_url)
                
                # Wait for page to load completely
                WebDriverWait(driver, page_load_timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
                time.sleep(5)  # Ensure full page is loaded
                
                # Create separate video path for each browser
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                video_path = f'{browser_name}_test_run_{timestamp}.avi'
                
                # Get browser window position for focused screen recording
                browser_position = pyautogui.getWindowsWithTitle(browser_name)[0].box
                record_screen(video_path, 60, browser_window_region=browser_position)  # 60 seconds video

                for resolution in resolutions:
                    capture_screenshots(driver, resolution, browser_name, device)
            
            except Exception as e:
                print(f"Error in {browser_name}: {str(e)}")
            
            finally:
                if driver:
                    driver.quit()

if __name__ == '__main__':
    run_tests()
