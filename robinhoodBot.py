import robin_stocks as r
import keyring as k
import pandas as pd
import pickle

from PySide2.QtCore import Signal, QObject

class Robinhood(QObject):
    sold_stock_signal = Signal()
    def __init__(self):
        super(Robinhood, self).__init__()
        self.stock_positions = {}
        empty_dic = {}
        temp_outfile = open("Sell_Positions","wb")
        pickle.dump(empty_dic, temp_outfile)
        temp_outfile.close()
        # self.sold_stock_signal.connect(self.signalReceived)
    def percentChange(self, option, info):
        return round((float(info['mark_price'])*float(option['trade_value_multiplier'])/float(option['average_price'])-1.0)*100.0,2)
    def getOptionInfo(self, option):
        inst = option['option']
        inst=inst[:len(inst)-1]
        inst = inst[str.rfind(inst, '/'):]
        return r.options.get_option_market_data_by_id(inst)
    def getInstrData(self, option):
        inst = option['option']
        inst=inst[:len(inst)-1]
        inst = inst[str.rfind(inst, '/'):]
        inst = inst[1:]
        return r.options.get_option_instrument_data_by_id(inst)
    def getUserInfo(self):
        username = k.get_password("MaxTradeBot", "BotUserName")
        return {"username":username, "password":k.get_password("MaxTrade", username)}
    #Sets stored username and password based on input
    def setUsernamePW(self, username, password):
        k.set_password("MaxTradeBot", "BotUserName", username)
        k.set_password("MaxTrade", k.get_password("MaxTradeBot", "BotUserName"), password)
    def login(self):
        if(k.get_password("MaxTradeBot", "BotUserName") == None):
            # username = input("Robinhood Email/Username:")
            # password = input("Robinhood Password:")
            # a = r.authentication.login(username=getUserInfo()["username"],password=getUserInfo()["password"],by_sms=False, store_session = True)
            return False
        else:
            print("Username stored:{}, Password Stored:{}".format(self.getUserInfo()["username"], self.getUserInfo()["password"]))
            a = r.authentication.login(username=self.getUserInfo()["username"],password=self.getUserInfo()["password"], store_session = True)
            return a
    def getStockHoldings(self):
        positions = {}
        for stock in self.stock_positions:
            positions[stock] = {"Quantity":float(self.stock_positions[stock]['quantity']), "Equity":float(self.stock_positions[stock]['equity']), "Percent Change":float(self.stock_positions[stock]['percent_change'])}
        pos_to_pd = pd.DataFrame.from_dict(positions, orient='index', columns=["Quantity","Equity","Percent Change"])
        return pos_to_pd
    def getStockPosition(self, ticker):
        return self.stock_positions[ticker]
    def getOptionPositions(self):
        option_positions =  r.options.get_open_option_positions()
        positions = {}
        for option in option_positions:
            info = self.getOptionInfo(option)
            instr = self.getInstrData(option)
            positions[option['chain_symbol']] = {"Strike Price":instr['strike_price'], "Type":option['type']+" "+instr['type'],"Expiration Date":instr['expiration_date'],"Quantity":option['quantity'],"Market Price":info['mark_price'],"Percent Change":percentChange(option, info)}
        pos_to_pd = pd.DataFrame.from_dict(positions, orient='index', columns=["Strike Price","Type","Expiration Date","Quantity","Market Price", "Percent Change"])
        return pos_to_pd
    def sellStockPosition(self, ticker, quantity, stop_loss, take_profit):
        # Setting Stop Loss
        stopPrice = round(float(self.getStockPosition(ticker)['average_buy_price'])*(1+stop_loss/100.0),1)
        #out_order = r.orders.order(ticker,quantity,"limit",trigger="stop",side="sell",priceType=None,limitPrice=stopPrice,stopPrice=stopPrice,timeInForce="gtc",extendedHours=False)
        out_order = {'id':'SAMPLE_SELL_ID'}
        order = {'take_profit':round(float(self.getStockPosition(ticker)['average_buy_price'])*(1+take_profit/100.0),1), 'stop_loss':stopPrice, 'quantity':quantity, "stop_id":out_order['id']}
        infile = open("Sell_Positions", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        curr_orders[ticker] = order
        outfile = open("Sell_Positions",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Cancels all stock orders for a given ticker
    def cancelAllOrders(self, ticker):
        currOrders = r.get_all_open_stock_orders()
        for order in currOrders:
            if(r.stocks.get_instrument_by_url(order['instrument'],"symbol")==ticker):
                r.orders.cancel_stock_order(order['id'])
    #Check if sell has been executed
    def checkSold(self, orderId):
        pastOrders = r.get_all_stock_orders('id')
        # pastOrders.append("SAMPLE_SELL_ID")
        pastOrders.append("SAMPLE_TAKE_PROFIT_ID")
        if(orderId in pastOrders):
            return True
        return False
    # def soldPosition(orders, ticker):
    #     sig = Signal()
    #     sig.emit()
    def signalReceived(self):
        print("SIGNAL RECIEVED SELL")

    #Deletes order from pickle file
    def deleteOrder(self, ticker):
        infile = open("Sell_Positions", 'rb')
        curr_orders = pickle.load(infile)
        curr_orders.pop(ticker)
        infile.close()
        outfile = open("Sell_Positions",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Return current orders dictionary
    def getCurrOrders(self):
        infile = open("Sell_Positions", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        return curr_orders
    def updateHoldings(self):
        self.stock_positions = r.account.build_holdings()
    def update(self):
        self.updateHoldings()
        orders = self.getCurrOrders()
        for order in orders:
            if("stop_id" in orders[order] and self.checkSold(orders[order]['stop_id'])):
                print("SOLD {} POSITION FOR {} LOSS".format(order, orders[order]['stop_loss']))
                self.sold_stock_signal.emit()
                self.deleteOrder(order)
            elif("take_profit_id" in orders[order] and self.checkSold(orders[order]['take_profit_id'])):
                print("SOLD {} POSITION FOR {} PROFIT".format(order, orders[order]['take_profit']))
                self.sold_stock_signal.emit()
                self.deleteOrder(order)
            elif float(self.getStockPosition(order)['price']) >= orders[order]['take_profit']:
                print("Canceling")
                self.cancelAllOrders(order)
                print("Selling")
                #out_order = r.orders.order(order, orders[order]['quantity'],"market",trigger="immediate",side="sell",priceType=None,limitPrice=None,stopPrice=None,timeInForce="gtc",extendedHours=False)
                out_order = {'id':"SAMPLE_TAKE_PROFIT_ID"}
                infile = open("Sell_Positions", 'rb')
                curr_orders = pickle.load(infile)
                infile.close()
                curr_orders[order]['take_profit_id'] = out_order['id'] 
                outfile = open("Sell_Positions",'wb')
                pickle.dump(curr_orders, outfile)
                outfile.close()
# stock_positions = r.account.build_holdings()
# option_positions =  r.options.get_open_option_positions()


#PRINTING CURRENT STOCK POSITIONS
# print("Stock Positions")
# print("Ticker--------------Quantity---------------Equity-------------------Percent Change")
# for stock in stock_positions:
#     print(stock+"                "+stock_positions[stock]['quantity']+"          $"+stock_positions[stock]['equity']+"                         "+stock_positions[stock]['percent_change']+"%")
# print("\n \n \n")

#PRINTING CURRENT OPTION POSITIONS
# print("Option Positions")
# print("Ticker--------------Strike Price----------Option Type----------Expiration Date-------Number of Contracts--------Percent Change")
# for option in option_positions:
#     info = getOptionInfo(option)
#     instr = getInstrData(option)
#     # print(option)
#     # print(info)
#     # print(instr)
#     print(option['chain_symbol']+"                   "+str(instr['strike_price'])+"               "+option['type']+" "+instr['type']+"             "+instr['expiration_date']+"             "+option['quantity']+"                    "+str(percentChange(option, info))+"%")

# stock_stops = {}
#ASKING FOR STOCK STOP LOSS/GAIN
# print("STOCKS STOP LOSS AND TAKE PROFIT: ")
# for stock in stock_positions:
#     print("---------------------------------------------------------------------------------------------------------------------------------------------")
#     set_stop = input("Would you like to set a stop loss/take profit for "+stock+"? (y/n)")
#     if(set_stop=="y"):
#         stock_stops[stock] = {"stop_loss":0.0, "take_profit":0.0}
#         confirm_loss = "n"
#         stop_loss = 0
#         confirm_gain = "n"
#         take_profit = 0
#         while(confirm_loss != "y"):
#             stop_loss = float(input("What is the stop loss percentage (do not put negative sign), if you do not want to set a stop loss, input 0.\n"))
#             confirm_loss = input("Stop loss set: -"+str(stop_loss)+"%. Confirm: (y/n)\n")
#         stock_stops[stock]["stop_loss"] = stop_loss
#         while(confirm_gain != "y"):
#             take_profit = float(input("What is the take profit percentage (do not put negative sign), if you do not want to set a take profit, input 0.\n"))
#             confirm_gain = input("Take profit set: "+str(take_profit)+"%. Confirm: (y/n)\n")
#         stock_stops[stock]["take_profit"] = take_profit

# options_stops = {}
#ASKING FOR OPTION STOP LOSS/GAIN
# print("OPTIONS STOP LOSS AND TAKE PROFIT: ")
# for option in option_positions:
#     print("---------------------------------------------------------------------------------------------------------------------------------------------")
#     ticker = option['chain_symbol']
#     set_stop = input("Would you like to set a stop loss/take profit for "+ticker+"? (y/n)")
#     if(set_stop=="y"):
#         options_stops[ticker] = {"stop_loss":0.0, "take_profit":0.0}
#         confirm_loss = "n"
#         stop_loss = 0
#         confirm_gain = "n"
#         take_profit = 0
#         while(confirm_loss != "y"):
#             stop_loss = float(input("What is the stop loss percentage (do not put negative sign), if you do not want to set a stop loss, input 0.\n"))
#             confirm_loss = input("Stop loss set: -"+str(stop_loss)+"%. Confirm: (y/n)\n")
#         options_stops[ticker]["stop_loss"] = stop_loss
#         while(confirm_gain != "y"):
#             take_profit = float(input("What is the take profit percentage (do not put negative sign), if you do not want to set a take profit, input 0.\n"))
#             confirm_gain = input("Take profit set: "+str(take_profit)+"%. Confirm: (y/n)\n")
#         options_stops[ticker]["take_profit"] = take_profit
# print(stock_stops)
# print(options_stops)