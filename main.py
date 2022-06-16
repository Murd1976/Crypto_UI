import sys  # sys нужен для передачи argv в QApplication
import os
import re
import pandas as pd
from datetime import datetime, date, time
import time as ttime

from PyQt5 import QtWidgets
import  subprocess
import paramiko
import socket

import design  # Это наш конвертированный файл дизайна
from global_report_24 import rep_from_test_res  # файл с функциями построения отчета
from test_json_to_txt import my_reports  # файл с функциями построения форматированного текстового отчета

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    server_directory = '/home/murd/buf/ft_userdata/'
    server_strategy_directory = '/user_data/strategies/'
    server_backtests_directory = '/user_data/backtest_results/'
    server_user_directory = ''
    client_directory = ''
    reports_directory = './reports/'

    # Информация о сервере, имя хоста (IP-адрес), номер порта, имя пользователя и пароль

    hostname = "172.18.90.46"
    port = 2222
    username = "murd"
    password = "Ambaloid!"
    
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        
        self.btnBrose.clicked.connect(self.browse_folder)
        self.btnExit.clicked.connect(self.exit_prog)
        self.btnRunBT.clicked.connect(self.run_backtest)
        self.btnReport.clicked.connect(self.run_report)
        self.btnConnect.clicked.connect(self.connect_ssh)
        
        self.checkROI_1.stateChanged.connect(self.roi_anable)
        self.checkROI_2.stateChanged.connect(self.roi_anable)
        self.checkROI_3.stateChanged.connect(self.roi_anable)
        self.checkROI_4.stateChanged.connect(self.roi_anable)
        #self.listBtResults.currentItemChan.stateChanged.connect(ged.connect(self.print_info)

        self.comboStrategies.activated.connect(self.param_of_cur_strategy)
        self.comboStrategies.currentIndexChanged.connect(self.param_of_cur_strategy)

#        self.lineEdit_Login.selectAll()
#        self.lineEdit_Password.selectAll()
        
        
    def browse_folder(self):
        self.comboBackTest.clear()  # На случай, если в списке уже есть элементы
        self.comboStrategies.clear()
        self.client_directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку", "C:/Users/Denis/ft_userdata")
#        self.directory = QtWidgets.QFileDialog.getExistingDirectoryUrl(self, "Выберите папку", "https://172.18.90.46/home/murd")

        self.listInfo.addItem(self.directory)
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if self.client_directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            
            for file_name in os.listdir(self.client_directory+'/backtest_results'):  # для каждого файла в директории
                if file_name != '.last_result.json':
                    splited_str = file_name.split('.')
                    if len(splited_str) == 2:
                        if splited_str[1] == 'json': 
                            self.comboBackTest.addItem(file_name)   # добавить файл в listBtResults
            for file_name in os.listdir(self.client_directory+'/strategies'):  # для каждого файла в директории
                splited_str = file_name.split('.')
                if len(splited_str) == 2:
                    if splited_str[1] == 'py': 
                        self.comboStrategies.addItem(file_name) # добавить файл в listStrategies

    def connect_ssh(self):

        # На случай, если в списке уже есть элементы
        self.comboBackTest.clear()
        self.comboStrategies.clear()
        
#        self.server_directory ='/home/murd/buf/ft_userdata'
        max_bytes=60000

        self.username = self.lineEdit_Login.text()
        self.password = self.lineEdit_Password.text()
        
         # Создать объект SSH
        self.listInfo.addItem("Runing SSH...")
        self.listInfo.addItem("Host name: " + self.hostname)
        self.listInfo.addItem("Port: " + str(self.port))
                
        client = paramiko.SSHClient()
         # Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
         # подключиться к серверу
        try:
            client.connect(self.hostname, self.port, self.username, self.password, compress=True)
                        
        except Exception as e:
            self.listInfo.addItem('Error connection to server: ' + str (e))
            #self.listInfo.addItem("Invalid login/password!")
            self.listInfo.addItem('________________________________________')
            return
            
        else:
            self.listInfo.addItem("Connected to server!")
            self.listInfo.addItem('________________________________________')

        sftp_client = client.open_sftp()
        #Проверяем наличие, на сервере, полльзователького каталога, если такго не существует - создаем
        try:
            sftp_attributes = sftp_client.stat(self.server_directory + self.server_backtests_directory+self.server_user_directory)
        except Exception as e:
#            self.listInfo.addItem('Error connection to server: ' + str (e))
            sftp_client.mkdir(self.server_directory + self.server_backtests_directory+self.server_user_directory)
            self.listInfo.addItem("Created user directory: " + self.server_user_directory)
#        print(sftp_attributes)

         # Выполнить команду linux
        command = 'ls /' + self.server_directory + self.server_strategy_directory
        
        stdin, stdout, stderr = client.exec_command(command)

