#Server Communivation
import requests

#data address
url = 'http://adveisor.de/data.php'
#url = 'http://localhost/adveisor/data.php'
###################################################################
#                    serverLib Documentation 
# Features: get last pushed data in form of array, set data
# 
# Usage: 
#      get_data() -> return array with array[0] := data string, array[1] := game id, array[2] := time uploaded  
#      set_data([game data (string up to 1024 byte)], [game id (int up to 32 byte)])
#
###################################################################

def get_data():
    dataToSend = {'connection': 'get'}
    x = requests.post(url, data = dataToSend)
    return x.text.split("!")
def set_data(game_data,game_id):
    dataToSend = {'connection': 'set','game_data': game_data, 'game_id': game_id}
    x = requests.post(url, data = dataToSend)
    if(x.text == "ok"):
        print("nice!")
        return True
    else:
        print(x.text)
        return False

###test code###
#get_data()
#set_data("g2g4","2")
