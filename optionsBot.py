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
        inst = option['option']
        inst=inst[:len(inst)-1]
        inst = inst[str.rfind(inst, '/'):]
        return r.options.get_option_market_data_by_id(inst)
    def getInstrData(self, option):
        inst = option['option']
        inst = inst[:len(inst)-1]
        inst = inst[str.rfind(inst, '/'):]
        inst = inst[1:]
        return r.options.get_option_instrument_data_by_id(inst)
    def updateOptionPositions(self):
        self.option_positions = r.options.get_open_option_positions()
    def updateOptions(self):
        self.updateOptionPositions()