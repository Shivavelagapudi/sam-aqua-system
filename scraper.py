import json
import time
import random
import re
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup

def get_live_market_data():
    # 1. Primary Target
    primary_url = "https://abgains.com/index.php?route=all-route"
    
    # 2. The Fallback Target: Google's cached snapshot of the site (bypasses firewalls)
    fallback_url = "http://webcache.googleusercontent.com/search?q=cache:https://abgains.com/index.php?route=all-route"
    
    steps_from_30 = {
        25: 75, 26: 25, 27: 10, 30: 0, 
        35: -65, 37: -70, 40: -75, 45: -95, 47: -100, 50: -105,
        60: -125, 70: -155, 80: -180, 90: -200, 100: -210
    }

    current_30_price = None
    status_msg = "System Tripped - All Sources Failed"

    # Create the advanced browser-mimicking scraper
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    # Order of attack: Hit the primary site, if it fails, hit the Google Cache fallback
    sources_to_try = [
        {"name": "Primary ABGains", "url": primary_url},
        {"name": "Google Cache Fallback", "url": fallback_url}
    ]

    for source in sources_to_try:
        if current_30_price:
            break # Stop attacking if we already got the data
            
        # Try 10 times per source
        for attempt in range(1, 11):
            try:
                # Random delay to trick anti-bot security
                time.sleep(random.uniform(2.0, 5.0))
                
                # Extended timeout to give slow Indian servers time to respond
                response = scraper.get(source["url"], timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    tables = soup.find_all('table')
                    
                    for table in tables:
                        text_content = table.text.lower()
                        # Fuzzy match to account for typos on their end
                        if "bhima" in text_content and "vannamei" in text_content:
                            rows = table.find_all('tr')
                            for row in rows:
                                cols = row.find_all(['td', 'th'])
                                if len(cols) >= 2:
                                    # Strip out everything except the pure numbers
                                    count_label = re.sub(r'\D', '', cols[0].text.strip())
                                    price_val = re.sub(r'\D', '', cols[1].text.strip())
                                    
                                    if count_label == "30" and price_val:
                                        current_30_price = int(price_val)
                                        status_msg = f"Live Anchor Active ({source['name']})"
                                        break
                        if current_30_price:
                            break
                
                if current_30_price:
                    break # Success! Break out of the 10-attempt loop
                    
            except Exception:
                continue # If it crashes, silently ignore it and try the next attempt

    # Math Logic to calculate the rest of the board
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
        # The ultimate catch-all: Only triggers if the main site AND Google are dead
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
