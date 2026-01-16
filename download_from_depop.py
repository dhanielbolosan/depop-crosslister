from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
import sys
from urllib.parse import urljoin

def load_depop_products(page):
    print("Loading depop products...")

    # Wait for products to load, return empty string if none found
    try:
        page.wait_for_selector('a[href*="/products/"]', timeout=10000)
    except:
        print("Warning: No products found.")
        return ""

    # Scroll down to load paginated products if any with 3 max attempts
    prev_count = 0
    attempts = 0
    max_attempts = 3

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

        curr_count = page.evaluate("() => document.querySelectorAll('a[href*=\"/products/\"]').length")
        
        if curr_count == prev_count:
            attempts += 1
        else:
            attempts = 0
            print(f"Found {curr_count} products...")
        
        if attempts >= max_attempts:
            break

        prev_count = curr_count
    
    return page.content()

def fetch_depop_listings(username:str):
    base_url = "https://www.depop.com"
    username_url = f"{base_url}/{username}/"

    # Use playwright to navigate to page and load all depop products
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
        
        print(f"Navigating to {username_url}...")
        page = context.new_page()
        response = page.goto(username_url, wait_until="domcontentloaded", timeout=60000)

        if response.status == 404 or page.locator("text=Page not found").is_visible() or not page.locator('[class*="styles_shopHeader"]').is_visible():
            print(f"Error: '{username}' is not a valid Depop profile!")
            return []

        html = load_depop_products(page)
        
        browser.close()
        context.close()
    
    # Use BeautifulSoup to parse HTML and extract all listed depop products
    soup = BeautifulSoup(html, "html.parser")

    all_products = soup.select('li[class*="listItem"]')
    products = []
    seen = set()

    for product in all_products:
        # Skip sold products
        if product.find(string="Sold"):
            continue

        link = product.select_one('a[href*="/products/"]')
        if link:
            href = link.get('href')
            product_link = urljoin(base_url, href)

            if product_link not in seen:
                seen.add(product_link)
                products.append({
                    "url": product_link,
                })
    
    if not products:
        return []

    print(f"Success: Found {len(products)} product listings")
    return products

def save_depop_products(username: str, products_list: list, out_dir: str = "data") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{username}_depop_listings.json")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"products": products_list}, f, indent=4)
        print(f"Success: Saved product listings to {path}")
        return path
    except Exception as e:
        print(f"Error: Failed to save product listings to JSON: {e}!")
        return ""

def main():
    username = input("Enter Depop username: ").strip()
    if not username:
        print("No username provided!")
        sys.exit(1)

    listings = fetch_depop_listings(username)
    if listings:
        save_depop_products(username, listings)

if __name__ == "__main__":
    main()
