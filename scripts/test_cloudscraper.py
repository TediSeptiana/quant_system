
import cloudscraper
import json

url = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&date=20220301"

try:
    scraper = cloudscraper.create_scraper()
    print(f"Requesting {url} with cloudscraper...")
    response = scraper.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("Keys:", data.keys())
            if 'data' in data and len(data['data']) > 0:
                print("First item sample:")
                print(json.dumps(data['data'][0], indent=2))
            else:
                print("No data found in 'data' key.")
        except json.JSONDecodeError:
            print("Response is not JSON.")
            print(response.text[:200])
    else:
        print(f"Failed with status: {response.status_code}")
        print(response.text[:200])

except Exception as e:
    print(f"Error: {e}")
