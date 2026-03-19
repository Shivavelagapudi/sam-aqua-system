import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def get_live_market_data():
    # Primary Source: AP Market Aggregator
    target_url = "https://abgains.com/index.php?route=all-route" 
    
    prices = {}
    status_msg = "No data available"

    try:
        # Attempt to fetch the live morning report
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, timeout=15, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    count = cols[0].text.strip().replace('C', '').replace(' ', '')
                    price = cols[1].text.strip().replace('₹', '').replace(',', '')
                    if count.isdigit() and price.isdigit():
                        prices[count] = int(price)
            
            if prices:
                status_msg = "Live Market Data Active"
            else:
                status_msg = "Source site loaded but no price table found"
        else:
            status_msg = f"Source site unavailable (Status: {response.status_code})"

    except Exception as e:
        status_msg = f"Fetch Error: {str(e)}"

    # Final Data Package - NO ANCHORS
    export_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p IST"),
        "status": status_msg,
        "prices": prices # This will be {} if the scrape fails
    }

    with open('prices.json', 'w') as f:
        json.dump(export_data, f, indent=4)

if __name__ == "__main__":
    get_live_market_data()
