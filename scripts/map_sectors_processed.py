
import pandas as pd
import os
import re

input_path = r"c:\Users\ASUS\Desktop\File Cepat\quant_system\data\processed\stockbit_sectors_20260130_023651.xlsx"
output_path = r"c:\Users\ASUS\Desktop\File Cepat\quant_system\data\processed\stock_mapping_final.xlsx"

def classify_item(row):
    text = str(row['Sector Name']).strip()
    url = str(row['Sector URL']).strip()
    
    classification = {
        'Type': 'Unknown',
        'Value': text
    }
    
    url_lower = url.lower()
    
    if '/listing-board/' in url_lower or 'papan' in text.lower():
        classification['Type'] = 'Board'
    elif '/indeks/' in url_lower:
        if 'ihsg' in text.lower():
             classification['Type'] = 'Index IHSG'
        else:
             classification['Type'] = 'Index'
             
    elif '/sector/' in url_lower or '/sub-sector/' in url_lower or '/industry/' in url_lower or '/sub-industry/' in url_lower:
        classification['Type'] = 'Sector'
    elif '/notasi/' in url_lower or 'remark' in text.lower() or 'suspend' in text.lower():
        classification['Type'] = 'Status'
    elif '/shariah/' in url_lower or 'syariah' in text.lower():
        classification['Type'] = 'Shariah'
    else:
        if text.isupper() and len(text) < 10:
             classification['Type'] = 'Index'
        elif any(x in text.lower() for x in ['sector', 'trade', 'services', 'finance', 'mining', 'basic', 'consumer', 'property', 'infrastruct']):
             classification['Type'] = 'Sector'
        else:
             classification['Type'] = 'Sector'

    return classification

def run():
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    print(f"Reading {input_path}...")
    df = pd.read_excel(input_path)
    
    # Process each row
    mapped_data = []
    
    # We want to group by 'Kode Saham' eventually
    # First, classify each row
    df['Type'] = df.apply(lambda row: classify_item(row)['Type'], axis=1)
    
    # Pivot logic
    # We want one row per stock
    unique_stocks = df['Kode Saham'].unique()
    print(f"Found {len(unique_stocks)} unique stocks.")
    
    final_rows = []
    
    for stock in unique_stocks:
        stock_df = df[df['Kode Saham'] == stock]
        
        row_data = {
            'Kode Saham': stock,
            'Board': None,
            'Sector': [],
            'Index IHSG': None,
            'Regional Index': [], # If any
            'Indices': [],
            'Status': [],
            'Shariah': 'No'
        }
        
        for _, item in stock_df.iterrows():
            itype = item['Type']
            val = item['Sector Name']
            
            if itype == 'Board':
                row_data['Board'] = val
            elif itype == 'Index IHSG':
                row_data['Index IHSG'] = val
            elif itype == 'Index':
                row_data['Indices'].append(val)
            elif itype == 'Sector':
                row_data['Sector'].append(val)
            elif itype == 'Status':
                row_data['Status'].append(val)
            elif itype == 'Shariah':
                row_data['Shariah'] = 'Yes'
        
        # Clean up lists
        row_data['Sector'] = ', '.join(sorted(list(set(row_data['Sector']))))
        row_data['Status'] = ', '.join(sorted(list(set(row_data['Status']))))
        row_data['Indices'] = ', '.join(sorted(list(set(row_data['Indices']))))
        
        final_rows.append(row_data)
        
    final_df = pd.DataFrame(final_rows)
    
    # Reorder columns for better readability
    cols = ['Kode Saham', 'Board', 'Sector', 'Status', 'Shariah', 'Index IHSG', 'Indices']
    final_df = final_df[cols]
    
    print(f"Saving mapped data to {output_path}...")
    final_df.to_excel(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    run()
