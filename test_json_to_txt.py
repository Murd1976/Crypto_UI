import json
import pandas as pd

class my_reports():

    def json_to_txt(self, directory:str='', f_name:str = ''):
        #f_name = "d:/Python/UI/reports/bc_4_p4_MyLossTrailingMinROI_4_4-2022-06-10_00-33-58.json"

        #загрузка данных о сделках из файла с результатами BackTest
        with open(directory + f_name, 'r') as f:
             #json_obj = json.loads(f.read())
            json_obj = json.loads(f.read())
#        print(f_name)
        cur_strategy = list(dict.keys(json_obj['strategy']))[0] # вытаскиваем имя стратегии из файла результатоы бектеста
        key_list = list(dict.keys(json_obj['strategy'][cur_strategy]))         
        #f.write(key_list)
        buf_str = f_name.split('.')

        #Открываем текстовый файл для сохранения форматированного отчета
        f = open(directory + buf_str[0] + '.txt', 'w')

#        print(len(json_obj['strategy'][cur_strategy]['trades']))

        jason_list = json_obj['strategy'][cur_strategy]['results_per_pair']
        #f.write(jason_list)

        f.write('============================================================= BACKTESTING REPORT ===========================================================\n')
        f.write('|       Pair   |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |   Avg Duration |   Win  Draw  Loss  Win%  |\n')
        f.write('|--------------+--------+----------------+----------------+-------------------+----------------+----------------+--------------------------|\n')

        for res_pair in jason_list:
            buf_str = ('| '+res_pair["key"].rjust(12)+ ' '
                      +str(f'| {res_pair["trades"]:6} | {res_pair["profit_mean_pct"]:14.2f} | {res_pair["profit_sum_pct"]:14.2f} | {res_pair["profit_total_abs"]:17.3f} | \
{res_pair["profit_total_pct"]:14.2f} | ')+ res_pair["duration_avg"].rjust(14)+ ' | ')
    
    
            if res_pair["trades"] > 0:
                win_pct = 100/res_pair["trades"]*res_pair["wins"]
            else:
                win_pct = 0
            buf_str = buf_str + str(f' {res_pair["wins"]:4}  {res_pair["draws"]:4}  {res_pair["losses"]:4}  {win_pct:5.1f} |\n')
            f.write(buf_str)

        f.write('========================================================= ENTER TAG STATS ===========================================================\n')
        f.write('|   TAG |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |   Avg Duration |   Win  Draw  Loss  Win%  |\n')
        f.write('|-------+--------+----------------+----------------+-------------------+----------------+----------------+--------------------------|\n')

        res_pair = json_obj['strategy'][cur_strategy]['results_per_enter_tag'][0]
        buf_str = ('| '+res_pair["key"].rjust(5)+' '
                  +str(f'| {res_pair["trades"]:6} | {res_pair["profit_mean_pct"]:14.2f} | {res_pair["profit_sum_pct"]:14.2f} | {res_pair["profit_total_abs"]:17.3f} | \
{res_pair["profit_total_pct"]:14.2f} | ') + res_pair["duration_avg"].rjust(14) +' | ')

        if res_pair["trades"] > 0:
           win_pct = 100/res_pair["trades"]*res_pair["wins"]
        else:
           win_pct = 0
        buf_str = buf_str + str(f' {res_pair["wins"]:4}  {res_pair["draws"]:4}  {res_pair["losses"]:4}  {win_pct:5.1f} |\n')
        f.write(buf_str)


        f.write('=====================================================+== EXIT REASON STATS ========================================================\n')                                                 
        f.write('|        Exit Reason |   Exits |   Win  Draws  Loss  Win%  |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |\n')                                               
        f.write('|--------------------+---------+---------------------------+----------------+----------------+-------------------+----------------|\n')
        jason_list = json_obj['strategy'][cur_strategy]['exit_reason_summary']
        for res_pair in jason_list:
            buf_str = ('| '+res_pair["exit_reason"].rjust(18)) + str(f' | {res_pair["trades"]:7} | ')
            if res_pair["trades"] > 0:
                win_pct = 100/res_pair["trades"]*res_pair["wins"]
            else:
                win_pct = 0
            buf_str = buf_str + str(f' {res_pair["wins"]:4}  {res_pair["draws"]:4}  {res_pair["losses"]:4}  {win_pct:5.1f} ')
            buf_str = buf_str + str(f' | {res_pair["profit_mean_pct"]:14.2f} | {res_pair["profit_sum_pct"]:14.2f} | {res_pair["profit_total_abs"]:17.3f} | \
{res_pair["profit_total_pct"]:14.2f} |\n')
            f.write(buf_str)    
    
        f.write('====================================================== LEFT OPEN TRADES REPORT =======================================================\n')                                              
        f.write('|   Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |   Avg Duration |   Win  Draw  Loss  Win%  |\n')                                              
        f.write('|--------+--------+----------------+----------------+-------------------+----------------+----------------+--------------------------|\n')
        res_pair = json_obj['strategy'][cur_strategy]['left_open_trades'][0]
        buf_str = ('| '+res_pair["key"].rjust(6))
        buf_str = buf_str + str(f' | {res_pair["trades"]:6} | {res_pair["profit_mean_pct"]:14.2f} | {res_pair["profit_sum_pct"]:14.2f} | {res_pair["profit_total_abs"]:17.3f} | \
{res_pair["profit_total_pct"]:14.2f} | ')
        buf_str = buf_str + (res_pair["duration_avg"].rjust(14) + ' | ')
        if res_pair["trades"] > 0:
           win_pct = 100/res_pair["trades"]*res_pair["wins"]
        else:
           win_pct = 0
        buf_str = buf_str + str(f' {res_pair["wins"]:4}  {res_pair["draws"]:4}  {res_pair["losses"]:4}  {win_pct:5.1f} |\n')
        f.write(buf_str) 

        f.write('================== SUMMARY METRICS ==================\n')                                                                                                                              
        f.write('| Metric                      | Value               |\n')                                                                                                                              
        f.write('|-----------------------------+---------------------|\n')
        jason_list = json_obj['strategy'][cur_strategy]['backtest_start']
        buf_str = str(f'| {"Backtesting from":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = json_obj['strategy'][cur_strategy]['backtest_end']
        buf_str = str(f'| {"Backtesting to":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(json_obj['strategy'][cur_strategy]['max_open_trades'])
        buf_str = str(f'| {"Max open trades":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        buf_str = str(f'| {" ":27} | {" ":19} |\n')
        f.write(buf_str)

        jason_list = str(json_obj['strategy'][cur_strategy]['total_trades'])
        jason_list = jason_list + ' / ' + str(json_obj['strategy'][cur_strategy]['trades_per_day'])
        buf_str = str(f'| {"Total/Daily Avg Trades":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = json_obj['strategy'][cur_strategy]['trades_per_day']
        jason_list = str(json_obj['strategy'][cur_strategy]['starting_balance']) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Starting balance":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['final_balance']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Final balance":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['profit_total_abs']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Absolute profit":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.2f}'.format(json_obj['strategy'][cur_strategy]['profit_total'] * 100))) + '%'
        buf_str = str(f'| {"Total profit %":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.2f}'.format(json_obj['strategy'][cur_strategy]['cagr'] * 100))) + '%'
        buf_str = str(f'| {"CAGR %":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['trades_per_day'])))
        buf_str = str(f'| {"Trades per day":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.2f}'.format(json_obj['strategy'][cur_strategy]['profit_total'] * 100/json_obj['strategy'][cur_strategy]['backtest_days']))) + '%'
        buf_str = str(f'| {"Avg. daily profit %":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['avg_stake_amount']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Avg. stake amount":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['total_volume']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Total trade volume":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        buf_str = str(f'| {" ":27} | {" ":19} |\n')
        f.write(buf_str)

        res_pair = json_obj['strategy'][cur_strategy]['best_pair']
        jason_list = res_pair["key"] + ' ' +  str(float('{:.2f}'.format(res_pair["profit_sum_pct"]))) + '%'
        buf_str = str(f'| {"Best Pair":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        res_pair = json_obj['strategy'][cur_strategy]['worst_pair']
        jason_list = res_pair["key"] + ' ' +  str(float('{:.2f}'.format(res_pair["profit_sum_pct"]))) + '%'
        buf_str = str(f'| {"Worst Pair":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        if len(json_obj['strategy'][cur_strategy]['trades']) > 0:
            jason_list = json_obj['strategy'][cur_strategy]['trades']
            best_trade_pair = jason_list[0]["pair"]
            worst_trade_pair = jason_list[0]["pair"]
            best_trade = jason_list[0]["profit_ratio"]
            worst_trade = jason_list[0]["profit_ratio"]

            for res_pair in jason_list:
               if res_pair["profit_ratio"] >  best_trade:
                  best_trade = res_pair["profit_ratio"]
                  best_trade_pair = res_pair["pair"]
               if res_pair["profit_ratio"] <  worst_trade:
                  worst_trade = res_pair["profit_ratio"]
                  worst_trade_pair = res_pair["pair"]
      
            jason_list = best_trade_pair + ' ' +  str(float('{:.2f}'.format(best_trade*100))) + '%' 
            buf_str = str(f'| {"Best trade":27} | '+ jason_list.ljust(19)+ ' |\n')
            f.write(buf_str)
            jason_list = worst_trade_pair + ' ' +  str(float('{:.2f}'.format(worst_trade*100))) + '%' 
            buf_str = str(f'| {"Worst trade":27} | '+ jason_list.ljust(19)+ ' |\n')
            f.write(buf_str)

        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['backtest_best_day_abs']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Best day":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['backtest_worst_day_abs']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Worst day":27} | '+ jason_list.ljust(19)+  ' |\n')
        f.write(buf_str)

        jason_list = str(json_obj['strategy'][cur_strategy]['winning_days'])
        jason_list = jason_list + ' / ' + str(json_obj['strategy'][cur_strategy]['draw_days'])
        jason_list = jason_list + ' / ' + str(json_obj['strategy'][cur_strategy]['losing_days'])
        buf_str = str(f'| {"Days win/draw/lose":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = str(json_obj['strategy'][cur_strategy]['winner_holding_avg'])
        buf_str = str(f'| {"Avg. Duration Winners":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(json_obj['strategy'][cur_strategy]['loser_holding_avg'])
        buf_str = str(f'| {"Avg. Duration Loser":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = str(json_obj['strategy'][cur_strategy]['rejected_signals'])
        buf_str = str(f'| {"Rejected Entry signals":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = str(json_obj['strategy'][cur_strategy]['timedout_entry_orders'])
        jason_list = jason_list + ' / ' + str(json_obj['strategy'][cur_strategy]['timedout_exit_orders'])
        buf_str = str(f'| {"Entry/Exit Timeouts":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        buf_str = str(f'| {" ":27} | {" ":19} |\n')
        f.write(buf_str)

        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['csum_min']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Min balance":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['csum_max']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Max balance":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        if 'max_relative_drawdown' in json_obj['strategy'][cur_strategy]:
            jason_list = str(float('{:.2f}'.format(json_obj['strategy'][cur_strategy]['max_relative_drawdown'] * 100))) + '%'
            buf_str = str(f'| {"Max % of account underwater":27} | '+ jason_list.ljust(19)+ ' |\n')
            f.write(buf_str)
        jason_list = str(float('{:.2f}'.format(json_obj['strategy'][cur_strategy]['max_drawdown_account'] * 100))) + '%'
        buf_str = str(f'| {"Absolute Drawdown (Account)":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['max_drawdown_abs']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Absolute Drawdown":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['max_drawdown_high']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Drawdown high":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = str(float('{:.3f}'.format(json_obj['strategy'][cur_strategy]['max_drawdown_low']))) + ' ' + json_obj['strategy'][cur_strategy]['stake_currency']
        buf_str = str(f'| {"Drawdown low":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = json_obj['strategy'][cur_strategy]['drawdown_start']
        buf_str = str(f'| {"Drawdown Start":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        jason_list = json_obj['strategy'][cur_strategy]['drawdown_end']
        buf_str = str(f'| {"Drawdown End":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)

        jason_list = str(float('{:.2f}'.format(json_obj['strategy'][cur_strategy]['market_change'] * 100))) + '%'
        buf_str = str(f'| {"Market change":27} | '+ jason_list.ljust(19)+ ' |\n')
        f.write(buf_str)
        buf_str = str('=====================================================')
        f.write(buf_str)

        f.close()    
