import json
import time
import random
import re
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests

def get_live_market_data():
    target_url = "https://abgains.com/index.php?route=all-route"
    encoded_url = urllib.parse.quote(target_url)

    steps_from_30 = {
        25: 75, 26: 25, 27: 10, 30: 0, 
        35: -65, 37: -70, 40: -75, 45: -95, 47: -100, 50: -105,
        60: -125, 70: -155, 80: -180, 90: -200, 100: -210
    }

    current_30_price = None
    status_msg = "System Tripped - All Evasion Layers Failed"

    # Multi-layered attack: TLS Impersonation + API Proxies + Caches
    sources = [
        {"name": "Direct TLS Chrome Spoof", "url": target_url, "type": "direct"},
        {"name": "CodeTabs Proxy", "url": f"https://api.codetabs.com/v1/proxy/?quest={target_url}", "type": "proxy"},
        {"name": "AllOrigins API", "url": f"https://api.allorigins.win/get?url={encoded_url}", "type": "json_proxy"},
        {"name": "Google Cache", "url": f"http://webcache.googleusercontent.com/search?q=cache:{target_url}", "type": "direct"}
    ]

    for source in sources:
        if current_30_price: break
        
        for attempt in range(1, 11):
            try:
                time.sleep(random.uniform(2.0, 5.0))
                print(f"DEBUG: Attacking via {source['name']} - Attempt {attempt}")
                
                # curl_cffi fakes the exact network signature of Chrome v110
                response = requests.get(source["url"], impersonate="chrome110", timeout=30)
                
                html_content = ""
                if source["type"] == "json_proxy":
                    data = response.json()
                    html_content = data.get("contents", "")
                else:
                    html_content = response.text

                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Deep Scan extraction logic
                all_rows = soup.find_all('tr')
                for row in all_rows:
                    cells = [c.get_text(strip=True).lower() for c in row.find_all(['td', 'th'])]
                    
                    if len(cells) >= 2:
                        text_c0 = cells[0]
                        text_c1 = cells[1].replace(',', '')
                        
                        count_matches = re.findall(r'\b30\b', text_c0)
                        price_matches = re.findall(r'\d{3}', text_c1)
                        
                        if count_matches and price_matches:
                            potential_price = int(price_matches[0])
                            if 300 <= potential_price <= 750:
                                current_30_price = potential_price
                                status_msg = f"Live Data Extracted ({source['name']})"
                                print(f"DEBUG: SUCCESS - Fetched 30-count at {current_30_price}")
                                break
                if current_30_price: break
            except Exception as e:
                print(f"DEBUG: {source['name']} Attempt {attempt} Failed - {str(e)}")
                continue

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
