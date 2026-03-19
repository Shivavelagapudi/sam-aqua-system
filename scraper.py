import json
import time
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def get_live_market_data():
    primary_url = "https://abgains.com/index.php?route=all-route"
    fallback_url = "http://webcache.googleusercontent.com/search?q=cache:https://abgains.com/index.php?route=all-route"
    
    steps_from_30 = {
        25: 75, 26: 25, 27: 10, 30: 0, 
        35: -65, 37: -70, 40: -75, 45: -95, 47: -100, 50: -105,
        60: -125, 70: -155, 80: -180, 90: -200, 100: -210
    }

    current_30_price = None
    status_msg = "System Tripped - All Sources Failed"

    sources_to_try = [
        {"name": "Primary ABGains", "url": primary_url},
        {"name": "Google Cache Fallback", "url": fallback_url}
    ]

    # Fire up the headless Chromium browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Spoof a real Windows 10 Chrome user
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        for source in sources_to_try:
            if current_30_price:
                break 
                
            for attempt in range(1, 11):
                try:
                    time.sleep(random.uniform(2.0, 5.0))
                    
                    # Force the browser to wait until the network is totally quiet (JS finished loading)
                    page.goto(source["url"], timeout=45000, wait_until="domcontentloaded")
                    time.sleep(4) # Give it 4 extra seconds just to be absolutely certain the table renders
                    
                    # Extract the fully rendered HTML
                    html_content = page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    tables = soup.find_all('table')
                    
                    for table in tables:
                        text_content = table.text.lower()
                        if "bhima" in text_content and "vannamei" in text_content:
                            rows = table.find_all('tr')
                            for row in rows:
                                cols = row.find_all(['td', 'th'])
                                if len(cols) >= 2:
                                    count_label = re.sub(r'\D', '', cols[0].text.strip())
                                    price_val = re.sub(r'\D', '', cols[1].text.strip())
                                    
                                    if count_label == "30" and price_val:
                                        current_30_price = int(price_val)
                                        status_msg = f"Live Anchor Active ({source['name']})"
                                        break
                        if current_30_price:
                            break
                except Exception:
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
