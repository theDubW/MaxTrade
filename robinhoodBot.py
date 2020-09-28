import robin_stocks as r
import keyring as k

def getUserInfo():
    username = k.get_password("MaxTradeBot", "BotUserName")
    return {"username":username, "password":k.get_password("MaxTrade", username)}
def percentChange(option, info):
    return round((float(info['mark_price'])*float(option['trade_value_multiplier'])/float(option['average_price'])-1.0)*100.0,2)
def getOptionInfo(option):
    inst = option['option']
    inst=inst[:len(inst)-1]
    inst = inst[str.rfind(inst, '/'):]
    return r.options.get_option_market_data_by_id(inst)
def getInstrData(option):
    inst = option['option']
    inst=inst[:len(inst)-1]
    inst = inst[str.rfind(inst, '/'):]
    inst = inst[1:]
    return r.options.get_option_instrument_data_by_id(inst)

if(k.get_password("MaxTradeBot", "BotUserName") == ""):
    username = input("Robinhood Email/Username:")
    password = input("Robinhood Password:")
    k.set_password("MaxTradeBot", "BotUserName", username)
    k.set_password("MaxTrade", k.get_password("MaxTradeBot", "BotUserName"), password)
else:
    a = r.authentication.login(username=getUserInfo()["username"],password=getUserInfo()["password"],by_sms=False)

stock_positions = r.account.build_holdings()
option_positions =  r.options.get_open_option_positions()


#PRINTING CURRENT STOCK POSITIONS
print("Stock Positions")
print("Ticker--------------Quantity---------------Equity-------------------Percent Change")
for stock in stock_positions:
    print(stock+"                "+stock_positions[stock]['quantity']+"          $"+stock_positions[stock]['equity']+"                         "+stock_positions[stock]['percent_change']+"%")
print("\n \n \n")

#PRINTING CURRENT OPTION POSITIONS
print("Option Positions")
print("Ticker--------------Strike Price----------Option Type----------Expiration Date-------Number of Contracts--------Percent Change")
for option in option_positions:
    info = getOptionInfo(option)
    instr = getInstrData(option)
    # print(option)
    # print(info)
    # print(instr)
    print(option['chain_symbol']+"                   "+str(instr['strike_price'])+"               "+option['type']+" "+instr['type']+"             "+instr['expiration_date']+"             "+option['quantity']+"                    "+str(percentChange(option, info))+"%")

stock_stops = {}
#ASKING FOR STOCK STOP LOSS/GAIN
print("STOCKS STOP LOSS AND TAKE PROFIT: ")
for stock in stock_positions:
    print("---------------------------------------------------------------------------------------------------------------------------------------------")
    set_stop = input("Would you like to set a stop loss/take profit for "+stock+"? (y/n)")
    if(set_stop=="y"):
        stock_stops[stock] = {"stop_loss":0.0, "take_profit":0.0}
        confirm_loss = "n"
        stop_loss = 0
        confirm_gain = "n"
        take_profit = 0
        while(confirm_loss != "y"):
            stop_loss = float(input("What is the stop loss percentage (do not put negative sign), if you do not want to set a stop loss, input 0.\n"))
            confirm_loss = input("Stop loss set: -"+str(stop_loss)+"%. Confirm: (y/n)\n")
        stock_stops[stock]["stop_loss"] = stop_loss
        while(confirm_gain != "y"):
            take_profit = float(input("What is the take profit percentage (do not put negative sign), if you do not want to set a take profit, input 0.\n"))
            confirm_gain = input("Take profit set: "+str(take_profit)+"%. Confirm: (y/n)\n")
        stock_stops[stock]["take_profit"] = take_profit

options_stops = {}
#ASKING FOR OPTION STOP LOSS/GAIN
print("OPTIONS STOP LOSS AND TAKE PROFIT: ")
for option in option_positions:
    print("---------------------------------------------------------------------------------------------------------------------------------------------")
    ticker = option['chain_symbol']
    set_stop = input("Would you like to set a stop loss/take profit for "+ticker+"? (y/n)")
    if(set_stop=="y"):
        options_stops[ticker] = {"stop_loss":0.0, "take_profit":0.0}
        confirm_loss = "n"
        stop_loss = 0
        confirm_gain = "n"
        take_profit = 0
        while(confirm_loss != "y"):
            stop_loss = float(input("What is the stop loss percentage (do not put negative sign), if you do not want to set a stop loss, input 0.\n"))
            confirm_loss = input("Stop loss set: -"+str(stop_loss)+"%. Confirm: (y/n)\n")
        options_stops[ticker]["stop_loss"] = stop_loss
        while(confirm_gain != "y"):
            take_profit = float(input("What is the take profit percentage (do not put negative sign), if you do not want to set a take profit, input 0.\n"))
            confirm_gain = input("Take profit set: "+str(take_profit)+"%. Confirm: (y/n)\n")
        options_stops[ticker]["take_profit"] = take_profit
print(stock_stops)
print(options_stops)