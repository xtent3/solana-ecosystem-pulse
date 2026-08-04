#!/usr/bin/env python
"""Screenshot premium dashboard using headless Chrome/Edge."""

import sys
import time
from pathlib import Path

# Check if selenium is available
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium no instalado. Instalando...")

if SELENIUM_AVAILABLE:
    def capture_dashboard(output_path="assets/screenshot-dashboard.png", width=1920, height=1080):
        options = Options()
        options.add_argument('--headless')
        options.add_argument(f'--window-size={width},{height}')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        driver = webdriver.Chrome(options=options)
        try:
            html_path = Path("output/premium_dashboard.html").absolute()
            driver.get(f"file:///{html_path}")
            time.sleep(2)  # Wait for animations
            driver.save_screenshot(output_path)
            print(f"✅ Screenshot saved: {output_path}")
            return True
        finally:
            driver.quit()

    if __name__ == "__main__":
        capture_dashboard()
else:
    print("Selenium not available. Alternative: use Edge manually")
