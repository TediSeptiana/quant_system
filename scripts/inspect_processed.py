
import pandas as pd
import os

file_path = r"c:\Users\ASUS\Desktop\File Cepat\quant_system\data\processed\stockbit_sectors_20260130_023651.xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("\nFirst 10 rows:")
    print(df.head(10))
    
    print("\nUnique Sector Names:")
    print(df['Sector Name'].unique())
    
    print("\nUnique Sector URLs:")
    print(df['Sector URL'].unique())

except Exception as e:
    print(f"Error: {e}")
