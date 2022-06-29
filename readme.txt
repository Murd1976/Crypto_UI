User's manual.

When the application starts and subsequent commands are executed, 
service information is displayed in the message window (at the bottom of the window).

1. “Connect” button – connects the application to the server and 
loads the list of available strategies and the list of saved test results 
in .json format from the user's folder.
To connect, you must enter a username and password.
Pressing the button again refreshes the loaded lists.

2. To start creating a report based on the test results, select the 
appropriate .json file from the list.
As a result, two report files will be created: a .txt file with a 
summary table of test results and an .xlsx file with 
advanced analytics of test results.
The execution process is displayed in the progress bar and may take several minutes, 
depending on the number of trades signals.

3. To launch a backtest, you need to select the appropriate strategy from 
the list and set the desired strategy parameters for testing.
Because the list of pairs available on Binance is divided into four parts - you need 
to choose which of these parts to run the backtest with.
When a strategy is selected, its parameters are set to the default values ​​contained in the 
base configuration file of the corresponding strategy.
A summary text table with the test results can be seen in the information field after the end 
of the backtest. 
Or in a text file after starting the report creation.
The progress is displayed in the progress bar and may take several minutes.
To see the .json files of the results of the latest tests, you need to refresh the list by 
clicking the "Connect" button

4. The ssh_my_config.conf file contains the server address, connection port 
and user directory where test results will be saved in .json format.
You can specify any name of the user directory - such a directory will be created 
on the server and saving/reading of test results will be performed from this directory.

