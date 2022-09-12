import os as os_lib
import pandas as pd
import numpy as np
import json
import time
import PySimpleGUI as sg
import paramiko
#import talib


class rep_from_test_res():
    #work_path= 'c:/Users/Denis/ft_userdata/user_data/backtest_results'
    #pairs_path= 'c:/Users/Denis/ft_userdata/user_data/data/binance'
    #flist=os_lib.listdir(work_path)
    #flist.sort()

    #f_pair_name = 'BETA_USDT-1m'
    #f_name= 'bc_loss_trail_roi_4_4_p4-2022-04-15_15-52-33'
    #cur_strategy = 'MyLossTrailingMinROI_4_4'

    N_strategy = 0

    N_candle_analyze = np.array([1,3,5,10,15,30]) #number of Candles to analyze after the buy trigger
    #N_candle_analyze = np.array([3]) #number of Candles to analyze after the buy trigger

    N_pre_candle_analyze = np.array([15,30, 60]) #number of Candles to analyze before the buy trigger
    #N_pre_candle_analyze = np.array([15]) #number of Candles to analyze before the buy trigger

    #pd.options.display.float_format = '{:,.5f}'.format
    pd.set_option('display.max_columns', None)

    #Average Price Change from the Buying Price
    def sma_rep(self, dataframe_1: pd.DataFrame, buy_price:float):
        dataframe_1=(dataframe_1-buy_price)/buy_price*100
        #sma = round(dataframe_1.sum(),5)/len(dataframe_1)
        sma = dataframe_1.mean()       
        return round(sma, 5)

    #On Average, how many candles have closing price > opening price (green candle)
    #On Average, how many candles have closing price < opening price (red candle
    def candles_rep(self, dataframe_1: pd.DataFrame):

        red_num  = len(dataframe_1.loc[(dataframe_1['open']-dataframe_1['close']) >= 0 ]) # RED candles
        green_num = len(dataframe_1.loc[(dataframe_1['open']-dataframe_1['close']) <0 ]) # GREEN candles
        red_p = red_num/len(dataframe_1)*100
        green_p = green_num/len(dataframe_1)*100
    
        return round(green_p, 2), round(red_p, 2)

    #Average Price Change Green candles
    #Average Price Change Red candles
    def av_candles_rep(self, dataframe_1: pd.DataFrame, buy_price:float):

        av_inc_green, av_dec_red = 0, 0
    
        # необходимо использовать (.copy(deep=True))чтобы не выдавало предупреждение "A value is trying to be set on a copy of a slice from a DataFrame"
        red_df = dataframe_1.loc[(dataframe_1['open']-dataframe_1['close']) >= 0 ].copy(deep=True) # RED candles
        green_df = dataframe_1.loc[(dataframe_1['open']-dataframe_1['close']) < 0 ].copy(deep=True) # GREEN candles

        red_df['change_price%'] =(red_df['close']-buy_price)/buy_price*100
        green_df['change_price%'] =(green_df['close']-buy_price)/buy_price*100
    
        red_num  = len(red_df) # RED candles count
        green_num = len(green_df) # GREEN candles count
 
        if red_num > 0:
            av_dec_red = red_df['change_price%'].mean()
        else:
            av_dec_red = 0
        
        if green_num > 0:    
            av_inc_green = green_df['change_price%'].mean()
        else:
           av_inc_green = 0 
    
        return av_inc_green, av_dec_red

    #maximum price and the minimum price, expressed as % change from buying price
    def min_max_rep(self, dataframe_1: pd.DataFrame, buy_price:float):
        dataframe_1=dataframe_1/buy_price*100-100
        max_p = dataframe_1.max()
        min_p = dataframe_1.min()
   
        return round(max_p, 3), round(min_p, 3)

    #the ratio of MAX price being above buying price (i.e a positive value)
    def retio_max_rep(self, dataframe_1: pd.DataFrame, buy_price:float):

        if dataframe_1.max() > buy_price:
            val = 1
        else:
            val = 0
        
        return val

    #Average price change of candles with closing price > buying price
    #Average price change of candles with closing price < buying price
    def av_up_down_rep(self, dataframe_1: pd.DataFrame, buy_price:float):

        av_up_candle = np.array([0.0, 0.0])
        av_down_candle = np.array([0.0, 0.0])

        # необходимо использовать (.copy(deep=True))чтобы не выдавало предупреждение "A value is trying to be set on a copy of a slice from a DataFrame"
        up_df = dataframe_1.loc[(dataframe_1['close']) > buy_price ].copy(deep=True) # UP price candles
        down_df = dataframe_1.loc[(dataframe_1['close']) <= buy_price ].copy(deep=True) # DOWN price candles

        up_df['change_price%'] =(up_df['close']-buy_price)/buy_price*100
        down_df['change_price%'] =(down_df['close']-buy_price)/buy_price*100
    
        up_num  = len(up_df) # UP price candles count
        down_num = len(down_df) # DOWN price candles count
        
        if up_num > 0:
            av_up_candle[1] = up_df['change_price%'].mean()
        else:
            av_up_candle[1] = 0
        
        if down_num > 0:    
            av_down_candle[1] = down_df['change_price%'].mean()
        else:
           av_down_candle[1] = 0

        av_up_candle[0] = up_num/len(dataframe_1)*100
        av_down_candle[0] = down_num/len(dataframe_1)*100
    
        return av_up_candle, av_down_candle


    #Average max_rate price, expressed as % change from buying price (calculated from the highest "high" value of the N candles)
    #Median max_rate price, expressed as % change from buying price (calculated from the highest "high" value of the N candles)
    #Average min_rate price, expressed as % change from buying price (calculated from the lowest "low" value of the N candles)
    #Median min_rate price, expressed as % change from buying price (calculated from the lowest "low" value of the N candles)
    def min_max_rate_rep(self, dataframe_1: pd.DataFrame, buy_price:float):
        dataframe_1=dataframe_1[['high', 'low']]/buy_price*100-100

        max_p = dataframe_1['high'].max()
        min_p = dataframe_1['low'].min()
   
        return round(max_p, 3), round(min_p, 3)

    #чтение свечей из заданного файла, с заданным time_rate
    def get_pair_fdata(self, f_name, time_rate):

        col_names=["date", "open", "high", "low", "close", "volume"]
        f_name=f_name+'-'+time_rate+'.json'

        hostname = "gate.controller.cloudlets.zone"
        port = 3022
        username = "7441-732"
        directory = '/root/application/user_data/data/binance/'
        
        try:        
            client = paramiko.SSHClient()
         # Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.RSAKey.from_private_key_file('RSA_private_1.txt')
         # подключиться к серверу
            client.connect(hostname, port, username, pkey=private_key, timeout=3, disabled_algorithms=dict(pubkeys=['rsa-sha2-256', 'rsa-sha2-512']))
        except:
            print('Error connection')
            return('error')
        
        

        sftp_client = client.open_sftp()
        #загрузить файл свечей на комп пользователя
        sftp_client.get(directory + f_name, "./reports/" + f_name)
        sftp_client.close()

        
        
        if not os_lib.path.exists("./reports/" +f_name): #проверяем наличие такого файла
            print('File not found: ', "./reports/" +f_name)
            return null
    
        f_out_df= pd.read_json("./reports/" +f_name) #читаем данные из файла с time_rate свечами, для конкретной пары
        f_out_df.index.name = 'index'
        f_out_df.columns = col_names
        f_out_df['date'] = pd.to_datetime(f_out_df['date'], unit='ms') #приводим дату в читаемый вид

        os_lib.remove("./reports/" +f_name)

