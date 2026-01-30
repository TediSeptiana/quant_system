
import pandas as pd
import time
import random
import requests
import os

def run(file_path):
    """
    Reads a stock summary Excel file, extracts stock codes, and visits their Stockbit pages.
    """
    if not os.path.exists(file_path):
        print(f"[Error] File not found: {file_path}")
        return

    print(f"[Scraper] Reading file: {file_path}")
    
    try:
        # Load the Excel file
        # Attempt to find the header row by looking for "Kode Saham"
        df = pd.read_excel(file_path, header=None)
        
        header_row_index = -1
        code_col_index = -1
        
        # Search for "Kode Saham" in the first few rows
        for r_idx, row in df.head(10).iterrows():
            for c_idx, cell in enumerate(row):
                if isinstance(cell, str) and "Kode Saham" in cell:
                    header_row_index = r_idx
                    code_col_index = c_idx
                    break
            if header_row_index != -1:
                break
        
        if header_row_index == -1:
            print("[Scraper] Could not find column 'Kode Saham'. Defaulting to 1st column, 2nd row as requested.")
            # Fallback: Assume header is row 1 (index 1), data starts row 2
            df = pd.read_excel(file_path, header=1)
            # Use the first column
            stock_codes = df.iloc[:, 0].dropna().astype(str).tolist()
        else:
            print(f"[Scraper] Found 'Kode Saham' at Row {header_row_index}, Column {code_col_index}")
            df = pd.read_excel(file_path, header=header_row_index)
            # Get the column name from the found index
            col_name = df.columns[code_col_index]
            stock_codes = df[col_name].dropna().astype(str).tolist()

        print(f"[Scraper] Found {len(stock_codes)} stock codes.")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        results = []

        try:
            for code in stock_codes:
                code = code.strip()
                if not code:
                    continue
                    
                url = f"https://stockbit.com/symbol/{code}"
                print(f"[Scraper] Checking: {code} -> {url}")
                
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        print(f"    [Success] Status {response.status_code}")
                        
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        catalog_links = soup.select('a[href^="/catalog/"]')
                        
                        if catalog_links:
                            for link in catalog_links:
                                text = link.get_text(strip=True)
                                href = link.get('href')
                                print(f"    [Data] Found Sector: {text} | URL: {href}")
                                results.append({
                                    'Kode Saham': code,
                                    'Sector Name': text,
                                    'Sector URL': href,
                                    'Scraped At': time.strftime("%Y-%m-%d %H:%M:%S")
                                })
                        else:
                            print("    [Info] No catalog/sector information found.")
                            # Append with empty sector info if needed to track checked stocks
                            results.append({
                                'Kode Saham': code,
                                'Sector Name': None,
                                'Sector URL': None,
                                'Scraped At': time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                    else:
                        print(f"    [Warning] Status {response.status_code}")
                except Exception as e:
                    print(f"    [Error] Failed to connect: {e}")
                
                # Rate limiting
                sleep_time = random.uniform(2, 5)
                # print(f"    [Sleep] Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\n[Scraper] Interrupted by user. Saving collected data...")

        # Save results
        if results:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'data', 'processed')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'stockbit_sectors_{time.strftime("%Y%m%d_%H%M%S")}.xlsx')
            
            print(f"[Scraper] Saving {len(results)} rows to {output_file}...")
            df_results = pd.DataFrame(results)
            df_results.to_excel(output_file, index=False)
            print("[Scraper] Save complete.")
        else:
            print("[Scraper] No data collected.")

    except Exception as e:
        print(f"[Error] An error occurred during execution: {e}")

if __name__ == "__main__":
    # Test run
    test_path = r"c:\Users\ASUS\Desktop\File Cepat\quant_system\data\raw\Ringkasan Saham-20260112.xlsx"
    run(test_path)