#        for line in stdout:
#             self.listInfo.addItem(line.strip('\n'))

        for file_name in stdout:  # для каждого файла в директории
            file_name = file_name.strip('\n')
            splited_str = file_name.split('.')
            if len(splited_str) == 2:
               if splited_str[1] == 'py':
                  splited_str2 = splited_str[0].split('_')
                  if splited_str2[0] in ['min']:
                     self.comboStrategies.addItem(file_name) # добавить файл в listStrategies

        self.param_of_cur_strategy() # выставляем значения параметров в соответствии с текущей стратегией

        command = 'ls /' + self.server_directory + self.server_backtests_directory + self.server_user_directory
        
        stdin, stdout, stderr = client.exec_command(command)
        for file_name in stdout:  # для каждого файла в директории
            file_name = file_name.strip('\n')
            if file_name != '.last_result.json':
               splited_str = file_name.split('.')
               if len(splited_str) == 2:
                  if splited_str[1] == 'json': 
                     self.comboBackTest.addItem(file_name)   # добавить файл в listBtResults

        if self.comboStrategies.count() > 0:
           self.btnRunBT.setEnabled(True)
        else:
           self.btnRunBT.setEnabled(False)
           
        if self.comboBackTest.count() > 0:
           self.btnReport.setEnabled(True)
        else:
           self.btnReport.setEnabled(False) 
            

        sftp_client.close()

#        commands = [ 'cd /' + self.server_directory + '/user_data/backtest_results', 'docker-compose ps', command]    
#        with client.invoke_shell() as ssh:
            #ssh.send("enable\n")
            #ssh.send(f"{enable}\n")
            #time.sleep(short_pause)
            #ssh.send("terminal length 0\n")
            #time.sleep(short_pause)
            #ssh.recv(max_bytes)

#            self.listInfo.addItem('________________________________________')
#            result = {}
#            for command_ in commands:
#                ssh.send(f"{command_}\n")
#                ssh.settimeout(1)

#                output = ""
#                while True:
#                    try:
#                        part = ssh.recv(max_bytes).decode("utf-8")
#                        output += part
#                        ttime.sleep(0.5)
#                    except socket.timeout:
#                        break
                #result[command] = output
#                self.listInfo.addItem(output)
#            self.listInfo.addItem('________________________________________')
            
            
    def print_info(self):
     #   self.listInfo.addItem(self.listBtResults.currentRow())
        self.listInfo.addItem(self.listBtResults.currentItem().text())
     #   self.listInfo.addItem(self.listBtResults.currentItem().isSelected())

    def get_strategy(self, f_name: str):

#        self.server_directory ='/home/murd/buf/ft_userdata'
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname, self.port, self.username, self.password, compress=True)
        sftp_client = client.open_sftp()
        remote_file = sftp_client.open (self.server_directory + self.server_strategy_directory + f_name) # Путь к файлу
        try:
            strategy_name = 'none'
            for line in remote_file:
                line = line.strip()
                if ('class' in line) and ('IStrategy' in line):
                    pars_str1 = line.split()
                    pars_str = pars_str1[1].split('(') #re.split(' |()', line)
                    strategy_name = pars_str[0]
                    #self.listInfo.addItem(line)
                    self.listInfo.addItem("Strategy name: ")
                    self.listInfo.addItem(strategy_name)
                    self.listInfo.addItem('________________________________________')
                    #for i in range(len(pars_str)):
                        #self.listInfo.addItem(" Len: "+ str(len(pars_str)))
                        #self.listInfo.addItem(str(pars_str[i]))
        finally:
            remote_file.close()
        
        return strategy_name

    def run_report(self):
        my_txt_rep = my_reports()   #создаем объект нашего собственного класса my_reports()
        
        my_rep = rep_from_test_res() #создаем объект нашего собственного класса rep_from_test_res()
        backtest_file_name = self.comboBackTest.currentText()

#        self.server_directory ='/home/murd/buf/ft_userdata'
        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username = self.username, password = self.password)
        
        sftp = paramiko.SFTPClient.from_transport(transport)
                        
        #загрузить файл результатов теста на комп пользователя             
        sftp.get(self.server_directory + self.server_backtests_directory +self.server_user_directory + backtest_file_name, self.reports_directory + backtest_file_name)
        sftp.close()
        
