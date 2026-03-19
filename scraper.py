import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def get_live_market_data():
    # 1. Target URL for Bhimavaram/AP Market
    target_url = "https://abgains.com/index.php?route=all-route" 
    
    # 2. Your EXACT Sheet Logic (Price jumps/falls relative to 30-count)
    # We use 30-count as the "Master Anchor"
    steps_from_30 = {
        25: 75, 26: 20, 27: 10, 30: 0, 
        35: -65, 37: -70, 40: -75, 45: -95, 47: -100, 50: -105,
        60: -125, 70: -155, 80: -180, 90: -200, 100: -210
    }

    # Fallback price if the internet fails (from your sheet)
    current_30_price = 465 
    status_msg = "Using Manual Sheet Baseline"

    try:
        # User-Agent makes the scraper look like a real browser
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)'}
        response = requests.get(target_url, timeout=15, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                # Target only the Bhimavaram Vannamei section
                if "Bhimavaram" in table.text and "Vannamei" in table.text:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            count_label = cols[0].text.strip()
                            price_val = cols[1].text.strip().replace('₹', '').replace(',', '')
                            
                            # We only care about finding the 30-count "Master Anchor"
                            if "30" in count_label and price_val.isdigit():
                                current_30_price = int(price_val)
                                status_msg = "Live Bhimavaram Anchor Active"
                                break
    except Exception as e:
        status_msg = f"Fetch Error: {str(e)} (Using Baseline)"

    # 3. Build the full 25-100 price list using your Fixed Steps
    full_market_prices = {}
    
    # Pre-calculate the anchor points
    anchors = {c: current_30_price + diff for c, diff in steps_from_30.items()}

    # Map every single count into your specific brackets
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
        else: val = anchors[25] # 25 Count
        
        full_market_prices[str(c)] = val

    # 4. Save to the JSON file for your iPad dashboard
    export_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p IST"),
        "status": status_msg,
        "prices": full_market_prices
    }

    with open('prices.json', 'w') as f:
        json.dump(export_data, f, indent=4)

if __name__ == "__main__":
    get_live_market_data()
