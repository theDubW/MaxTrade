# MaxTrade
An experimental stock and options trading program I built from the ground up in Python.
Log into your Robinhood account with secure authentication and easily view your positions, as well as your profit, equity, percent change, and many other data points. 
For the trading bot, you can set stop loss or take profit percentages for both your stocks and specific options contracts. Simply select the desired item, the quantity, and the percentages that you want to automatically sell at. Now you no longer have to constantly check prices and can prevent yourself from being too greedy (or falling into a sunk cost fallacy).

# How to run #
1. First, either clone or download this repository.
2. Make sure you have [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) (python package) installed, as it is used for all the necessary python dependencies.
3. Navigate to the parent directory (the one containing main.py), and create a new conda environment with `conda env create -f requirements.yml` in your terminal. Then activate your environment with `conda activate MaxTrade`.
4. You're done! All you need to do now is run main.py, which you can do simply by running `python main.py` in your terminal, or if you would prefer, double click on run.bat (Windows) or run.sh (Mac/Linux)
5. A new window with a login should open up on your first run, and the following times you should remain logged in and the main window will open automatically.

Disclaimer: I make no claims of responsibility if something goes wrong. Please treat this as an experimental tool, but it's open source, so feel free to build on it.  