#        self.reports_directory = './reports/'

        self.listInfo.addItem("Creating report, please wait... ")
        
        res_report = my_txt_rep.json_to_txt(self.reports_directory, backtest_file_name)
        self.listInfo.addItem("Created report: ")
        self.listInfo.addItem(backtest_file_name.split('.')[0]+'.txt')
        
        res_report = my_rep.get_report(self.reports_directory, backtest_file_name)
        
        os.remove(self.reports_directory + backtest_file_name)

        if res_report == "no_trades":
            self.listInfo.addItem("Created report error: No trades in test results!")
        else:
            self.listInfo.addItem("Created report: ")
            self.listInfo.addItem(backtest_file_name.split('.')[0]+'_t1.xlsx')
        self.listInfo.addItem('________________________________________')
        rep_done =True
        return rep_done

    def get_config_part(self):
        config_str = "p4"
        if self.rbPairsPart1.isChecked():
           config_str = "p1"
        if self.rbPairsPart2.isChecked():
           config_str = "p2"
        if self.rbPairsPart3.isChecked():
           config_str = "p3"
           
        return config_str
    
    def run_backtest(self):

        buf_str = self.get_strategy(self.comboStrategies.currentText())
        file_config = 'usr_' + buf_str + '_config.py'
        max_bytes=160000
        short_pause=1
        long_pause=5
        
        if buf_str != 'none':
            datadir = " --datadir user_data/data/binance "
            export = " --export trades "
            config = " --config user_data/config_" + self.get_config_part() + ".json "
            export_filename = " --export-filename user_data/backtest_results/" + self.server_user_directory + "bc_" + self.lineEdit_N.text() +'_' + self.get_config_part()+ '_' + buf_str + '.json'

            strategy = " -s "+ buf_str
            
            #run_str = "docker-compose run --rm freqtrade backtesting " + datadir+export+ config+ export_filename+strategy
            run_str = "freqtrade backtesting " + datadir+export+ config+ export_filename+strategy
            
            self.listInfo.addItem('Command line for run test:')
            self.listInfo.addItem(run_str)
            self.listInfo.addItem('________________________________________')
        else:
            self.listInfo.addItem('Strategy name not found!!!')
            self.listInfo.addItem('________________________________________')

        # Minimal ROI designed for the strategy.
        not_first = False
        buf_str = '    minimal_roi = { "'
        if self.checkROI_1.checkState():
            buf_str += self.lineEdit_ROI_4_1.text()+ '":  ' + self.normalyze_percents(self.lineEdit_ROI_4_2.text())
            not_first = True
        if self.checkROI_2.checkState():
            if not_first:
                buf_str += ', "'
            buf_str += self.lineEdit_ROI_3_1.text()+ '":  ' + self.normalyze_percents(self.lineEdit_ROI_3_2.text())
            not_first = True
        if self.checkROI_3.checkState():
            if not_first:
                buf_str += ', "'
            buf_str += self.lineEdit_ROI_2_1.text()+ '":  ' + self.normalyze_percents(self.lineEdit_ROI_2_2.text())
            not_first = True
        if self.checkROI_4.checkState():
            if not_first:
                buf_str += ', "'
            buf_str += self.lineEdit_ROI_1_1.text()+ '":  ' + self.normalyze_percents(self.lineEdit_ROI_1_2.text())

        buf_str += '}'
        strategy_settings = pd.Series([buf_str])

        buf_str = '    arg_N =  ' + self.lineEdit_N.text()
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        #arg_X=0
        
        buf_str = '    arg_R =  ' + self.lineEdit_R.text()
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        #- arg_P % price increase in arg_N candles
        buf_str = '    arg_P =  ' + self.lineEdit_P.text()
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)       
           
        #- arg_MR % movement ROI
        buf_str = '    arg_MR =  ' + self.normalyze_percents(self.lineEdit_MR.text())
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # Optimal stoploss designed for the strategy.
        buf_str = '    stoploss = -' + self.normalyze_percents(self.lineEdit_SL.text())
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # Optimal time-depended stoploss designed for the strategy.
        buf_str = '    my_stoploss = np.array([' + self.lineEdit_MySL_1.text() + ', -'+ self.normalyze_percents(self.lineEdit_MySL_2.text()) + '])'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True) 

        #(S = desired Stop-Loss Value)
        buf_str = '    arg_stoploss =  ' + self.normalyze_percents(self.lineEdit_S.text())
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        
        with open(file_config, 'w') as out_file:
            out_file.write('#  '+datetime.now().strftime('%Y-%m-%d / %H:%M:%S')+'\n \n')
            out_file.write('import numpy as np \n')
            out_file.write('class config_strategy(): \n')
            
            # сохранить файл конфигурации тестируемой стратегии в каталоге пользователя
            for buf_str in strategy_settings:
                out_file.write(buf_str+'\n')

        out_file.close()


