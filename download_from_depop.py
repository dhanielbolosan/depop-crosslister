import json
import os
import sys
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TIMEOUT_LONG = 60000
TIMEOUT_SHORT = 10000
TIMEOUT_SCROLL = 3000

def get_listing_urls(page, base_url):
    print("Loading depop products...")

    # Wait for products to load, return empty if none found
    try:
        page.wait_for_selector('a[href*="/products/"]', timeout=TIMEOUT_SHORT)
    except:
        print("Warning: No products found on profile.")
        return []

    # Scroll down to load paginated products if any with 3 max attempts
    prev_count = 0
    attempts = 0
    max_attempts = 3

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(TIMEOUT_SCROLL)

        curr_count = page.evaluate("() => document.querySelectorAll('a[href*=\"/products/\"]').length")
        
        if curr_count == prev_count:
            attempts += 1
        else:
            attempts = 0
            print(f"Found {curr_count} products...")
        
        if attempts >= max_attempts:
            break

        prev_count = curr_count
    
    # Extract links after full load
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    products = []
    seen = set()

    for product in soup.select('li[class*="listItem"]'):
        if product.find(string="Sold"):
            continue

        url_tag = product.select_one('a[href*="/products/"]')

        if url_tag:
            href = url_tag.get('href')
            full_url = urljoin(base_url, href)

            if full_url not in seen:
                seen.add(full_url)
                products.append(full_url)
    
    return products

def get_listing_details(page, product_url):
    print(f"Loading product details for {product_url}...")

    try: 
        # 1. Navigate to the product page first
        response = page.goto(product_url, wait_until="domcontentloaded", timeout=TIMEOUT_LONG)

        # 2. Validate if product page exists
        if response.status == 404 or page.locator("text=Page not found").is_visible():
            print(f"Error: '{product_url}' is not a valid Depop product!")
            return None
    
        # 3. Wait for content to load
        try:
            page.wait_for_selector('div[data-testid="productPrimaryAttributes"]', timeout=TIMEOUT_SHORT//2)
        except:
            pass

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.select_one('h1[class*="styles_title"]')
        title = title_tag.get_text(strip=True) if title_tag else ""

        price_tag = soup.select_one('p[aria-label="Price"]')
        price = price_tag.get_text(strip=True) if price_tag else ""

        desc_tag = soup.select_one('p[class*="styles_textWrapper"]')
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        attr_container = soup.select('div[data-testid="productPrimaryAttributes"] p')
        attributes = [attr.get_text(strip=True) for attr in attr_container]
    
        size = attributes[0] if len(attributes) > 0 else ""
        condition = attributes[1] if len(attributes) > 1 else ""
    
        brand_tag = soup.select_one('div[data-testid="productPrimaryAttributes"] a')
        brand = brand_tag.get_text(strip=True) if brand_tag else ""

        images = []
        for img in soup.select('div[class*="styles_imageContainer"] img'):
            src = img.get('src')
            if src and "media-photos.depop.com" in src and src not in images:
                images.append(src)

        return {
            "url": product_url,
            "title": title,
            "price": price,
            "description": description,
            "size": size,
            "condition": condition,
            "brand": brand,
            "images": images
        }

    except Exception as e:
        print(f"Error: Failed to load product details for '{product_url}': {e}")
        return None

def scrape_depop_profile(username:str):
    base_url = "https://www.depop.com"
    profile_url = f"{base_url}/{username}/"
    all_product_details = []

    # Use playwright to navigate to page and load all depop products
    with sync_playwright() as playwright:

        # Avoid bot detection
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled", 
            ]
        )

        # Set viewport and user agent
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US"
        )
        
        print(f"Navigating to {profile_url}...")
        page = context.new_page()
        response = page.goto(profile_url, wait_until="domcontentloaded", timeout=TIMEOUT_LONG)

        if response.status == 404 or page.locator("text=Page not found").is_visible() or not page.locator('[class*="styles_shopHeader"]').is_visible():
            print(f"Error: '{username}' is not a valid Depop profile!")
            return []

        product_urls = get_listing_urls(page, base_url)

        for i, url in enumerate(product_urls):
            print(f"[{i+1}/{len(product_urls)}] Extracting {url} ...")
            details = get_listing_details(page, url)

            if details:
                all_product_details.append(details)
            time.sleep(1)
        
        browser.close()
        context.close()
    
    return all_product_details

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

    listings = scrape_depop_profile(username)
    if listings:
        save_depop_products(username, listings)

if __name__ == "__main__":
    main()
