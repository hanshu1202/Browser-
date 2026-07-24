"""
Visit a URL with a real (non-headless) Chrome window and stay for N seconds.
Optionally logs in first by loading exported session cookies, so no
username/password is ever typed or stored.

Usage:
    python visit_site.py <url> [duration_seconds] [cookies_json_path]

cookies_json_path should point to a JSON file in the format exported by
a browser extension like "Cookie-Editor":
    [
      {"name": "session_id", "value": "...", "domain": ".example.com", "path": "/"},
      ...
    ]

Meant to run on a machine/CI runner that already has a display available
(a real monitor, or a virtual one like Xvfb) at $DISPLAY.
"""

import json
import sys
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def load_cookies(driver, cookies_path: str, base_url: str) -> None:
    """Load exported cookies into the current Selenium session.

    Selenium requires the browser to already be on the target domain
    before cookies for that domain can be added, so we first navigate
    to the site's root, add the cookies, then the caller can navigate
    to the actual target URL.
    """
    with open(cookies_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    parsed = urlparse(base_url)
    root_url = f"{parsed.scheme}://{parsed.netloc}/"
    driver.get(root_url)

    for cookie in cookies:
        # Selenium is picky about a few fields; strip ones it rejects.
        cookie.pop("sameSite", None) if cookie.get("sameSite") not in (
            "Strict", "Lax", "None"
        ) else None
        cookie.pop("id", None)
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Skipped cookie '{cookie.get('name')}': {e}")

    print(f"Loaded {len(cookies)} cookies for {parsed.netloc}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python visit_site.py <url> [duration_seconds] [cookies_json_path]")
        sys.exit(1)

    url = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    cookies_path = sys.argv[3] if len(sys.argv) > 3 else None

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Deliberately NOT passing --headless: this is a real, windowed
    # Chrome instance rendering onto whatever $DISPLAY points to.

    driver = webdriver.Chrome(options=options)
    try:
        if cookies_path:
            print("Logging in via saved cookies...")
            load_cookies(driver, cookies_path, url)

        print(f"Opening {url}")
        driver.get(url)
        print(f"Staying on page for {duration} seconds...")
        time.sleep(duration)
    finally:
        driver.quit()
        print("Done.")


if __name__ == "__main__":
    main()
