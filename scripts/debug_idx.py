
import requests

url = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&date=20220301"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.idx.co.id/en/market-data/trading-summary/stock-summary/',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest'
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    with open("idx_error.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved response to idx_error.html")
except Exception as e:
    print(f"Error: {e}")
