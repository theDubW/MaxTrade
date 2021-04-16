import robin_stocks as r
import pandas as pd
import pickle


from PySide2.QtCore import Signal, QObject

class OptionsBot(QObject):
    sold_option_signal = Signal(list,name="OptionSold")
    output = Signal(str, name="Output")
    def __init__(self):
        super(OptionsBot, self).__init__()
        self.option_positions = {}
        self.hasCanceledStopLimit = 0
        empty_dic = {}
        
        try:
            pending = pickle.load(open("Pending_Option_Orders.pkl", 'rb'))
        except (OSError, IOError) as e:
            temp_pending = open("Pending_Option_Orders.pkl", 'wb')
            pickle.dump(empty_dic, temp_pending)
            temp_pending.close()
        # creating option sell pickle file
        try:
            stock_orders = pickle.load(open("Sell_Option_Positions.pkl",'rb'))
            print(stock_orders)
        except (OSError, IOError) as e:
            temp_outfile = open("Sell_Option_Positions.pkl","wb")
            pickle.dump(empty_dic, temp_outfile)
            temp_outfile.close()
    
    def getOptionPositions(self):
        positions = {}
        i=0
        for option in self.option_positions:
            info = self.getOptionInfo(option)
            instr = self.getInstrData(option)
            pct_change = self.optionPercentChange(option, info)
            positions[i] = {"Ticker":option['chain_symbol'],"Strike Price":float(instr['strike_price']), "Type":option['type']+" "+instr['type'],"Expiration Date":instr['expiration_date'],"Quantity":float(option['quantity']),"Market Price":float(info['adjusted_mark_price']),"Profit":self.getOptionProfit(option,info),"Percent Change":pct_change, "id":option['option_id']}
            i+=1
        pos_to_pd = pd.DataFrame.from_dict(positions, orient='index', columns=["Ticker","Strike Price","Type","Expiration Date","Quantity","Market Price", "Profit","Percent Change","id"])
        return pos_to_pd
    def getOptionProfit(self, option, info):
        if(option['type']=="short"):
            return (abs(float(option['average_price']))-float(info['adjusted_mark_price'])*float(option['trade_value_multiplier']))*float(option['quantity'])
        else:
            return (float(info['adjusted_mark_price'])*float(option['trade_value_multiplier'])-float(option['average_price']))*float(option['quantity'])
    def optionPercentChange(self, option, info):
        if(option['type']=="short"):
            return round((float(info['adjusted_mark_price'])*float(option['trade_value_multiplier'])/float(option['average_price'])+1.0)*100.0,2)
        else:
            return round((float(info['adjusted_mark_price'])*float(option['trade_value_multiplier'])/float(option['average_price'])-1.0)*100.0,2)
        
    def getOptionInfo(self, option):
        # inst = option['option']
        # inst=inst[:len(inst)-1]
        # inst = inst[str.rfind(inst, '/'):]
        inst = option['option_id']
        return r.options.get_option_market_data_by_id(inst)
    def getInstrData(self, option):
        # inst = option['option']
        # inst = inst[:len(inst)-1]
        # inst = inst[str.rfind(inst, '/'):]
        # inst = inst[1:]
        inst = option['option_id']
        return r.options.get_option_instrument_data_by_id(inst)
    def getOptionPosition(self, id):
        for option in self.option_positions:
            if(option['option_id']==id):
                return option
        return False
    def tempSell(self, ticker, quantity, stop_loss, take_profit, id):
        currOption = self.getOptionPosition(id)
        instr_data = self.getInstrData(currOption)
        info = self.getOptionInfo(currOption)
        
        if(currOption['type']=="short"):
            stopPrice = round(float(currOption['average_price'])*(-1-stop_loss/100.0),2)
            print("CREDIT OPTION FOR {} AT CURRENT PRICE {} FROM BUYING PRICE OF {}".format(ticker, float(info['adjusted_mark_price'])*float(currOption['trade_value_multiplier']), currOption['average_price']))
            print("Stop loss of {} and take profit {}".format(stopPrice, round(float(currOption['average_price'])*(-1+take_profit/100.0),1)))
        else:
            stopPrice = round(float(currOption['average_price'])*(1-stop_loss/100.0),2)
            print("DEBIT OPTION")
            print("Stop loss of {} and take profit {}".format(stopPrice, round(float(currOption['average_price'])*(1+take_profit/100.0),1)))
        

        

    def sellOptionPosition(self, ticker, quantity, stop_loss, take_profit, id):
        # print("Stop %:{}".format(stop_loss))
        print("CANCELING ALL PREVIOUS {} ORDERS".format(ticker))
        self.cancelAllOptionOrders(id)
        currOption = self.getOptionPosition(id)
        instr_data = self.getInstrData(currOption)
        stopPrice = -1
        takeProfit=-1
        # TODO add support for short calls etc.
        out_order = {}
        order = {}
        fullType = currOption["type"]
        if(currOption['type']=="short"):
            print("SHORT SELL ORDER")
            stopPrice = round(float(currOption['average_price'])*(-1-stop_loss/100.0)/float(currOption['trade_value_multiplier']),2)
            takeProfit = round(float(currOption['average_price'])*(-1+take_profit/100.0)/float(currOption['trade_value_multiplier']),2)
            # print("Take Profit: {}".format(takeProfit))
            # out_order = r.orders.order_sell_option_stop_limit('close', 'debit', stopPrice, stopPrice, ticker, quantity, instr_data['expiration_date'], instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')
            out_order = r.orders.order_buy_option_stop_limit('close', 'debit', stopPrice, stopPrice, ticker, quantity, expirationDate=instr_data['expiration_date'], strike=instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')

        else:
            print("LONG SELL ORDER")
            takeProfit = round(float(currOption['average_price'])*(1+take_profit/100.e0)/float(currOption['trade_value_multiplier']),2)
            stopPrice = round(float(currOption['average_price'])*(1-stop_loss/100.0),2)
            print(stopPrice)
            out_order = r.orders.order_sell_option_stop_limit('close', 'credit', stopPrice, stopPrice, ticker, quantity, instr_data['expiration_date'], instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')
        # out_order = {'id':'SAMPLE_SELL_ID'}
        print(out_order)
        while(out_order.get('id') == None):
            if(currOption['type']=="short"):
                stopPrice = round(float(currOption['average_price'])*(-1-stop_loss/100.0)/float(currOption['trade_value_multiplier']),2)
                # out_order = r.orders.order_sell_option_stop_limit('close', 'debit', stopPrice, stopPrice, ticker, quantity, instr_data['expiration_date'], instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')
                out_order = r.orders.order_buy_option_stop_limit('close', 'debit', stopPrice, stopPrice, ticker, quantity, expirationDate=instr_data['expiration_date'], strike=instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')

            else:
                stopPrice = round(float(currOption['average_price'])*(1-stop_loss/100.0),2)
                out_order = r.orders.order_sell_option_stop_limit('close', 'credit', stopPrice, stopPrice, ticker, quantity, instr_data['expiration_date'], instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')
            if(out_order.get('detail')=="This order introduces infinite risk."):
                print("ERROR: INFINITE RISK SELLING")
                self.output.emit("ERROR: INFINITE RISK SELLING")
                return
            elif(out_order.get('detail')=="This order is invalid because you do not have enough shares to close your position."):
                print("ERROR: NOT ENOUGH CONTRACTS AVAILABLE")
                self.output.emit("ERROR: NOT ENOUGH CONTRACTS AVAILABLE")
                return
        if(currOption['type']=="short"):
            #Switch take profit and stop loss for short positions
            order = {'ticker':ticker, 'bought_price':float(currOption['average_price']), 'take_profit':stopPrice, 'stop_loss':takeProfit, 'tp_percent':take_profit, 'sl_percent':stop_loss, 'quantity': quantity, 'expiration_date':instr_data['expiration_date'], 'strike_price':instr_data['strike_price'], 'type':instr_data['type'], 'full_type':fullType,'id':out_order['id'], 'option_id':id}
        else:
            order = {'ticker':ticker, 'bought_price':float(currOption['average_price']), 'take_profit':takeProfit, 'stop_loss':stopPrice, 'tp_percent':take_profit, 'sl_percent':stop_loss, 'quantity': quantity, 'expiration_date':instr_data['expiration_date'], 'strike_price':instr_data['strike_price'], 'type':instr_data['type'], 'full_type':fullType, 'id':out_order['id'], 'option_id':id}

        infile = open("Sell_Option_Positions.pkl", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        curr_orders[order['option_id']] = order
        outfile = open("Sell_Option_Positions.pkl",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Cancels all option orders for a given ticker
    def cancelAllOptionOrders(self, id):
        currOrders = self.getCurrOptionOrders()
        for order in currOrders:
            print(order)
            if(currOrders[order]['option_id']==id):
                print("calling cancel api for order "+currOrders[order]['id'])
                r.orders.cancel_option_order(currOrders[order]['id'])
        # currOrders = r.get_all_open_option_orders()
        # for order in currOrders:
        #     if(order['id']==id):
        
    #Check if option sell has been executed
    def checkOptionSold(self, orderId):
        pastOrders = r.get_all_option_orders('id')
        # pastOrders.append("SAMPLE_SELL_ID")
        # pastOrders.append("SAMPLE_SELL_ID")
        if(orderId in pastOrders):
            if(orderId !="SAMPLE_SELL_ID" and orderId != "SAMPLE_TAKE_PROFIT_ID"):
                orderInfo = r.get_option_order_info(orderId)
                if orderInfo['state'] == "filled":
                    return True
            else:
                return True
        return False
    def getOptionSoldInfo(self, orderId, ticker):
        info = {}
        if(orderId != "SAMPLE_TAKE_PROFIT_ID" and orderId != "SAMPLE_SELL_ID"):
            info = r.get_option_order_info(orderId)
        else:
            orders = self.getCurrOptionOrders()[ticker]
            if(orderId == "SAMPLE_SELL_ID"):
                info = {"processed_quantity":orders['quantity'], "premium":orders['stop_loss'], 'processed_premium':round(float(orders['quantity'])*float(orders['stop_loss']),2)}
            elif(orderId == "SAMPLE_TAKE_PROFIT_ID"):
                info = {"processed_quantity":orders['quantity'], "premium":orders['take_profit'], 'processed_premium':round(float(orders['quantity'])*float(orders['take_profit']),2)}
        return {'quantity':float(info['processed_quantity']), 'sell_price':float(info['premium']), 'profit':round(float(info['processed_premium'])-orders['bought_price']*orders['quantity'], 2)}
    #Deletes order from pickle file
    def deleteOptionOrder(self, ticker):
        infile = open("Sell_Option_Positions.pkl", 'rb')
        curr_orders = pickle.load(infile)
        curr_orders.pop(ticker)
        infile.close()
        outfile = open("Sell_Option_Positions.pkl",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Return current pending orders
    def getPendingOptionOrders(self):
        infile = open("Pending_Option_Orders.pkl", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        return curr_orders
    #gets ticker by option_id
    def getTickerByID(self, id):
        currOrders = self.getCurrOptionOrders()
        for order in currOrders:
            if(currOrders[order]['option_id']==id):
                return currOrders[order]['ticker']
        return "-1"
    def getCurrOptionOrders(self):
        infile = open("Sell_Option_Positions.pkl", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        return curr_orders
    def updateOptionPositions(self):
        self.option_positions = r.options.get_open_option_positions()
        # print(self.option_positions)
        # self.option_positions = r.options.get_aggregate_positions()
    def updateOptions(self):
        self.updateOptionPositions()
        orders = self.getCurrOptionOrders()
        for order in orders:
            # print("ORDER ID: {}".format(orders[order]['id']))
            # print("Current Price: {}, Take profit price: {}".format(float(self.getOptionInfo(self.getOptionPosition(order))['adjusted_mark_price']), orders[order]['take_profit']))
            # print("Curr price: {}, take profit: {}, stop loss: {}".format(float(self.getOptionInfo(self.getOptionPosition(orders[order]['option_id']))['adjusted_mark_price']), orders[order]['take_profit'], orders[order]['stop_loss']))
            # isShort = True if self.getOptionPosition(order['option_id'])['type']=="short" else False
            isShort = True if orders[order]['full_type']=="short" else False
            if(self.checkOptionSold(orders[order]['id'])):
                info = self.getOptionSoldInfo(orders[order]['id'], order)
                print("SOLD {} CONTRACTS OF {} POSITION FOR A PROFIT OF {}".format(info['quantity'], order, info['profit']))
                #Signal emits: quantity, ticker, option type, price of sold contract, profit, and profit %
                self.sold_option_signal.emit([info['quantity'], order, orders[order]['type'], info['sell_price'], info['profit'], round(100*info['profit']/(orders[order]['bought_price']*orders[order]['quantity']),2)])
                # self.sold_option_signal.emit(info['quantity'], order, info['profit']/)
                self.deleteOptionOrder(order)
            # elif  >= orders[order]['take_profit']:
            
            elif float(self.getOptionInfo(self.getOptionPosition(orders[order]['option_id']))['adjusted_mark_price']) >= orders[order]['take_profit'] and self.hasCanceledStopLimit == 0:
                
                if(isShort):
                    self.output.emit("Placing stop limit order for option as stop loss price has been reached")
                    print("Placing stop limit order for option as stop loss price has been reached")
                else:
                    self.output.emit("Placing sell order for option as take profit price has been reached")
                    print("Placing sell order for option as take profit price has been reached")
                print("Cancelling current option stop limit order")
                self.cancelAllOptionOrders(order)
                out_order={}
                if(isShort):
                    #purposefully wrong-looking index take_profit and stop_loss switched
                    out_order = r.orders.order_buy_option_stop_limit(positionEffect='close',creditOrDebit='debit',limitPrice=orders[order]['take_profit'], symbol=order, quantity=orders[order]['quantity'], expirationDate=orders[order]['expiration_date'], strike=orders[order]['strike_price'], optionType=orders[order]['type'], timeInForce='gtc')
                else:
                    out_order = r.orders.order_sell_option_limit(positionEffect='close',creditOrDebit='credit',price=self.getOptionInfo(self.getOptionPosition(orders[order]['id']))['adjusted_mark_price'], symbol=order, quantity=orders[order]['quantity'], expirationDate=orders[order]['expiration_date'], strike=orders[order]['strike_price'], optionType=orders[order]['type'], timeInForce='gtc')

                if(out_order.get("id") != None):
                    self.hasCanceledStopLimit = 1
                else:
                    continue
                print(out_order)
                # out_order = {'id':"SAMPLE_TAKE_PROFIT_ID"}
                #Changing the order id in pickle file
                infile = open("Sell_Option_Positions.pkl", 'rb')
                curr_orders = pickle.load(infile)
                infile.close()
                print(curr_orders[order])
                curr_orders[order]['id'] = out_order['id'] 
                outfile = open("Sell_Option_Positions.pkl",'wb')
                pickle.dump(curr_orders, outfile)
                outfile.close()
            #If I've placed sell take profit order, but price drops below again
            elif float(self.getOptionInfo(self.getOptionPosition(orders[order]['option_id']))['adjusted_mark_price']) < orders[order]['take_profit'] and self.hasCanceledStopLimit==1:
                print("Cancelling current option market order, price dipped again")
                self.cancelAllOptionOrders(order)
                # stopPrice = round(float(currOption['average_price'])*(1-stop_loss/100.0),2)
                # TODO add support for short calls etc.
                out_order = r.orders.order_sell_option_stop_limit('close', 'credit', orders[order]['stop_loss'], orders[order]['stop_loss'], order, orders[order]['quantity'], orders[order]['expiration_date'], orders[order]['strike_price'], optionType=orders[order]['type'], timeInForce='gtc')
                if(out_order.get("id") != None):
                    self.hasCanceledStopLimit=0
                else:
                    continue
                infile = open("Sell_Option_Positions.pkl", 'rb')
                curr_orders = pickle.load(infile)
                infile.close()
                print(curr_orders[order])
                curr_orders[order]['id'] = out_order['id'] 
                outfile = open("Sell_Option_Positions.pkl",'wb')
                pickle.dump(curr_orders, outfile)
                outfile.close()
            pendingOrders = self.getPendingOptionOrders()
            if(len(pendingOrders)>0):
                print("Trying pending order again...")
                for ticker in pendingOrders:
                    self.sellOptionPosition(pendingOrders[ticker][0],pendingOrders[ticker][1],pendingOrders[ticker][2],pendingOrders[ticker][3])
                    infile = open("Pending_Option_Orders.pkl", 'rb')
                    curr_orders = pickle.load(infile)
                    curr_orders.pop(ticker)
                    infile.close()
                    outfile = open("Pending_Option_Orders.pkl",'wb')
                    pickle.dump(curr_orders, outfile)
                    outfile.close()