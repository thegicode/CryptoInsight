import asyncio
import datetime
import os
import subprocess
import json
from typing import List, Dict
from strategies import (
    golden_dead_cross_signals,
    daily_average_signals,
    volatility_strategy,
    noise_strategy,
    afternoon_strategy
)
from coins import coin_list
from utils.telegram import get_chat_ids, send_telegram_message

CHAT_GROUP_ID = get_chat_ids()
ANALYSIS_SCRIPT_PATH = os.path.join('analysis', 'best_strategy.py')
ANALYSIS_RESULTS_PATH = 'results/analysis/best_strategy.txt'
OUTPUT_FILE_PATH = 'results/trade/strategies.txt'

def run_analysis_script(coins: List[str]) -> str:
    """Run the best strategy analysis script and return the output."""
    result = subprocess.run(['python3', ANALYSIS_SCRIPT_PATH, ','.join(coins)], capture_output=True, text=True)
    return result.stdout

def read_analysis_results() -> Dict[str, List[str]]:
    """Read and parse the analysis results from the generated file."""
    with open(ANALYSIS_RESULTS_PATH, 'r', encoding='utf-8') as f:
        return {
            strategy: json.loads(markets)
            for line in f
            for strategy, markets in [line.strip().split(' : ', 1)]
        }

async def execute_strategies(strategy_to_markets: Dict[str, List[str]]) -> List[str]:
    """Execute trading strategies based on the analysis results."""
    tasks = [
        asyncio.create_task(daily_average_signals(strategy_to_markets.get('daily_average_5', []))),
        asyncio.create_task(daily_average_signals(strategy_to_markets.get('daily_average_120', []), 120)),
        asyncio.create_task(golden_dead_cross_signals(strategy_to_markets.get('golden_cross', []))),
        asyncio.create_task(volatility_strategy(strategy_to_markets.get('volatility', []))),
        asyncio.create_task(volatility_strategy(strategy_to_markets.get('volatility_ma', []), check_ma=True)),
        asyncio.create_task(volatility_strategy(strategy_to_markets.get('volatility_volume', []), check_ma=True, check_volume=True)),
        asyncio.create_task(afternoon_strategy(strategy_to_markets.get('afternoon', []))),
        asyncio.create_task(noise_strategy(coin_list)),
    ]
    return await asyncio.gather(*tasks)

def write_and_print_results(execution_datetime: str, results: List[str]):
    """Write the execution results to the output file and print to console."""
    output = f"Execution Date: {execution_datetime}\n"
    output += "\n".join(results)

    # Write to file
    with open(OUTPUT_FILE_PATH, 'w') as f:
        f.write(output)

    # Print to console
    print(output)

async def main():
    """Main function to execute the trading strategies and save the results."""
    run_analysis_script(coin_list)
    strategy_to_markets = read_analysis_results()

    execution_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = await execute_strategies(strategy_to_markets)

    write_and_print_results(execution_datetime, results)

    # Uncomment the following line to send results via Telegram
    # send_telegram_message(f"Execution Date: {execution_datetime}\n" + '\n'.join(map(str, results)))

if __name__ == "__main__":
    asyncio.run(main())