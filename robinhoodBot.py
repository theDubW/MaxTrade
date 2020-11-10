import robin_stocks as r
import keyring as k
import pandas as pd
import pickle

from PySide2.QtCore import Signal, QObject

class Robinhood(QObject):
    sold_stock_signal = Signal(list,name="StockPositionSold")
    def __init__(self):
        super(Robinhood, self).__init__()
        self.stock_positions = {}
        empty_dic = {}
        temp_outfile = open("Sell_Stock_Positions","wb")
        pickle.dump(empty_dic, temp_outfile)
        temp_outfile.close()
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
    def sellStockPosition(self, ticker, quantity, stop_loss, take_profit):
        # Setting Stop Loss
        print("Stop %:{}".format(stop_loss))
        stopPrice = round(float(self.getStockPosition(ticker)['average_buy_price'])*(1-stop_loss/100.0),2)
        out_order = r.orders.order(ticker,quantity,"limit",trigger="stop",side="sell",priceType=None,limitPrice=stopPrice,stopPrice=stopPrice,timeInForce="gtc",extendedHours=False)
        print(out_order)
        # out_order = {'id':'SAMPLE_SELL_ID'}
        order = {'bought_price':float(self.getStockPosition(ticker)['average_buy_price']), 'take_profit':round(float(self.getStockPosition(ticker)['average_buy_price'])*(1+take_profit/100.0),1), 'stop_loss':stopPrice, 'quantity':quantity, "id":out_order['id']}
        infile = open("Sell_Stock_Positions", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        curr_orders[ticker] = order
        outfile = open("Sell_Stock_Positions",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Cancels all stock orders for a given ticker
    def cancelAllStockOrders(self, ticker):
        currOrders = r.get_all_open_stock_orders()
        for order in currOrders:
            if(r.stocks.get_instrument_by_url(order['instrument'],"symbol")==ticker):
                r.orders.cancel_stock_order(order['id'])
    #Check if stock sell has been executed
    def checkStockSold(self, orderId):
        pastOrders = r.get_all_stock_orders('id')
        # pastOrders.append("SAMPLE_SELL_ID")
        # pastOrders.append("SAMPLE_TAKE_PROFIT_ID")
        if(orderId in pastOrders):
            orderInfo = r.get_stock_order_info(orderId)
            if orderInfo['state'] == "filled":
                return True
        return False
    # def soldPosition(orders, ticker):
    #     sig = Signal()
    #     sig.emit()
    def getStockSoldInfo(self, orderId, ticker):
        if(orderId != "SAMPLE_TAKE_PROFIT_ID"):
            info = r.get_stock_order_info(orderId)
        else:
            orders = self.getCurrStockOrders()[ticker]
            info = {"cumulative_quantity":orders['quantity'], "average_price":orders['take_profit']}
        return {'quantity':float(info['cumulative_quantity']), 'sell_price':float(info['average_price'])}
    #Deletes order from pickle file
    def deleteStockOrder(self, ticker):
        infile = open("Sell_Stock_Positions", 'rb')
        curr_orders = pickle.load(infile)
        curr_orders.pop(ticker)
        infile.close()
        outfile = open("Sell_Stock_Positions",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Return current orders dictionary
    def getCurrStockOrders(self):
        infile = open("Sell_Stock_Positions", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        return curr_orders
    def updateStockHoldings(self):
        self.stock_positions = r.account.build_holdings()
    def updateStocks(self):
        self.updateStockHoldings()
        orders = self.getCurrStockOrders()
        for order in orders:
            print("ORDER ID: {}".format(orders[order]['id']))
            if(self.checkStockSold(orders[order]['id'])):
                info = self.getStockSoldInfo(orders[order]['id'], order)
                print("SOLD {} POSITION FOR {}".format(order, info['sell_price']))
                self.sold_stock_signal.emit([info['quantity'], order, info['sell_price'], round((info['sell_price']/orders[order]['bought_price']-1)*100, 2)])
                self.deleteStockOrder(order)
            elif float(self.getStockPosition(order)['price']) >= orders[order]['take_profit']:
                print("Canceling")
                self.cancelAllStockOrders(order)
                print("Selling")
                out_order = r.orders.order(order, orders[order]['quantity'],"market",trigger="immediate",side="sell",priceType=None,limitPrice=None,stopPrice=None,timeInForce="gtc",extendedHours=False)
                # out_order = {'id':"SAMPLE_TAKE_PROFIT_ID"}
                infile = open("Sell_Stock_Positions", 'rb')
                curr_orders = pickle.load(infile)
                infile.close()
                curr_orders[order]['id'] = out_order['id'] 
                outfile = open("Sell_Stock_Positions",'wb')
                pickle.dump(curr_orders, outfile)
                outfile.close()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#   OPTION POSITIONS METHODS
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    
