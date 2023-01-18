#Currently just a script if you are unable to logout due to the program crashing. Last case scenario
#TODO Add window functionality
import keyring as k
from robin_stocks import robinhood as r
username = ""
try:
    username = k.get_password("MaxTradeBot", "BotUserName")
    k.delete_password("MaxTradeBot", "BotUserName")
except:
    print("Couldn't find username")
try:
    k.delete_password("MaxTrade", username)
except:
    print("Couldn't delete password")
try:
    r.authentication.logout()
except:
    print("Failed to log out of robinhood")