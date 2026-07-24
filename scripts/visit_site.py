import json
import sys
import time
import os
import subprocess
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def ollama_signin():
    """Handles the Ollama sign-in and prints the link for the user"""
    print("\n🚀 [AI SESSION] Starting Ollama Sign-in...")
    process = subprocess.Popen(
        ["ollama", "signin"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True,
        bufsize=1
    )

    found_link = None
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                line = process.stderr.readline()
                if not line: break
            
            match = re.search(r'https?://[^\s]+', line)
            if match:
                found_link = match.group(0)
                print(f"\n\n🎯 SIGN-IN LINK FOUND: {found_link}\n\n")
                break
    except Exception as e:
        print(f"❌ Error during sign-in: {e}")

    if found_link:
        print("⏳ Waiting 60 seconds for you to click the link and authorize...")
        time.sleep(60)
        print("✅ Authorization window closed.")
        # Launch the model to activate the session
        subprocess.run(["ollama", "run", "gemma4:cloud"], check=False)
        print("🤖 I AM RUNNING! Model active in session.")
        return True
    return False

def load_cookies(driver, cookies_path: str, base_url: str) -> None:
    with open(cookies_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    parsed = urlparse(base_url)
    root_url = f"{parsed.scheme}://{parsed.netloc}/"
    driver.get(root_url)
    for cookie in cookies:
        cookie.pop("sameSite", None) if cookie.get("sameSite") not in ("Strict", "Lax", "None") else None
        cookie.pop("id", None)
        try: driver.add_cookie(cookie)
        except: pass

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python visit_site.py <url> [duration] [cookies]")
        sys.exit(1)
    
    url = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    cookies_path = sys.argv[3] if len(sys.argv) > 3 else None

    # FIRST: Handle AI Session Authorization
    ollama_signin()

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    try:
        if cookies_path:
            load_cookies(driver, cookies_path, url)
        
        print(f"Opening {url}")
        driver.get(url)
        print(f"Staying on page for {duration} seconds... (Clear CF now!)")
        time.sleep(duration)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
