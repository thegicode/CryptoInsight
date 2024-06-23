import asyncio
import datetime
import os
import subprocess
import json
from strategies import golden_dead_cross_signals, daily_average_signals, volatility_strategy, noise_strategy

def run_analysis_script(coin_list):
    """
    Run the best strategy analysis script and return the output.

    Parameters:
    coin_list (list): List of coin symbols to analyze.

    Returns:
    str: The output of the analysis script.
    """
    script_path = os.path.join('analysis', 'best_strategy_analysis.py')
    result = subprocess.run(['python3', script_path, ','.join(coin_list)], capture_output=True, text=True)
    return result.stdout


async def main():
    """
    Main function to execute the trading strategies and save the results.
    """
    # List of coins to analyze
    coin_list = [
        'KRW-AVAX', 'KRW-BCH', 'KRW-BTC', 'KRW-DOGE', 'KRW-DOT',
        'KRW-ETH', 'KRW-NEAR', 'KRW-POLYX', 'KRW-SHIB', 'KRW-SOL',
        'KRW-THETA', 'KRW-TFUEL', 'KRW-ZRX'
    ]

    # Run the analysis script and generate the strategy-to-markets mapping
    run_analysis_script(coin_list)

    # Read the results from the generated file
    with open('results/best_strategy_analysis.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create a dictionary mapping strategies to their respective markets
    strategy_to_markets = {}
    for line in lines:
        strategy, markets = line.strip().split(' : ', 1)
        strategy_to_markets[strategy] = json.loads(markets)

    # Get the current execution date and time
    execution_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file = 'results/strategies_result.txt'

    # Remove the existing output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Open the output file for writing
    with open(output_file, 'w') as f:
        def print_and_save(msg):
            print(msg)
            f.write(msg + "\n")

        # Write the execution date and time to the file
        print_and_save(f"Execution Date: {execution_datetime}\n")

        # Gather the results of each strategy asynchronously
        tasks = [
            asyncio.create_task(golden_dead_cross_signals(strategy_to_markets.get('golden_cross', []))),
            asyncio.create_task(daily_average_signals(strategy_to_markets.get('daily_average', []))),
            asyncio.create_task(volatility_strategy(strategy_to_markets.get('volatility', []))),
            asyncio.create_task(volatility_strategy(strategy_to_markets.get('volatility_ma', []), check_ma=True)),
            asyncio.create_task(volatility_strategy(strategy_to_markets.get('volatility_volume', []), check_ma=True, check_volume=True)),
            asyncio.create_task(noise_strategy(coin_list))
        ]

        results = await asyncio.gather(*tasks)

        # Write each result to the output file
        for result in results:
            print_and_save(result)


if __name__ == "__main__":
    asyncio.run(main())
