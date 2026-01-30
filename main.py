import argparse
import sys
import os

# Ensure src is in the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    parser = argparse.ArgumentParser(description="Quant System CLI: Central command for all system components.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Data Ingestion ---
    ingest_parser = subparsers.add_parser("ingest", help="Trigger data ingestion modules")
    ingest_parser.add_argument("--source", type=str, required=True, help="Data source provider (e.g., binance, alpaca, yahoo)")
    ingest_parser.add_argument("--symbol", type=str, help="Symbol to ingest (e.g., BTCUSDT, AAPL)")

    # --- Processing ---
    process_parser = subparsers.add_parser("process", help="Run data processing pipelines")
    process_parser.add_argument("--type", choices=['clean', 'validate'], default='clean', help="Type of processing")

    # --- Backtesting ---
    bt_parser = subparsers.add_parser("backtest", help="Run strategy backtests")
    bt_parser.add_argument("--strategy", type=str, required=True, help="Name of the strategy class to run")
    bt_parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    bt_parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")

    # --- Execution ---
    trade_parser = subparsers.add_parser("trade", help="Live or Paper Trading Execution")
    trade_parser.add_argument("--mode", choices=['paper', 'live'], default='paper', help="Trading mode")
    trade_parser.add_argument("--strategy", type=str, required=True, help="Strategy to deploy")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Routing logic (Placeholder for now, will import specific modules later)
    if args.command == "ingest":
        print(f"[Ingestion] Starting ingestion from source: {args.source}")
        if args.source.lower() == "stockbit":
            from src.data_ingestion.scrapers import stockbit_scraper
            # Hardcoded path for this specific task, or could be passed via args
            excel_path = r"c:\Users\ASUS\Desktop\File Cepat\quant_system\data\raw\Ringkasan Saham-20260112.xlsx"
            stockbit_scraper.run(excel_path)
        else:
            print(f"[Ingestion] Source '{args.source}' not yet implemented.")
            
        if args.symbol:
            print(f"[Ingestion] Target symbol: {args.symbol}")

    elif args.command == "process":
        print(f"[Processing] Running {args.type} pipeline...")
        # TODO: import src.processing.runner and call run(args)

    elif args.command == "backtest":
        print(f"[Backtest] Initializing strategy: {args.strategy}")
        if args.start and args.end:
            print(f"[Backtest] Period: {args.start} to {args.end}")
        # TODO: import src.backtester.runner and call run(args)
        
    elif args.command == "trade":
        print(f"[Execution] Starting {args.mode} trading with strategy: {args.strategy}")
        # TODO: import src.execution.runner and call run(args)

if __name__ == "__main__":
    main()
