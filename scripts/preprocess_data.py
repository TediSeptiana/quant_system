import pandas as pd
import os
import argparse

def preprocess_idx_data(input_path, output_path, frequency='daily'):
    """
    Preprocesses IDX trading summary data.

    Args:
        input_path (str): Path to the input CSV file.
        output_path (str): Path to save the processed CSV file.
        frequency (str): Frequency of the data ('daily', 'weekly', 'monthly').
    """
    print(f"Processing {frequency} data from {input_path}...")
    
    try:
        # Load data
        df = pd.read_csv(input_path)
        
        # Clean Date column
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        
        # Ensure numeric columns are actually numeric
        numeric_cols = ['Close', 'OpenPrice', 'High', 'Low', 'Volume', 'Value', 'Frequency']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle missing or zero Close prices
        df = df[df['Close'] > 0]
        
        # Sort by StockCode and Date
        df = df.sort_values(by=['StockCode', 'Date'])
        
        # Check if we have enough data points per stock
        stock_counts = df['StockCode'].value_counts()
        valid_stocks = stock_counts[stock_counts > 1].index
        df = df[df['StockCode'].isin(valid_stocks)]

        if df.empty:
            print(f"Warning: No valid data found for {frequency} after filtering.")
            return None

        # Calculate Returns
        df['Return'] = df.groupby('StockCode')['Close'].pct_change()
        
        # Drop the first row of each stock (NaN return)
        df = df.dropna(subset=['Return'])

        # Save processed data
        print(f"Saving processed data to {output_path}...")
        df.to_csv(output_path, index=False)
        print(f"Successfully processed {frequency} data. Shape: {df.shape}")
        return df

    except Exception as e:
        print(f"Error processing {frequency} data: {e}")
        return None

def generate_monthly_from_daily(daily_output_path, monthly_output_path):
    """
    Generates monthly data by aggregating daily data.
    """
    print(f"Generating monthly data from {daily_output_path}...")
    try:
        df = pd.read_csv(daily_output_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Sort to ensure resampling works correctly
        df = df.sort_values(by=['StockCode', 'Date'])
        
        # Group by StockCode and resample to Month End
        # We take the last value for Close, and sum for Volume/Value etc if needed, 
        # but for Price simulation we mainly need Close.
        
        def resample_stock(group):
            # Resample to month end
            monthly_group = group.set_index('Date').resample('ME').agg({
                'Close': 'last',
                'High': 'max',
                'Low': 'min',
                'OpenPrice': 'first',
                'Volume': 'sum',
                'Value': 'sum',
                'Frequency': 'sum'
            })
            return monthly_group

        monthly_df = df.groupby('StockCode', group_keys=True).apply(resample_stock).reset_index()
        
        # If StockCode is duplicated in columns (possible if reset_index does weird things with existing columns), handle it.
        # But here reset_index on MultiIndex(StockCode, Date) should produce StockCode and Date columns.
        # However, aggregating might have kept 'StockCode' if it was in the agg dict? No, it wasn't.
        # So group_keys=True is the right way.

        
        # Handle zero Close (just in case)
        monthly_df = monthly_df[monthly_df['Close'] > 0]

        # Calculate Monthly Returns
        monthly_df['Return'] = monthly_df.groupby('StockCode')['Close'].pct_change()
        monthly_df = monthly_df.dropna(subset=['Return'])

        print(f"Saving generated monthly data to {monthly_output_path}...")
        monthly_df.to_csv(monthly_output_path, index=False)
        print(f"Successfully generated monthly data. Shape: {monthly_df.shape}")

    except Exception as e:
        print(f"Error generating monthly data: {e}")

def main():
    base_data_dir = r"c:/Users/ASUS/Desktop/File Cepat/quant_system/data/processed"
    input_dir = os.path.join(base_data_dir, "idx_trading_summary")
    
    # Paths
    daily_input = os.path.join(input_dir, "idx_daily.csv")
    weekly_input = os.path.join(input_dir, "idx_weekly.csv")
    
    daily_output = os.path.join(base_data_dir, "idx_daily_cleaned.csv")
    weekly_output = os.path.join(base_data_dir, "idx_weekly_cleaned.csv")
    monthly_output = os.path.join(base_data_dir, "idx_monthly_cleaned.csv")
    
    # 1. Process Daily
    if os.path.exists(daily_input):
        preprocess_idx_data(daily_input, daily_output, "daily")
    else:
        print("Error: Daily input file not found.")

    # 2. Process Weekly
    if os.path.exists(weekly_input):
        preprocess_idx_data(weekly_input, weekly_output, "weekly")
    else:
        print("Error: Weekly input file not found.")

    # 3. Generate Monthly from processed Daily (since raw monthly is snapshot only)
    if os.path.exists(daily_output):
        generate_monthly_from_daily(daily_output, monthly_output)
    else:
        print("Error: Could not generate monthly data because processed daily data is missing.")

if __name__ == "__main__":
    main()
