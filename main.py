import sys  # sys нужен для передачи argv в QApplication
import os
import re
import pandas as pd
from datetime import datetime, date, time

from PyQt5 import QtWidgets
import  subprocess

import design  # Это наш конвертированный файл дизайна
from global_report_24 import rep_from_test_res# файл с функциями построения отчета

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    directory = ''
    
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        
        self.btnBrose.clicked.connect(self.browse_folder)
        self.btnExit.clicked.connect(self.exit_prog)
        self.btnRunBT.clicked.connect(self.run_backtest)
        self.btnReport.clicked.connect(self.run_report)
        
        self.checkROI_1.stateChanged.connect(self.roi_anable)
        self.checkROI_2.stateChanged.connect(self.roi_anable)
        self.checkROI_3.stateChanged.connect(self.roi_anable)
        self.checkROI_4.stateChanged.connect(self.roi_anable)
        #self.listBtResults.currentItemChan.stateChanged.connect(ged.connect(self.print_info)
        
        
    def browse_folder(self):
        self.comboBackTest.clear()  # На случай, если в списке уже есть элементы
        self.comboStrategies.clear()
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку", "C:/Users/Denis/ft_userdata")

        self.listInfo.addItem(self.directory)
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if self.directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            
            for file_name in os.listdir(self.directory+'/backtest_results'):  # для каждого файла в директории
                if file_name != '.last_result.json':
                    splited_str = file_name.split('.')
                    if len(splited_str) == 2:
                        if splited_str[1] == 'json': 
                            self.comboBackTest.addItem(file_name)   # добавить файл в listBtResults
            for file_name in os.listdir(self.directory+'/strategies'):  # для каждого файла в директории
                splited_str = file_name.split('.')
                if len(splited_str) == 2:
                    if splited_str[1] == 'py': 
                        self.comboStrategies.addItem(file_name) # добавить файл в listStrategies

    def print_info(self):
     #   self.listInfo.addItem(self.listBtResults.currentRow())
        self.listInfo.addItem(self.listBtResults.currentItem().text())
     #   self.listInfo.addItem(self.listBtResults.currentItem().isSelected())

    def get_strategy(self, f_name: str):
        strategy_name = 'none'
        with open(self.directory+'/strategies/'+f_name, 'r') as f:
            for line in f:
                if ('class' in line) and ('IStrategy' in line):
                    pars_str1 = line.split()
                    pars_str = pars_str1[1].split('(') #re.split(' |()', line)
                    strategy_name = pars_str[0]
                    #self.listInfo.addItem(line)
                    self.listInfo.addItem("Strategi name: ")
                    self.listInfo.addItem(strategy_name)
                    self.listInfo.addItem('________________________________________')
                    #for i in range(len(pars_str)):
                        #self.listInfo.addItem(" Len: "+ str(len(pars_str)))
                        #self.listInfo.addItem(str(pars_str[i]))
        f.close()
        
        return strategy_name

    def run_report(self):
        my_rep = rep_from_test_res()
        backtest_file_name = self.comboBackTest.currentText()
        self.listInfo.addItem("Creatin report, please wait... ")
        my_rep.get_report(self.directory, backtest_file_name)

        self.listInfo.addItem("Created report: ")
        self.listInfo.addItem(backtest_file_name.split('.')[0]+'_t1.xlsx')
        self.listInfo.addItem('________________________________________')
        rep_done =True
        return rep_done
    
    def run_backtest(self):

        buf_str = self.get_strategy(self.comboStrategies.currentText())
        if buf_str != 'none':
            datadir = " --datadir user_data/data/binance "
            export = " --export trades "
            config = " --config config_p4.json "
            export_filename = " --export-filename user_data/backtest_results/bc_" + self.lineEdit_N.text() +'_' + buf_str + '.json'

            strategy = " -s "+ buf_str
            
            run_str = "docker-compose run --rm freqtrade backtesting " + datadir+export+ config+ export_filename+strategy
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

        file_path = 'config_param.py'
        with open(file_path, 'w') as out_file:
            out_file.write('#  '+datetime.now().strftime('%Y-%m-%d / %H:%M:%S')+'\n \n')
            out_file.write('class config_strategy(self): \n')
            
            for buf_str in strategy_settings:
                out_file.write(buf_str+'\n')

        out_file.close()

        self.listInfo.addItem('Settings for current test:')
        for buf_str in strategy_settings:
            self.listInfo.addItem(buf_str)
        self.listInfo.addItem('________________________________________')

        #os.system("cd C:\\Users\\Denis\\ft_userdata\\user_data\\docker-compose ps" )
        
        cmd = "cd /d C:\\Users\\Denis\\ft_userdata\\user_data"
        #subprocess.Popen(cmd, shell = True)
        

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

    def exit_prog(self):
        exit()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()    
