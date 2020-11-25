import robin_stocks as r
import pandas as pd
import pickle


from PySide2.QtCore import Signal, QObject

class OptionsBot(QObject):
    sold_option_signal = Signal(list,name="OptionSold")
    def __init__(self):
        super(OptionsBot, self).__init__()
        self.option_positions = {}
        empty_dic = {}
        temp_outfile = open("Sell_Option_Positions","wb")
        pickle.dump(empty_dic, temp_outfile)
        temp_outfile.close()
    def getOptionPositions(self):
        positions = {}
        for option in self.option_positions:
            info = self.getOptionInfo(option)
            instr = self.getInstrData(option)
            positions[option['chain_symbol']] = {"Strike Price":float(instr['strike_price']), "Type":option['type']+" "+instr['type'],"Expiration Date":instr['expiration_date'],"Quantity":float(option['quantity']),"Market Price":float(info['mark_price']),"Percent Change":self.optionPercentChange(option, info)}
        pos_to_pd = pd.DataFrame.from_dict(positions, orient='index', columns=["Strike Price","Type","Expiration Date","Quantity","Market Price", "Percent Change"])
        return pos_to_pd
    def optionPercentChange(self, option, info):
        return round((float(info['mark_price'])*float(option['trade_value_multiplier'])/float(option['average_price'])-1.0)*100.0,2)
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
    def getOptionPosition(self, ticker):
        for option in self.option_positions:
            if(option['chain_symbol']==ticker):
                return option
        return False
    def sellOptionPosition(self, ticker, quantity, stop_loss, take_profit):
        # print("Stop %:{}".format(stop_loss))
        currOption = self.getOptionPosition(ticker)
        instr_data = self.getInstrData(currOption)
        stopPrice = round(float(currOption['average_price'])*(1-stop_loss/100.0),2)
        # TODO add support for short calls etc.
        # out_order = r.orders.order_sell_option_stop_limit('close', 'credit', stopPrice, stopPrice, ticker, quantity, instr_data['expiration_date'], instr_data['strike_price'], optionType=instr_data['type'], timeInForce='gtc')
        out_order = {'id':'SAMPLE_SELL_ID'}
        order = {'bought_price':float(currOption['average_price']), 'take_profit':round(float(currOption['average_price'])*(1+take_profit/100.0),1), 'stop_loss':stopPrice, 'quantity': quantity, 'expiration_date':instr_data['expiration_date'], 'strike_price':instr_data['strike_price'], 'type':instr_data['type'], 'id':out_order['id']}
        infile = open("Sell_Option_Positions", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        curr_orders[ticker] = order
        outfile = open("Sell_Option_Positions",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    #Cancels all option orders for a given ticker
    def cancelAllOptionOrders(self, ticker):
        currOrders = r.get_all_open_option_orders()
        for order in currOrders:
            if(order['chain_symbol']==ticker):
                r.orders.cancel_option_order(order['id'])
    #Check if option sell has been executed
    def checkOptionSold(self, orderId):
        pastOrders = r.get_all_option_orders('id')
        # pastOrders.append("SAMPLE_SELL_ID")
        pastOrders.append("SAMPLE_TAKE_PROFIT_ID")
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
        infile = open("Sell_Option_Positions", 'rb')
        curr_orders = pickle.load(infile)
        curr_orders.pop(ticker)
        infile.close()
        outfile = open("Sell_Option_Positions",'wb')
        pickle.dump(curr_orders, outfile)
        outfile.close()
    def getCurrOptionOrders(self):
        infile = open("Sell_Option_Positions", 'rb')
        curr_orders = pickle.load(infile)
        infile.close()
        return curr_orders
    def updateOptionPositions(self):
        self.option_positions = r.options.get_open_option_positions()
    def updateOptions(self):
        self.updateOptionPositions()
        orders = self.getCurrOptionOrders()
        for order in orders:
            print("ORDER ID: {}".format(orders[order]['id']))
            if(self.checkOptionSold(orders[order]['id'])):
                info = self.getOptionSoldInfo(orders[order]['id'], order)
                print("SOLD {} CONTRACTS OF {} POSITION FOR A PROFIT OF {}".format(info['quantity'], order, info['profit']))
                #Signal emits: quantity, ticker, option type, price of sold contract, profit, and profit %
                self.sold_option_signal.emit([info['quantity'], order, orders[order]['type'], info['sell_price'], info['profit'], round(100*info['profit']/(orders[order]['bought_price']*orders[order]['quantity']),2)])
                # self.sold_option_signal.emit(info['quantity'], order, info['profit']/)
                self.deleteOptionOrder(order)
            # elif float(self.getOptionInfo(self.getOptionPosition(order))['adjusted_mark_price']) >= orders[order]['take_profit']:
            elif 170.0 >= orders[order]['take_profit']:
                print("Cancelling current option sell order")
                self.cancelAllOptionOrders(order)
                print("Placing sell order for option as take profit price has been reached")
                # out_order = r.orders.order_sell_option_limit(positionEffect='close',creditOrDebit='credit',price=self.getOptionPosition(order)['adjusted_mark_price'], symbol=order, quantity=orders[order]['quantity'], expirationDate=orders[order]['expiration_date'], strike=orders[order]['strike_price'], optionType=orders[order]['type'], timeInForce='gtc')
                out_order = {'id':"SAMPLE_TAKE_PROFIT_ID"}
                #Changing the order id in pickle file
                infile = open("Sell_Option_Positions", 'rb')
                curr_orders = pickle.load(infile)
                infile.close()
                curr_orders[order]['id'] = out_order['id'] 
                outfile = open("Sell_Option_Positions",'wb')
                pickle.dump(curr_orders, outfile)
                outfile.close()
