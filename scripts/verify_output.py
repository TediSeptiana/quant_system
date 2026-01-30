
import pandas as pd
import os

file_path = r"c:\Users\ASUS\Desktop\File Cepat\quant_system\data\processed\stock_mapping_final.xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

df = pd.read_excel(file_path)
print("Columns:", df.columns.tolist())
print("-" * 30)
print(df.head(10).to_string())
