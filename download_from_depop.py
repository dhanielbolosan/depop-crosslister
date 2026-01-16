from playwright.sync_api import sync_playwright
import re
from bs4 import BeautifulSoup
import json
import os
import sys
from urllib.parse import urljoin

def load_depop_products(page):
    print("Loading depop products...")

    try:
        page.wait_for_selector('a[href*="/products/"]', timeout=10000)
    except:
        print("Warning: No initial products found.")
        return False

    previous = 0
    attempts = 0
    max_attempts = 5

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

        current = page.evaluate("() => document.querySelectorAll('a[href*=\"/products/\"]').length")
        
        if current == previous:
            attempts += 1
            print(f"No new items loaded ({attempts}/{max_attempts}). Current number of products: {current}")
        else:
            attempts = 0
            print(f"Loaded {current} products...")
        
        if attempts >= max_attempts:
            break

        previous = current
    
    return True

def fetch_depop_products(username:str):
    base_url = "https://www.depop.com"
    username_url = f"{base_url}/{username}/"

    with sync_playwright() as playwright:
        # Avoid bot detection
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--disable-dev-shm-usage"
            ]
        )

        # Set viewport and user agent
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US"
        )

        print(f"Navigating to {username_url}")
        page = context.new_page()
        page.goto(username_url, wait_until="domcontentloaded", timeout=60000)

        success = load_depop_products(page)
        if not success:
            print(f"Failed to load products.")
            return []

        html = page.content()
        browser.close()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Select all list items first
    all_items = soup.select('li[class*="listItem"]')
    
    products = []
    seen = set()

    for item in all_items:
        # Check if the item is sold
        if item.find(string="Sold"):
            continue

        link = item.select_one('a[href*="/products/"]')
        if link:
            href = link.get('href')
            product_link = urljoin(base_url, href)

            if product_link not in seen:
                seen.add(product_link)
                products.append({
                    "url": product_link,
                })
    
    return products

def save_depop_products(products_list: list, out_dir: str = "data") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "depop_listings.json")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"products": products_list}, f, indent=4)
        return path
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return ""

def main():
    username = input("Enter Depop username: ").strip()
    if not username:
        print("No username provided!")
        sys.exit(1)

    print(f"Loading depop page for: {username}")    
    try:
        products = fetch_depop_products(username)
    except Exception as e:
        print(f"Error fetching depop products: {e}")
        sys.exit(1)
    
    if not products:
        print("No products found!")
        sys.exit(1)
    
    print(f"Found {len(products)} products")
    
    saved_path = save_depop_products(products)
    if saved_path:
        print(f"Successfully saved products to {saved_path}")

if __name__ == "__main__":
    main()