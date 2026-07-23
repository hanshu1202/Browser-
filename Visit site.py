"""
Visit a URL with a real (non-headless) Chrome window and stay for N seconds.

Usage:
    python visit_site.py <url> [duration_seconds]

Meant to run on a machine/CI runner that already has a display available
(a real monitor, or a virtual one like Xvfb) at $DISPLAY.
"""

import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python visit_site.py <url> [duration_seconds]")
        sys.exit(1)

    url = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Deliberately NOT passing --headless: this is a real, windowed
    # Chrome instance rendering onto whatever $DISPLAY points to.

    driver = webdriver.Chrome(options=options)
    try:
        print(f"Opening {url}")
        driver.get(url)
        print(f"Staying on page for {duration} seconds...")
        time.sleep(duration)
    finally:
        driver.quit()
        print("Done.")


if __name__ == "__main__":
    main()
