import json
import time
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def get_live_market_data():
    primary_url = "https://abgains.com/index.php?route=all-route"
    fallback_url_1 = "http://webcache.googleusercontent.com/search?q=cache:https://abgains.com/index.php?route=all-route"
    fallback_url_2 = "https://web.archive.org/web/2/https://abgains.com/index.php?route=all-route"
    
    steps_from_30 = {
        25: 75, 26: 25, 27: 10, 30: 0, 
        35: -65, 37: -70, 40: -75, 45: -95, 47: -100, 50: -105,
        60: -125, 70: -155, 80: -180, 90: -200, 100: -210
    }

    current_30_price = None
    status_msg = "System Tripped - All Sources Failed"

    sources_to_try = [
        {"name": "Primary ABGains", "url": primary_url},
        {"name": "Google Cache", "url": fallback_url_1},
        {"name": "Wayback Machine", "url": fallback_url_2}
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        for source in sources_to_try:
            if current_30_price:
                break 
                
            for attempt in range(1, 11):
                try:
                    time.sleep(random.uniform(2.0, 5.0))
                    page.goto(source["url"], timeout=45000, wait_until="domcontentloaded")
                    time.sleep(5) 
                    
                    html_content = page.content()
                    print(f"DEBUG: Attacking {source['name']} - Attempt {attempt}. Page Title: '{page.title()}'")
                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Ruthless Extraction: Find '30' and any number between 300-700
                    rows = soup.find_all('tr')
                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 2:
                            text_c0 = cols[0].text.strip().lower()
                            text_c1 = cols[1].text.strip().replace(',', '')
                            
                            count_matches = re.findall(r'\b30\b', text_c0)
                            price_matches = re.findall(r'\d{3}', text_c1)
                            
                            if count_matches and price_matches:
                                potential_price = int(price_matches[0])
                                if 300 <= potential_price <= 700:
                                    current_30_price = potential_price
                                    status_msg = f"Live Anchor Active ({source['name']})"
                                    print(f"DEBUG: SUCCESS - Extracted {current_30_price} from {source['name']}")
                                    break
                        if current_30_price:
                            break
                except Exception as e:
                    print(f"DEBUG: Blocked on {source['name']} Attempt {attempt} - {e}")
                    continue 
                
                if current_30_price:
                    break
                    
        browser.close()

    full_market_prices = {}
    
    if current_30_price:
        anchors = {c: current_30_price + diff for c, diff in steps_from_30.items()}
        for c in range(25, 101):
            if c >= 93: val = anchors[100]
            elif c >= 83: val = anchors[90]
            elif c >= 73: val = anchors[80]
            elif c >= 63: val = anchors[70]
            elif c >= 51: val = anchors[60]
            elif c >= 48: val = anchors[50]
            elif c >= 46: val = anchors[47]
            elif c >= 43: val = anchors[45]
            elif c >= 38: val = anchors[40]
            elif c >= 36: val = anchors[37]
            elif c >= 33: val = anchors[35]
            elif c >= 28: val = anchors[30]
            elif c == 27: val = anchors[27]
            elif c == 26: val = anchors[26]
            else: val = anchors[25] 
            full_market_prices[str(c)] = val
    else:
        for c in range(25, 101):
            full_market_prices[str(c)] = "Not Available"

    export_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p IST"),
        "status": status_msg,
        "prices": full_market_prices
    }

    with open('prices.json', 'w') as f:
        json.dump(export_data, f, indent=4)

if __name__ == "__main__":
    get_live_market_data()
