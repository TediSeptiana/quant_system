import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

def run_monte_carlo(data_path, stock_code, simulations=1000, time_horizon=252, frequency='daily'):
    """
    Runs a Monte Carlo simulation for a given stock using Geometric Brownian Motion.

    Args:
        data_path (str): Path to the processed CSV file.
        stock_code (str): Ticker symbol of the stock (e.g., 'BBCA').
        simulations (int): Number of simulation runs.
        time_horizon (int): Number of time steps to simulate (e.g., 252 for 1 year daily).
        frequency (str): Data frequency ('daily', 'weekly', 'monthly').
    """
    print(f"Loading data from {data_path} for {stock_code} ({frequency})...")
    
    try:
        df = pd.read_csv(data_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter for the specific stock
        stock_df = df[df['StockCode'] == stock_code].copy()
        
        if stock_df.empty:
            print(f"Error: Stock {stock_code} not found in dataset.")
            return

        # Sort by date
        stock_df = stock_df.sort_values('Date')
        
        # Get historical stats
        returns = stock_df['Return']
        last_price = stock_df['Close'].iloc[-1]
        
        # Calculate drift (mu) and volatility (sigma)
        # We use log returns for GBM parameters usually, but simple returns * roughly equals log returns for small values.
        # Let's use simple returns statistics for simplicity in this basic version, or convert to log returns.
        # Log returns are better for GBM.
        log_returns = np.log(1 + returns)
        
        u = log_returns.mean()
        var = log_returns.var()
        
        # Drift
        drift = u - (0.5 * var)
        # Volatility
        stdev = log_returns.std()
        
        print(f"Statistics for {stock_code}:")
        print(f"  Last Price: {last_price}")
        print(f"  Mean Log Return: {u:.6f}")
        print(f"  Volatility (std): {stdev:.6f}")
        print(f"  Drift: {drift:.6f}")

        # Simulation
        # Z is random component
        # Price_t = Price_t-1 * exp(drift + sigma * Z)
        
        daily_returns_sim = np.exp(drift + stdev * np.random.normal(0, 1, (time_horizon, simulations)))
        
        price_paths = np.zeros_like(daily_returns_sim)
        price_paths[0] = last_price
        
        for t in range(1, time_horizon):
            price_paths[t] = price_paths[t-1] * daily_returns_sim[t]
            
        # Directories
        results_dir = os.path.join(os.path.dirname(data_path), '..', '..', 'results')
        plots_dir = os.path.join(results_dir, 'plots')
        reports_dir = os.path.join(results_dir, 'reports')
        
        os.makedirs(plots_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)

        # Date string for filename
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')

        # Visualization
        plt.figure(figsize=(10, 6))
        plt.plot(price_paths[:, :50]) # Plot first 50 simulations to avoid clutter
        plt.title(f'Monte Carlo Simulation for {stock_code} ({frequency}) - {time_horizon} steps')
        plt.xlabel('Time Steps')
        plt.ylabel('Price')
        plt.grid(True)
        
        output_plot = os.path.join(plots_dir, f"monte_carlo_{stock_code}_{frequency}_{date_str}.png")
        plt.savefig(output_plot)
        print(f"Simulation plot saved to {output_plot}")
        
        # Analysis
        final_prices = price_paths[-1]
        mean_final_price = np.mean(final_prices)
        VaR_95 = np.percentile(final_prices, 5)
        implied_growth = ((mean_final_price - last_price) / last_price) * 100
        
        print(f"Simulation Results ({simulations} runs):")
        print(f"  Expected Price: {mean_final_price:.2f}")
        print(f"  VaR (5%): {VaR_95:.2f} (Price at 5th percentile)")
        print(f"  Implied Growth: {implied_growth:.2f}%")
        
        # Save Report
        report_path = os.path.join(reports_dir, f"monte_carlo_{stock_code}_{frequency}_{date_str}.txt")
        with open(report_path, "w") as f:
            f.write(f"Monte Carlo Simulation Report\n")
            f.write(f"=============================\n")
            f.write(f"Date: {date_str}\n")
            f.write(f"Stock: {stock_code}\n")
            f.write(f"Frequency: {frequency}\n")
            f.write(f"Time Horizon: {time_horizon} steps\n")
            f.write(f"Simulations: {simulations}\n\n")
            f.write(f"Statistics:\n")
            f.write(f"  Last Price: {last_price}\n")
            f.write(f"  Mean Log Return: {u:.6f}\n")
            f.write(f"  Volatility (std): {stdev:.6f}\n")
            f.write(f"  Drift: {drift:.6f}\n\n")
            f.write(f"Results:\n")
            f.write(f"  Expected Price: {mean_final_price:.2f}\n")
            f.write(f"  VaR (5%): {VaR_95:.2f}\n")
            f.write(f"  Implied Growth: {implied_growth:.2f}%\n")
        print(f"Simulation report saved to {report_path}")

    except Exception as e:
        print(f"Error running simulation: {e}")

def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Simulation for Stock Prices")
    parser.add_argument("--stock", type=str, required=True, help="Stock Ticker (e.g., BBCA)")
    parser.add_argument("--freq", type=str, choices=['daily', 'weekly', 'monthly'], default='daily', help="Data Frequency")
    parser.add_argument("--steps", type=int, default=30, help="Time steps to simulate")
    parser.add_argument("--sims", type=int, default=1000, help="Number of simulations")
    
    args = parser.parse_args()
    
    base_data_dir = r"c:/Users/ASUS/Desktop/File Cepat/quant_system/data/processed"
    
    if args.freq == 'daily':
        data_file = "idx_daily_cleaned.csv"
    elif args.freq == 'weekly':
        data_file = "idx_weekly_cleaned.csv"
    elif args.freq == 'monthly':
        data_file = "idx_monthly_cleaned.csv"
        
    data_path = os.path.join(base_data_dir, data_file)
    
    if os.path.exists(data_path):
        run_monte_carlo(data_path, args.stock, args.sims, args.steps, args.freq)
    else:
        print(f"Error: Data file not found: {data_path}")

if __name__ == "__main__":
    main()