#    print(f_out_df[:10])

        return f_out_df


    #загрузка свечей из файла конкретной пары

    #col_names=["date", "open", "high", "low", "close", "volume"]

    #df_pair= pd.read_json(pairs_path+'/'+f_pair_name+'.json')
    #df_pair.index.name = 'index'
    #df_pair.columns = col_names
    #df_pair['date'] = pd.to_datetime(df_pair['date'], unit='ms') #приводим дату в читаемый вид
    def get_report(self, work_path:str = '', f_name:str=''):

        #берем длину последовательности из имени файла теста
        N_strategy = int(f_name.split('_')[1])
        
	#загрузка данных о сделках из файла с результатами BackTest
        with open(work_path+f_name, 'r') as f:
            json_obj = json.loads(f.read())

        cur_strategy = list(dict.keys(json_obj['strategy']))[0] # вытаскиваем имя стратегии из файла результатоы бектеста
        
        df = pd.DataFrame(json_obj['strategy'][cur_strategy]['trades'])
        if df.empty:
            return "no_trades"
        df.index.name = 'Index'

        df = df[['pair', 'amount', 'open_date', 'close_date', 'open_rate', 'close_rate', 'trade_duration',
			 'profit_ratio', 'profit_abs', 'exit_reason', 'stake_amount', 'fee_open', 'fee_close',
			 'initial_stop_loss_abs', 'initial_stop_loss_ratio', 'stop_loss_abs', 'stop_loss_ratio',
		  	 'min_rate', 'max_rate', 'is_open', 'enter_tag', "is_short", 'open_timestamp', 'close_timestamp']]

        df['open_timestamp'] = pd.to_datetime(df['open_timestamp'], unit='ms') #приводим дату в читаемый вид
        df['close_timestamp'] = pd.to_datetime(df['close_timestamp'], unit='ms') #приводим дату в читаемый вид
	
	#df= pd.read_json('/freqtrade/back_tests/'+f_name)
        df_group = df.groupby(['pair', 'open_date'])[['pair', 'amount', 'open_date', 'close_date', 'open_rate', 'close_rate', 'trade_duration']].sum()
        df_pairs = df['pair'].unique() #список уникальных имен пар
	#print('Unique pairs: ', len(df_pairs))

	#заготовка под промежуточный развернутый отчет
        res_df = pd.DataFrame(columns=['pair','analyze_N', 'open_date', 'open_rate', 'close_rate', 'trade_duration',
			 'profit_ratio', 'exit_reason', 'min_rate', 'max_rate',
			 'sma', 'av_green', 'av_red', 'av_change_green', 'av_change_red', 'max_price%', 'min_price%', 'retio_of_max',
			 'av_up_price', 'av_down_price', 'av_up_price_change', 'av_down_price_change', 'av_max_rate', 'av_min_rate',
			 'volume', 'value_AV', 'value_MV', 'value_TV', 'TV/AV', 'TV/MV', 'win_TV/AV', 'SMA', 'Win_SMA'])

        pre_df = pd.DataFrame(columns=['pair', 'analyze_N', 'volume', 'value_AV', 'value_MV', 'value_TV', 'TV/AV', 'TV/MV', 'win_TV/AV',
								   'open_date', 'open_rate', 'close_rate', 'trade_duration', 'profit_ratio', 'exit_reason', 'min_rate', 'max_rate'])

	# заготовка под финальный общий отчет
        report_df = pd.DataFrame(np.zeros([7,23]), columns=['value_N', 'sma', 'av_green', 'av_red', 'av_change_green', 'av_change_red', 'max_price%', 'min_price%', 'retio_of_max',
														'av_up_price', 'av_down_price', 'av_up_price_change', 'av_down_price_change', 'av_loss_min_price%',
														'av_max_rate', 'm_max_rate', 'm_min_rate', 'av_min_rate',
														'TV/AV', 'TV/MV', 'win_TV/AV', 'SMA', 'Win_SMA'])
        report_df['value_N']=['N-1', 'N-3', 'N-5', 'N-10', 'N-15', 'N-30', 'N-60']

        report_df_2 = pd.DataFrame(np.zeros([1,16]), columns=['av_24h_volume', 'last_24h_volume', 'av_24h_amplitude_up', 'av_24h_amplitude_down', 'last_24h_amplitude_up', 'last_24h_amplitude_down', 'last_24h_SMA', 'last_24h_SMAbuy',
									  'win_av_24h_volume', 'win_last_24h_volume', 'win_av_24h_amplitude_up', 'win_av_24h_amplitude_down',
									  'win_last_24h_amplitude_up', 'win_last_24h_amplitude_down', 'win_last_24h_SMA', 'win_last_24h_SMAbuy'])

        rep_columns=['pair', 'open_date', 'open_rate', 'close_rate', 'trade_duration',
				 'profit_ratio', 'exit_reason', 'min_rate', 'max_rate']

        pre_report_df = pd.DataFrame(np.zeros([3,9]), columns=['value_N', 'value_AV', 'value_MV', 'value_TV', 'TV/AV', 'TV/MV', 'win_TV/AV', 'SMA', 'Win_SMA'])
        pre_report_df['value_N']=['N-15', 'N-30', 'N-60']

        big_rep_df = pd.DataFrame(columns=['pair', 'date', 'open', 'close'])
        pre_big_rep_df = pd.DataFrame(columns=['pair', 'date', 'open', 'close', 'volume'])
        res_df_24 = pd.DataFrame(np.zeros([len(df),18]),
				 columns=['pair', 'date', 'av_24h_volume', 'last_24h_volume', 'av_24h_amplitude_up', 'av_24h_amplitude_down', 'last_24h_amplitude_up', 'last_24h_amplitude_down', 'last_24h_SMA', 'last_24h_SMAbuy',
					  'win_av_24h_volume', 'win_last_24h_volume', 'win_av_24h_amplitude_up', 'win_av_24h_amplitude_down',
					  'win_last_24h_amplitude_up', 'win_last_24h_amplitude_down', 'win_last_24h_SMA', 'win_last_24h_SMAbuy'])


	#Отключаем сообщение об ошибках присваивания
        pd.options.mode.chained_assignment = None  # default='warn'
        #print(f_name+' in progress!')

        bar_len = len(df)*(len(self.N_candle_analyze)+len(self.N_pre_candle_analyze))
        #print('Len', bar_len)
        bar_step = 0;
        idnex_count = 0;

        for ii, i in enumerate(df_pairs): #проходим по всему списку уникальных имен пар
        	buf_df=df.loc[df['pair'] == i] # датафрейм с трейдами для текущего, уникального, названия пары
        	f_pair_name = i.replace('/', '_')
        	#print(buf_df)
                #f_pair_name=work_path+'/data/binance'+'/'+i.replace('/', '_')
        	df_pair_1m = self.get_pair_fdata(f_pair_name, '1m')
        	df_pair_1h = self.get_pair_fdata(f_pair_name, '1h')
        	df_pair_1d = self.get_pair_fdata(f_pair_name, '1d')

        	df_pair_1d['volume'] = df_pair_1d['volume']*df_pair_1d['close']
	
	#    f_pair_hour_name=pairs_path+'/'+i.replace('/', '_')+'-1h.json'
	#    f_pair_day_name=pairs_path+'/'+i.replace('/', '_')+'-1d.json'
	#    print(f_pair_name)
	#    if not os_lib.path.exists(f_pair_name): #проверяем наличие такого файла
	#        print('File ot found: ', f_pair_name)
	#        continue
	
	#    df_pair= pd.read_json(f_pair_min_name) #читаем данные из файла с минутными свечами, для конкретной пары
	#    df_pair.index.name = 'index'
	#    df_pair.columns = col_names
	#    df_pair['date'] = pd.to_datetime(df_pair['date'], unit='ms') #приводим дату в читаемый вид
	#    z=0 # счетчик трейдов для конкретной пары
        	for z, b in enumerate(buf_df['open_timestamp']): #делаем выборки данных по каждому трейду текущей пары

		  #  res_df= pd.concat([res_df, buf_df.iloc[z:z+1]], ignore_index = True) #выдергиваем строку исходного отчета с трейдом и добавляем ее в расширенный отчет
		
        		buy_pos = list(np.where(df_pair_1m['date'] == b))[0]  #ищем адрес текущего трейда в общих данных для пары
        		cur_buy_price = buf_df['open_rate'].iloc[z] #стартовая цена для текущего тренда
        		max_step = len(df_pair_1m)-buy_pos

	#POST BUY TRIGGER PRICES ANALYSIS
        		for cc, n in enumerate(self.N_candle_analyze):
        			res_df= pd.concat([res_df, buf_df[rep_columns].iloc[z:z+1]], ignore_index = True) #выдергиваем строку исходного отчета с трейдом и добавляем ее в расширенный отчет
        			res_df['analyze_N'].iloc[-1] = n
	#            print(res_df.iloc[-1])
        			out_df = df_pair_1m[buy_pos[0]+1: buy_pos[0]+1+n].copy() #выдергиваем из данных для пары, N-свечей для анализа
			
	#            print('analyze: ', n)
        			out_df['pair'] = i
	#            print(out_df)
        			big_rep_df = pd.concat([big_rep_df, out_df[['pair', 'date', 'open', 'close']]], ignore_index = True)
		
        			output = self.sma_rep(out_df['close'], cur_buy_price)
        			res_df['sma'].iloc[-1] = output
		
        			green_c, red_c = self.candles_rep(out_df)
        			res_df['av_green'].iloc[-1] = green_c
        			res_df['av_red'].iloc[-1] = red_c
		
        			green_av, red_av = self.av_candles_rep(out_df, cur_buy_price)
        			res_df['av_change_green'].iloc[-1] = green_av
        			res_df['av_change_red'].iloc[-1] = red_av

        			maxp, minp = self.min_max_rep(out_df['close'], cur_buy_price)
        			res_df['max_price%'].iloc[-1] = maxp
        			res_df['min_price%'].iloc[-1] = minp

        			r_max = self.retio_max_rep(out_df['close'], cur_buy_price)
        			res_df['retio_of_max'].iloc[-1] = r_max

        			up_candle, down_candle = self.av_up_down_rep(out_df, cur_buy_price)
			   # print(up_candle, down_candle)            
        			res_df['av_up_price'].iloc[-1] = up_candle[0]
        			res_df['av_down_price'].iloc[-1] = down_candle[0]
        			res_df['av_up_price_change'].iloc[-1] = up_candle[1]
        			res_df['av_down_price_change'].iloc[-1] = down_candle[1]
			
        			max_r, min_r = self.min_max_rate_rep(out_df, cur_buy_price)
        			res_df['av_max_rate'].iloc[-1] = max_r
        			res_df['av_min_rate'].iloc[-1] = min_r

        			sg.one_line_progress_meter('Creatin report in progress...', bar_step+z*len(self.N_candle_analyze)+len(self.N_pre_candle_analyze)*len(buf_df)+cc+1, bar_len, 'Count...', orientation='h')

	# PRE BUY ANALYSIS
        		if len(self.N_pre_candle_analyze) > 1:
        			b_step = len(self.N_pre_candle_analyze)-1
        		else: b_step = 1
		
        		current_profit = 0
        		for cc, n in enumerate(self.N_pre_candle_analyze):
	#            print('cc: ', cc, 'n: ', n)
        			current_index = -b_step+cc
	#            print('current_index: ', current_index)
        			if n == 60 :
        				res_df= pd.concat([res_df, buf_df[rep_columns].iloc[z:z+1]], ignore_index = True) #выдергиваем строку исходного отчета с трейдом и добавляем ее в расширенный отчет
        				if len(self.N_pre_candle_analyze) > 1:
        					b_step = len(self.N_pre_candle_analyze)
        				else: b_step = 1
        				current_index = -b_step+cc
        				res_df['analyze_N'].iloc[current_index] = n
				
        			res_df['volume'].iloc[current_index] = df_pair_1m['volume'].iloc[buy_pos[0]].copy()
        			out_df =  df_pair_1m[buy_pos[0]-(n+self.N_strategy): buy_pos[0]].copy() #выдергиваем из данных для пары, n-свечей плюс N-сигнальных свечей (зависит от стратегии) для анализа плюс сигнальные свечи
        			out_df['pair'] = i

        			current_profit = res_df['profit_ratio'].iloc[current_index]
	#            print('current_profit: ', current_profit)

        			pre_big_rep_df = pd.concat([pre_big_rep_df, out_df], ignore_index = True)
			
        			res_df['value_AV'].iloc[current_index] = out_df['volume'].iloc[:-self.N_strategy].mean()
        			res_df['value_MV'].iloc[current_index] = out_df['volume'].iloc[:-self.N_strategy].median()
	#            print(out_df['volume'].iloc[-N_strategy:])
        			res_df['value_TV'].iloc[current_index] = out_df['volume'].iloc[-self.N_strategy:].mean()
			
        			if  res_df['value_AV'].iloc[current_index] !=0:
        				res_df['TV/AV'].iloc[current_index] = res_df['value_TV'].iloc[current_index]/res_df['value_AV'].iloc[current_index]
        			else:
        				res_df['TV/AV'].iloc[current_index] = 0
				
        			if res_df['value_MV'].iloc[current_index] !=0:
        				res_df['TV/MV'].iloc[current_index] = res_df['value_TV'].iloc[current_index]/res_df['value_MV'].iloc[current_index]
        			else:
        				res_df['TV/MV'].iloc[current_index] = 0

        			if current_profit > 0:
        				if res_df['value_AV'].iloc[current_index] != 0:
        					res_df['win_TV/AV'].iloc[current_index] = res_df['value_TV'].iloc[current_index]/res_df['value_AV'].iloc[current_index]
        			else:
        			   res_df['win_TV/AV'].iloc[current_index] = 0

        			first_bs_candle_open = out_df['open'].iloc[-self.N_strategy]
        			output = self.sma_rep(out_df['close'].iloc[:-self.N_strategy], first_bs_candle_open)
        			res_df['SMA'].iloc[current_index] = output

        			if current_profit > 0:
        				res_df['Win_SMA'].iloc[current_index] = output
        			else: 
        				res_df['Win_SMA'].iloc[current_index] = 'loss'

	#Заполняем данные на основе свечей 1 час и 24 часа(1 день)
	#Сначала сохраняем имя пары и дату трейда
        		res_df_24['pair'][idnex_count] = i
        		res_df_24['date'][idnex_count] = b
	#Average 24 hours Volume in USDT (in the last 7 or 10 days) - simply from 24h candles data
        		res_df_24['av_24h_volume'][idnex_count] = df_pair_1d['volume'].tail(10).mean()
	#Last 24 hours Volume in USDT - simply from 24h candles data
        		print(i)
        		print(b)
        		print()
        		print(df_pair_1d)
        		print()
        		        		
        		df_temp = df_pair_1d['volume'].loc[df_pair_1d['date'] <= b]
        		print(df_temp)
        		res_df_24['last_24h_volume'][idnex_count] = df_temp.iloc[-2]
	#Average 24 hours Amplitude (in the last 7 or 10 days) - simply from 24h candles data
        		df_temp = df_pair_1d['high']/df_pair_1d['open']*100-100
        		res_df_24['av_24h_amplitude_up'][idnex_count] = df_temp.mean()
        		df_temp = df_pair_1d['low']/df_pair_1d['open']*100-100
        		res_df_24['av_24h_amplitude_down'][idnex_count] = df_temp.mean()
	#Last 24 hours Amplitude - simply from 24h candles data
        		df_temp = df_pair_1d.loc[df_pair_1d['date'] <= b]
        		res_df_24['last_24h_amplitude_up'][idnex_count] = (df_temp['high'].iloc[-2]/df_temp['open'].iloc[-2]*100-100)
        		res_df_24['last_24h_amplitude_down'][idnex_count] = (df_temp['low'].iloc[-2]/df_temp['open'].iloc[-2]*100-100)
	#Last 24 hours SMA - simply from 24h candles data        
        		res_df_24['last_24h_SMA'][idnex_count] = df_temp['close'].iloc[-2]/cur_buy_price*100-100
	#Last 24 hours SMA - calculate 24h from the buy signal
        		df_temp = df_pair_1h.loc[df_pair_1h['date'] <= b]
        		df_temp =  df_temp['close'][-25:-1].mean()
        		res_df_24['last_24h_SMAbuy'][idnex_count] = df_temp/cur_buy_price*100-100


        		if current_profit > 0:
	#WINS Average 24 hours Volume in USDT (in the last 7 or 10 days) - simply from 24h candles data
        			res_df_24['win_av_24h_volume'][idnex_count] = res_df_24['av_24h_volume'][idnex_count]
	#WINS Last 24 hours Volume in USDT - simply from 24h candles data
        			res_df_24['win_last_24h_volume'][idnex_count] = res_df_24['last_24h_volume'][idnex_count]
	#WINS Average 24 hours Amplitude (in the last 7 or 10 days) - simply from 24h candles data
        			res_df_24['win_av_24h_amplitude_up'][idnex_count] = res_df_24['av_24h_amplitude_up'][idnex_count]
        			res_df_24['win_av_24h_amplitude_down'][idnex_count] = res_df_24['av_24h_amplitude_down'][idnex_count]
	#WINS Last 24 hours Amplitude - simply from 24h candles data
        			res_df_24['win_last_24h_amplitude_up'][idnex_count] = res_df_24['last_24h_amplitude_up'][idnex_count]
        			res_df_24['win_last_24h_amplitude_down'][idnex_count] = res_df_24['last_24h_amplitude_down'][idnex_count]
	#WINS Last 24 hours SMA - simply from 24h candles data        
        			res_df_24['win_last_24h_SMA'][idnex_count] = res_df_24['last_24h_SMA'][idnex_count]
	#WINS Last 24 hours SMA - calculate 24h from the buy signal
        			res_df_24['win_last_24h_SMAbuy'][idnex_count] = res_df_24['last_24h_SMAbuy'][idnex_count]
        		else: 
        				res_df_24['win_av_24h_volume'][idnex_count] = 'loss'
        				res_df_24['win_last_24h_volume'][idnex_count] = 'loss'
        				res_df_24['win_av_24h_amplitude_up'][idnex_count] = 'loss'
        				res_df_24['win_av_24h_amplitude_down'][idnex_count] = 'loss'
        				res_df_24['win_last_24h_amplitude_up'][idnex_count] = 'loss'
        				res_df_24['win_last_24h_amplitude_down'][idnex_count] = 'loss'
        				res_df_24['win_last_24h_SMA'][idnex_count] = 'loss'
        				res_df_24['win_last_24h_SMAbuy'][idnex_count] = 'loss'

        		idnex_count += 1
			
        	bar_step += len(buf_df)*(len(self.N_candle_analyze)+len(self.N_pre_candle_analyze))
        	#print('last step', bar_step)

        for cc, n in enumerate(self.N_candle_analyze):
        	res_df_filtred = res_df.loc[res_df['analyze_N'] == n]
	#    print(res_df_filtred)
        	if len(res_df_filtred['retio_of_max']) > 0:
        		gy = res_df_filtred['retio_of_max'].sum()/len(res_df_filtred['retio_of_max'])*100
        		report_df['retio_of_max'].iloc[cc] = gy
        	report_df['sma'].iloc[cc] = res_df_filtred['sma'].mean()
        	report_df['av_green'].iloc[cc] = res_df_filtred['av_green'].mean()
        	report_df['av_red'].iloc[cc] = res_df_filtred['av_red'].mean()
	
		# необходимо отсекать нулевые значения при подсчете среднего
        	report_df['av_change_green'].iloc[cc] = res_df_filtred['av_change_green'].loc[res_df_filtred['av_change_green'] != 0].mean()
        	report_df['av_change_red'].iloc[cc] = res_df_filtred['av_change_red'].loc[res_df_filtred['av_change_red'] != 0].mean()
	
        	report_df['max_price%'].iloc[cc] = res_df_filtred['max_price%'].mean()
        	report_df['min_price%'].iloc[cc] = res_df_filtred['min_price%'].mean()
        	report_df['av_up_price'].iloc[cc] = res_df_filtred['av_up_price'].mean()
        	report_df['av_down_price'].iloc[cc] = res_df_filtred['av_down_price'].mean()
	
		# необходимо отсекать нулевые значения при подсчете среднего
        	report_df['av_up_price_change'].iloc[cc] = res_df_filtred['av_up_price_change'].loc[res_df_filtred['av_up_price_change'] != 0].mean()
        	report_df['av_down_price_change'].iloc[cc] = res_df_filtred['av_down_price_change'].loc[res_df_filtred['av_down_price_change'] != 0].mean()

		#Average minimum price, expressed as % change from buying price (ONLY LOSSES/NEGATIVE)
        	report_df['av_loss_min_price%'].iloc[cc] = res_df_filtred.loc[( res_df['profit_ratio'] < 0)]['min_price%'].mean()

        	report_df['av_max_rate'].iloc[cc] = res_df_filtred['av_max_rate'].mean()
        	report_df['m_max_rate'].iloc[cc] = res_df_filtred['av_max_rate'].median()
        	report_df['av_min_rate'].iloc[cc] = res_df_filtred['av_min_rate'].mean()
        	report_df['m_min_rate'].iloc[cc] = res_df_filtred['av_min_rate'].median()

        for cc, n in enumerate(self.N_pre_candle_analyze):
        	res_df_filtred = res_df.loc[res_df['analyze_N'] == n]
	#    print('cc: ', cc, 'n: ', n)
        	report_df['TV/AV'].iloc[cc+4] = res_df_filtred['TV/AV'].loc[res_df_filtred['TV/AV'] != 0].mean()

        	report_df['TV/MV'].iloc[cc+4] = res_df_filtred['TV/MV'].loc[res_df_filtred['TV/MV'] != 0].mean()
		
        	report_df['win_TV/AV'].iloc[cc+4] = res_df_filtred['win_TV/AV'].loc[res_df_filtred['win_TV/AV'] != 0].mean()

        	report_df['SMA'].iloc[cc+4] = res_df_filtred['SMA'].mean()
	
        	report_df['Win_SMA'].iloc[cc+4] = res_df_filtred['Win_SMA'].loc[res_df_filtred['Win_SMA'] != 'loss'].mean()
	
	#print(pre_report_df)
	#print(report_df)

        list_of_columns = report_df_2.columns.tolist()

        for num, col_name in enumerate(list_of_columns):
        	report_df_2[col_name] = res_df_24[col_name].loc[res_df_24[col_name] != 'loss'].mean()


	# create excel writer 
        #writer = pd.ExcelWriter(work_path+'/backtest_results/'+f_name.split('.')[0]+'_t1.xlsx')
        writer = pd.ExcelWriter('reports/'+f_name.split('.')[0]+'_t1.xlsx')

	# write dataframe to excel sheet named 'trades' 
	#df.to_excel(writer, 'Trades') # save the excel file
        report_df.to_excel(writer, 'Report') # save the excel file
        res_df.to_excel(writer, 'Global') # save the excel file
        res_df_24.to_excel(writer, '24_hour') # save the excel file

        report_df_2.to_excel(writer, sheet_name='Report', index=False, startrow=12, startcol=2)
	#report_df_2.to_excel(writer, 'average_24_hour', index = False) # save the excel file

	#big_rep_df.to_excel(writer, 'Pairs blocks') # save the excel file


	#pre_report_df.to_excel(writer, 'Pre_Report') # save the excel file
	#pre_df.to_excel(writer, 'Pre Buy Analysis') # save the excel file
	#pre_big_rep_df.to_excel(writer, 'Pre Pairs blocks') # save the excel file
        writer.save()



        #print(f_name+'_t1.xlsx is wrote!')
