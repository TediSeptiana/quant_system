
import requests
import json

url = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&date=20220301"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.idx.co.id/en/market-data/trading-summary/stock-summary/',
    'Origin': 'https://www.idx.co.id',
    'Accept': '*/*'
}

try:
    print(f"Requesting {url}...")
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Keys:", data.keys())
        if 'data' in data and len(data['data']) > 0:
            print("First item sample:")
            print(json.dumps(data['data'][0], indent=2))
        else:
            print("No data found in 'data' key.")
    else:
        print(f"Response text: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