#        self.directory ='home/murd/buf/ft_userdata'
        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username = self.username, password = self.password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        #загрузить файл конфигурации тестируемой стратегии на сервер
        sftp.put("./" + file_config, '/' + self.server_directory + self.server_strategy_directory + file_config)
        
        sftp.close()

        self.listInfo.addItem('Settings for current test:')
        for buf_str in strategy_settings:
            self.listInfo.addItem(buf_str)

        self.listInfo.addItem('Saved in config file: ' + file_config)   
        self.listInfo.addItem('________________________________________')

        # Создать объект SSH
        self.listInfo.addItem("Runing SSH...") 
        client = paramiko.SSHClient()
         # Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
         # подключиться к серверу
        client.connect(self.hostname, self.port, self.username, self.password, compress=True)
        self.listInfo.addItem("Connected to server!")

         # Выполнить команду linux
        #command = run_str #+ ' /' + self.directory
        #commands = [ 'cd /' + self.directory, run_str]  # набор команд: переход в рабочий каталог; команда(строка) для запуска бектеста с заданными параметрами
        commands = [run_str]  # команда(строка) для запуска бектеста с заданными параметрами
        
        with client.invoke_shell() as ssh:
            ssh.recv(max_bytes)
            self.listInfo.addItem('________________________________________')

#            command = [ "cd /" + self.directory]
#            ssh.send(f"{command}\n")
#            ttime.sleep(short_pause)

#            command = [ "source freqtrade/.env/bin/activate"]
#            ssh.send(f"{command}\n")
#            ttime.sleep(short_pause)

            command = "cd /" + self.server_directory
            ssh.send(f"{command}\n")
            ttime.sleep(short_pause)

            command = "source freqtrade/.env/bin/activate"
            ssh.send(f"{command}\n")
            ttime.sleep(short_pause)

            part = ssh.recv(max_bytes).decode("utf-8")
            self.listInfo.addItem(part) 
            
            result = {}
            for command_ in commands:
                ssh.send(f"{command_}\n")
                ssh.settimeout(170)    #пауза после отправки команды, чтобы дать появиться сопутствующему тексту консоли

                output = ""
                while True:
                    try:
                        part = ssh.recv(max_bytes).decode("utf-8")
                        #output += part
                        self.listInfo.addItem(part)
                        ttime.sleep(0.5)
                    except socket.timeout:
                        break
                #result[command] = output
                #self.listInfo.addItem(output)
            self.listInfo.addItem('________________________________________')
                

    def normalyze_percents(self, num: str):
       buf = float(num)/100
       str_num = str(buf)
       return str_num

    def roi_anable(self):
        if self.checkROI_1.checkState():
            self.gBox_ROI_1.setEnabled(True)
        else: self.gBox_ROI_1.setEnabled(False)

        if self.checkROI_2.checkState():
            self.gBox_ROI_2.setEnabled(True)
        else: self.gBox_ROI_2.setEnabled(False)

        if self.checkROI_3.checkState():
            self.gBox_ROI_3.setEnabled(True)
        else: self.gBox_ROI_3.setEnabled(False)

        if self.checkROI_4.checkState():
            self.gBox_ROI_4.setEnabled(True)
        else: self.gBox_ROI_4.setEnabled(False)

    def param_of_cur_strategy(self):
        if self.comboBackTest.count() > 0 :
           buf_str = self.get_strategy(self.comboStrategies.currentText())
           buf_str = buf_str + '_config.py'
            
           if os.path.exists(buf_str):
               with open(buf_str, 'r') as f:

                   for line in f:
                       line = line.strip()
                       if ('arg_N' in line):
                           pars_str = line.split('=')
                           self.lineEdit_N.setText(pars_str[1].strip())
               f.close()        

    def load_ssh_my_config(self):

        if not os.path.exists("./reports/"):
            os.mkdir("reports")
            self.listInfo.addItem("Created directory: /reports")
#        else:
#            self.listInfo.addItem("Alredy exist.")
        buf_str = 'ssh_my_config.conf'
        if os.path.exists(buf_str):
            f = open(buf_str)
            host_name = 'none'
            port = "22"
            for line in f:
                line = line.strip()
                if ('hostname' in line):
                        pars_str = line.split('=')
                        host_name = pars_str[1].strip()
                        self.hostname = host_name
                        self.listInfo.addItem("Host name: " + host_name)
                    

                if ('port' in line):
                        pars_str = line.split('=')
                        port = pars_str[1]
                        self.port = int(port)
                        self.listInfo.addItem("Port: " + port)

                if ('user_dir' in line):
                        pars_str = line.split('=')
                        self.server_user_directory = pars_str[1].strip() + '/'
                        self.listInfo.addItem('User directory: ' + self.server_user_directory)
                                        
            self.listInfo.addItem('________________________________________')
            f.close()

    def exit_prog(self):
        exit()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.load_ssh_my_config() # load ssh_my_config file
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()    
