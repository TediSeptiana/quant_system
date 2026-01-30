

import cloudscraper
import pandas as pd
import time
import datetime
import os
import random
import csv

def run_scraper(start_date="2022-03-01", output_dir="data/processed/idx_trading_summary"):
    scraper = cloudscraper.create_scraper()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    daily_file = os.path.join(output_dir, "idx_daily.csv")
    
    # Check for existing data to resume
    existing_dates = set()
    if os.path.exists(daily_file):
        try:
            # Read just the Date column to find what we have
            df_existing = pd.read_csv(daily_file, usecols=['Date'])
            existing_dates = set(df_existing['Date'].tolist())
            print(f"[Scraper] Found {len(existing_dates)} days already scraped. Resuming...")
        except Exception as e:
            print(f"[Scraper] Error reading existing file: {e}. Starting fresh.")
    
    # Generate date range
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    date_list = pd.date_range(start=start_date, end=end_date)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.idx.co.id/en/market-data/trading-summary/stock-summary/',
        'Origin': 'https://www.idx.co.id',
    }
    
    print(f"[Scraper] Target: {start_date} to {end_date}")
    
    consecutive_failures = 0
    
    for target_date in date_list:
        date_str = target_date.strftime("%Y%m%d")
        display_date = target_date.strftime("%Y-%m-%d")
        
        # Skip if already done
        if display_date in existing_dates:
            continue
            
        # Skip if weekend
        if target_date.weekday() >= 5: 
            continue
            
        url = f"https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&date={date_str}"
        
        print(f"    [Fetch] {display_date} ...", end="", flush=True)
        
        success = False
        retries = 3
        while retries > 0:
            try:
                response = scraper.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        daily_records = data['data']
                        # Add Date column
                        for record in daily_records:
                            record['Date'] = display_date
                        
                        # Append to CSV immediately
                        write_header = not os.path.exists(daily_file)
                        mode = 'a' if not write_header else 'w'
                        
                        # Use pandas to append easily
                        df_temp = pd.DataFrame(daily_records)
                        # Ensure columns are consistent? 
                        # We trust the API returns consistent schema usually, but to be safe we might align cols if needed
                        # For now, just append
                        
                        df_temp.to_csv(daily_file, mode=mode, header=write_header, index=False)
                        
                        print(f" Done. {len(daily_records)} recs.")
                        consecutive_failures = 0
                        success = True
                        break
                    else:
                        print(" No data (Empty).")
                        # Even if empty, mark as done to avoid re-scraping? 
                        # Maybe it's a holiday. We should record it as "checked" or just assume absence of data in CSV means "no data" or "not checked"
                        # To be safe, we skip writing if empty, but next run will check again. 
                        # Optimization: Write a dummy row or keep a "checked_dates.log"
                        # For now, we just skip.
                        consecutive_failures = 0 # It was a success call, just no data
                        success = True
                        break
                elif response.status_code == 404:
                     print(" 404 Not Found.")
                     consecutive_failures = 0
                     success = True
                     break
                else:
                    print(f" Status {response.status_code}. Retry...", end="")
                    retries -= 1
                    time.sleep(2)
            except Exception as e:
                print(f" Error: {e}. Retry...", end="")
                retries -= 1
                time.sleep(2)
        
        if not success:
            print(" Failed after retries.")
            consecutive_failures += 1
            if consecutive_failures >= 5:
                print("[Scraper] Too many consecutive failures. Stopping.")
                break
        else:
             print("") # Newline
             
        # Delay
        time.sleep(random.uniform(1.0, 3.0))

    print("\n[Scraper] Scraping phase complete.")
    process_data(output_dir)

def process_data(output_dir):
    print("[Processing] Generating Weekly and Monthly aggregates...")
    daily_file = os.path.join(output_dir, "idx_daily.csv")
    
    if not os.path.exists(daily_file):
        print(f"[Error] {daily_file} not found.")
        return
        
    try:
        # Load data (might be large, use chunks if needed, but for 4 years it fits in RAM)
        df = pd.read_csv(daily_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Define aggregation
        # Inspect columns to be sure
        # Common: StockCode, Open, High, Low, Close, Volume, Value, Frequency
        available_cols = df.columns.tolist()
        
        agg_rules = {}
        if 'Open' in available_cols: agg_rules['Open'] = 'first'
        if 'High' in available_cols: agg_rules['High'] = 'max'
        if 'Low' in available_cols: agg_rules['Low'] = 'min'
        if 'Close' in available_cols: agg_rules['Close'] = 'last'
        if 'Volume' in available_cols: agg_rules['Volume'] = 'sum'
        if 'Value' in available_cols: agg_rules['Value'] = 'sum'
        if 'Frequency' in available_cols: agg_rules['Frequency'] = 'sum'
        # Also keep Board or Remarks if available? Usually they are static per day, can take 'last' or 'first'
        
        if not agg_rules:
            print("[Error] No OHLCV columns found to aggregate.")
            return

        # Weekly
        print("  - Aggregating Weekly...")
        df_weekly = df.groupby('StockCode').resample('W', on='Date').agg(agg_rules).reset_index()
        df_weekly.to_csv(os.path.join(output_dir, "idx_weekly.csv"), index=False)
        
        # Monthly
        print("  - Aggregating Monthly...")
        df_monthly = df.groupby('StockCode').resample('M', on='Date').agg(agg_rules).reset_index()
        df_monthly.to_csv(os.path.join(output_dir, "idx_monthly.csv"), index=False)
        
        print("[Processing] Done.")
        
    except Exception as e:
        print(f"[Error] Processing failed: {e}")

if __name__ == "__main__":
    run_scraper()
