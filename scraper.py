import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def apply_bhimavaram_pattern(live_anchors):
    # Base anchor prices from your handwritten sheet
    anchors = {
        100: 255, 90: 265, 80: 285, 70: 310, 60: 340,
        50: 360, 47: 365, 45: 370, 40: 390, 37: 395,
        35: 400, 30: 465, 27: 475, 26: 485, 25: 540
    }
    
    # 1. Update anchors with real internet data for today
    for c, p in live_anchors.items():
        if c in anchors:
            anchors[c] = p
            
    # 2. Dynamic Curve Math (Calculating the gaps just like your sheet)
    gap_40_30 = anchors[30] - anchors[40]
    if 35 not in live_anchors: anchors[35] = anchors[40] + round(0.133 * gap_40_30)
    if 37 not in live_anchors: anchors[37] = anchors[40] + round(0.066 * gap_40_30)

    gap_50_40 = anchors[40] - anchors[50]
    if 45 not in live_anchors: anchors[45] = anchors[50] + round(0.333 * gap_50_40)
    if 47 not in live_anchors: anchors[47] = anchors[50] + round(0.166 * gap_50_40)

    gap_30_25 = anchors[25] - anchors[30]
    if 27 not in live_anchors: anchors[27] = anchors[30] + round(0.133 * gap_30_25)
    if 26 not in live_anchors: anchors[26] = anchors[30] + round(0.266 * gap_30_25)

    # 3. Apply your exact brackets to build the full 25-100 list
    full_market_list = {}
    for c in range(25, 101):
        if c >= 93: full_market_list[str(c)] = anchors[100]
        elif c >= 83: full_market_list[str(c)] = anchors[90]
        elif c >= 73: full_market_list[str(c)] = anchors[80]
        elif c >= 63: full_market_list[str(c)] = anchors[70]
        elif c >= 51: full_market_list[str(c)] = anchors[60]  # 61, 62 round down to 60c
        elif c >= 48: full_market_list[str(c)] = anchors[50]  # 48c - 50c
        elif c >= 46: full_market_list[str(c)] = anchors[47]  # 46c - 47c
        elif c >= 43: full_market_list[str(c)] = anchors[45]  # 43c - 45c
        elif c >= 38: full_market_list[str(c)] = anchors[40]  # 38c - 42c
        elif c >= 36: full_market_list[str(c)] = anchors[37]  # 36c - 37c
        elif c >= 33: full_market_list[str(c)] = anchors[35]  # 33c - 35c
        elif c >= 28: full_market_list[str(c)] = anchors[30]  # 28c - 32c
        elif c == 27: full_market_list[str(c)] = anchors[27]
        elif c == 26: full_market_list[str(c)] = anchors[26]
        elif c == 25: full_market_list[str(c)] = anchors[25]
        
    return full_market_list

def get_live_market_data():
    target_url = "https://abgains.com/index.php?route=all-route" 
    live_anchors = {}
    status_msg = "No data available"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, timeout=15, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                if "Bhimavaram" in table.text and "Vannamei" in table.text:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            count = cols[0].text.strip().replace('C', '').replace(' ', '')
                            price = cols[1].text.strip().replace('₹', '').replace(',', '')
                            if count.isdigit() and price.isdigit():
                                live_anchors[int(count)] = int(price)
            if live_anchors:
                status_msg = "Live AP Market Logic Active"
    except Exception as e:
        status_msg = f"Using Manual Base Pattern"

    # Process the live data through the custom pattern
    final_prices = apply_bhimavaram_pattern(live_anchors)

    export_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p IST"),
        "status": status_msg,
        "prices": final_prices
    }

    with open('prices.json', 'w') as f:
        json.dump(export_data, f, indent=4)

if __name__ == "__main__":
    get_live_market_data()
