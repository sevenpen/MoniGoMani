import getopt
import json
import os
import sys
from pathlib import Path

import rapidjson
from pandas import DataFrame, json_normalize


def ExportCsvResults(config_file, input_file, output_file):
    # Load the 'mgm-config' file as an object and parse it as a dictionary

    basedir = os.getcwd()

    mgm_config = {}
    if os.path.isfile(config_file) is True:
        file_object = open(config_file, )
        json_data = json.load(file_object)
        mgm_config = json_data['monigomani_settings']

    # Fetch the latest '.fthypt' filename from last_result
    if input_file is None or input_file == '':
        last_result_file = Path(f'{basedir}/user_data/hyperopt_results/.last_result.json')
        with last_result_file.open('r') as f:
            data = [rapidjson.loads(line) for line in f]
        last_rf = json_normalize(data, max_level=1)

        results_file = Path(f'{basedir}/user_data/hyperopt_results/{last_rf["latest_hyperopt"].loc[0]}')
    else:
        results_file = Path(input_file)

    run_id = results_file.name.split('.')[0]

    # Open '.fthypt' file and normalize '.json' to dataframe
    with results_file.open('r') as f:
        data = [rapidjson.loads(line) for line in f]
    epochs = json_normalize(data, max_level=1)

    # Filter out epochs without profit
    epochs = epochs.loc[epochs['results_metrics.profit_total'] > 0]

    # Define result dataframe columns
    results_df = DataFrame(columns=[
        'current_epoch', 'HOLoss_result', 'total_profit', 'stake_currency', 'avg_profit', 'median_profit',
        'total_trades', 'wins', 'losses', 'draws', 'trades_per_day', 'rejected_signals', 'avgduration_h',
        'avgduration_winner_h', 'avgduration_loser_h', 'max_drawdown', 'drawdown_ratio', 'drawdown_start',
        'drawdown_end', 'pairlist', 'max_open_trades_setting', 'timeframe', 'backtest_timeframe', 'timerange',
        'backtest_start', 'backtest_end', 'backtest_days', 'buy_trades_when_downwards', 'buy_trades_when_sideways',
        'buy_trades_when_upwards', 'sell_trades_when_downwards', 'sell_trades_when_sideways',
        'sell_trades_when_upwards', 'unclogger_enabled', 'enable_protections', 'use_sell_signal', 'sell_profit_only',
        'sell_profit_offset', 'ignore_roi_if_buy_signal', 'minimal_roi', 'stoploss', 'trailing_stop',
        'trailing_stop_positive', 'trailing_stop_positive_offset', 'trailing_only_offset_is_reached'
    ])

    # Populate results df with selected values + rearrange format
    results_df['current_epoch'] = epochs['current_epoch']
    results_df['HOLoss_result'] = epochs['loss']
    results_df['total_profit'] = epochs['results_metrics.profit_total_abs'].apply(lambda x: round(x, 2))
    results_df['stake_currency'] = epochs['results_metrics.stake_currency']
    results_df['avg_profit'] = epochs['results_metrics.profit_mean'].apply(lambda x: round(x * 100, 2))
    results_df['median_profit'] = epochs['results_metrics.profit_median'].apply(lambda x: round(x * 100, 2))
    results_df['total_trades'] = epochs['results_metrics.total_trades']
    results_df['wins'] = epochs['results_metrics.wins']
    results_df['losses'] = epochs['results_metrics.losses']
    results_df['draws'] = epochs['results_metrics.draws']
    results_df['trades_per_day'] = epochs['results_metrics.trades_per_day']
    results_df['rejected_signals'] = epochs['results_metrics.rejected_signals']
    results_df['avgduration_h'] = epochs['results_metrics.holding_avg_s'].apply(lambda x: round(x / 3600, 2))
    results_df['avgduration_winner_h'] = epochs['results_metrics.winner_holding_avg_s'].apply(
        lambda x: round(x / 3600, 2))
    results_df['avgduration_loser_h'] = epochs['results_metrics.loser_holding_avg_s'].apply(
        lambda x: round(x / 3600, 2))
    results_df['max_drawdown'] = epochs['results_metrics.max_drawdown_abs'].apply(lambda x: round(x, 2))
    epochs['results_metrics.drawdown_ratio'] = (epochs['results_metrics.max_drawdown_abs'] /
                                                epochs['results_metrics.max_drawdown_high'])
    results_df['drawdown_ratio'] = epochs['results_metrics.drawdown_ratio'].apply(lambda x: round(x * 100, 2))
    results_df['drawdown_start'] = epochs['results_metrics.drawdown_start']
    results_df['drawdown_end'] = epochs['results_metrics.drawdown_end']
    # results_df['balance_min'] = epochs['results_metrics.csum_min'].apply(lambda x: round(x,2))
    # results_df['balance_max'] = epochs['results_metrics.csum_max'].apply(lambda x: round(x,2))
    results_df['pairlist'] = epochs['results_metrics.pairlist']
    results_df['max_open_trades_setting'] = epochs['results_metrics.max_open_trades_setting']
    results_df['timeframe'] = mgm_config['timeframes']['timeframe']
    results_df['backtest_timeframe'] = mgm_config['timeframes']['backtest_timeframe']
    results_df['timerange'] = epochs['results_metrics.timerange']
    results_df['backtest_start'] = epochs['results_metrics.backtest_start']
    results_df['backtest_end'] = epochs['results_metrics.backtest_end']
    results_df['backtest_days'] = epochs['results_metrics.backtest_days']
    results_df['buy_trades_when_downwards'] = mgm_config['trading_during_trends']['buy_trades_when_downwards']
    results_df['buy_trades_when_sideways'] = mgm_config['trading_during_trends']['buy_trades_when_sideways']
    results_df['buy_trades_when_upwards'] = mgm_config['trading_during_trends']['buy_trades_when_upwards']
    results_df['sell_trades_when_downwards'] = mgm_config['trading_during_trends']['sell_trades_when_downwards']
    results_df['sell_trades_when_sideways'] = mgm_config['trading_during_trends']['sell_trades_when_sideways']
    results_df['sell_trades_when_upwards'] = mgm_config['trading_during_trends']['sell_trades_when_upwards']
    results_df['unclogger_enabled'] = mgm_config['unclogger_spaces']['unclogger_enabled']
    results_df['enable_protections'] = epochs['results_metrics.enable_protections']
    results_df['use_sell_signal'] = epochs['results_metrics.use_sell_signal']
    results_df['sell_profit_only'] = epochs['results_metrics.sell_profit_only']
    results_df['sell_profit_offset'] = epochs['results_metrics.sell_profit_offset']
    results_df['ignore_roi_if_buy_signal'] = epochs['results_metrics.ignore_roi_if_buy_signal']
    results_df['minimal_roi'] = epochs['results_metrics.minimal_roi']
    results_df['stoploss'] = epochs['results_metrics.stoploss']
    results_df['trailing_stop'] = epochs['results_metrics.trailing_stop']
    results_df['trailing_stop_positive'] = epochs['results_metrics.trailing_stop_positive']
    results_df['trailing_stop_positive_offset'] = epochs['results_metrics.trailing_stop_positive_offset']
    results_df['trailing_only_offset_is_reached'] = epochs['results_metrics.trailing_only_offset_is_reached']
    results_df.insert(0, 'run_id', run_id)

    # Export result as '.csv' file for readable result
    if output_file is None or output_file == '':
        output_file = f'{basedir}/user_data/csv_results/{run_id}.csv'

    results_df.to_csv(output_file, index=False, header=True, mode='w', encoding='UTF-8')


def print_help():
    head = '\nExportCsvResults.py '
    print(
        f'{head}Usage examples:\n'
        f'{head}-c            <mgm_config_file> -i           <input_file> -o            <output_file>'
        f'{head}--cfile       <mgm_config_file> --ifile      <input_file> --ofile       <output_file>'
        f'{head}--config_file <mgm_config_file> --input_file <input_file> --output_file <output_file>')


def main(argv):
    input_file = ''
    output_file = ''
    config_file = f'{os.getcwd()}/user_data/mgm-config.json'
    try:
        opts, args = getopt.getopt(argv, 'hc:i:o:', [
            'cfile=', 'config_file=',
            'ifile=', 'input_file=',
            'ofile=', 'output_file='])
    except getopt.GetoptError:
        print('An error occurred while parsing the command arguments...')
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ('-c', '--cfile', '--config_file'):
            config_file = arg
        elif opt in ('-i', '--ifile', '--input_file'):
            input_file = arg
        elif opt in ('-o', '--ofile', '--output_file'):
            output_file = arg

    ExportCsvResults(config_file, input_file, output_file)


if __name__ == '__main__':
    main(sys.argv[1:])
