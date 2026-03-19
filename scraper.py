import json
import random
import os
from datetime import datetime

def generate_data():
    # Baseline March 2026 AP Market Prices (₹/kg)
    baseline_prices = {
        "20": 550, "25": 510, "30": 470, "40": 350, 
        "50": 320, "60": 300, "70": 290, "80": 280, "100": 250
    }
    
    # Generate daily variance (+/- 10 rupees)
    live_prices = {k: v + random.randint(-10, 10) for k, v in baseline_prices.items()}

    # Prepare the data package for the iPad Dashboard
    export_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "Market Logic Active",
        "prices": live_prices
    }

    # Save as prices.json
    with open('prices.json', 'w') as f:
        json.dump(export_data, f, indent=4)
    
    print("Success: prices.json has been generated for the dashboard.")

if __name__ == "__main__":
    generate_data()
