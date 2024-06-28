import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
from coins import coin_list

# CSV file paths
CSV_PATHS = {
    'daily_average': 'results/backtest/daily_average_backtest_200.csv',
    'golden_cross': 'results/backtest/golden_dead_cross_backtest_200.csv',
    'volatility': 'results/backtest/volatility_backtest_200.csv',
    'volatility_ma': 'results/backtest/volatility_checkMA_backtest_200.csv',
    'volatility_volume': 'results/backtest/volatility_checkMA_checkVolume_backtest_200.csv'
}

# Load CSV files into dataframes
dataframes_dict = {name: pd.read_csv(path) for name, path in CSV_PATHS.items()}

# Create results directory if it doesn't exist
OUTPUT_DIR = 'results/analysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_single_coin(coin_symbol, df_dict):
    """
    Analyze a single coin across multiple backtest strategies to determine the best strategy.

    Parameters:
    coin_symbol (str): The symbol of the coin to analyze.
    df_dict (dict): A dictionary of dataframes containing backtest results.

    Returns:
    pd.Series: A series containing the best strategy and its performance metrics for the given coin.
    """
    backtests = list(CSV_PATHS.keys())

    # Combine results into a single dataframe
    combined_df = pd.DataFrame({
        'Backtest': backtests,
        'Cumulative Return (%)': [
            df_dict[bt][df_dict[bt]['Market'] == coin_symbol]['Cumulative Return (%)'].values[0]
            if not df_dict[bt][df_dict[bt]['Market'] == coin_symbol].empty else None
            for bt in backtests
        ],
        'Win Rate (%)': [
            df_dict[bt][df_dict[bt]['Market'] == coin_symbol]['Win Rate (%)'].values[0]
            if not df_dict[bt][df_dict[bt]['Market'] == coin_symbol].empty else None
            for bt in backtests
        ],
        'Max Drawdown (MDD) (%)': [
            df_dict[bt][df_dict[bt]['Market'] == coin_symbol]['Max Drawdown (MDD) (%)'].values[0]
            if not df_dict[bt][df_dict[bt]['Market'] == coin_symbol].empty else None
            for bt in backtests
        ]
    })

    # Select the strategy with the highest cumulative return
    max_return_idx = combined_df['Cumulative Return (%)'].idxmax()
    best_strategy_result = combined_df.iloc[max_return_idx]

    return best_strategy_result

def analyze_coins(coin_list):
    """
    Analyze multiple coins and determine the best strategy for each.

    Parameters:
    coin_list (list): List of coin symbols to analyze.

    Returns:
    dict: A dictionary mapping each strategy to the list of coins for which it is the best strategy.
    """
    strategy_to_coins = {key: [] for key in CSV_PATHS.keys()}

    for single_coin in coin_list:
        best_strategy_for_coin = analyze_single_coin(single_coin, dataframes_dict)
        strategy_to_coins[best_strategy_for_coin['Backtest']].append(single_coin)

    return strategy_to_coins

if __name__ == "__main__":
    if len(sys.argv) > 1:
        markets = sys.argv[1].split(',')
    else:
        # 기본 코인 리스트를 설정합니다
        markets = coin_list

    result = analyze_coins(markets)

    # Save the results to a text file
    output_file_path = os.path.join(OUTPUT_DIR, 'best_strategy.txt')
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for strategy_name, coins in result.items():
            f.write(f"{strategy_name} : {json.dumps(coins)}\n")
            print(f"{strategy_name} : {json.dumps(coins)}\n")

    print("Analysis completed and saved to", output_file_path)
