import kivyLib
import hardware
import serverLib
import time
#from operator import truediv
#import RPi.GPIO as GPIO
#from RpiMotorLib import RpiMotorLib
#mymotor = RpiMotorLib.BYJMotor("MyMotor", "28BYJ")
enable = False
boardSide = "w"
boardDesignation = 1
lastmove = ""
#notation conversion
def to_chess_notation(move_from, move_to):
	x = "abcdefgh"
	y = "12345678"
	return x[move_from[0]] + y[move_from[1]] + x[move_to[0]]+ y[move_to[1]]

if __name__ == '__main__':
    #wait for kivy start
    if enable == True:
        hardware.init("COM6")
    #CameraUp(GpioPins)
    time.sleep(3)
    #start chessboard
    kivyLib.send_data("hehe")
    #get initial server data 
    serverData = serverLib.get_data()
    lastmove = serverData[0]
    while True:
        data = kivyLib.get_data().split("-")
        for x in data: 
            cmd = x.split(",")
            if(cmd[0] == "move" ):
                print(data)
                move = to_chess_notation([int(cmd[1]), int(cmd[2])],[int(cmd[3]), int(cmd[4])])
                serverLib.set_data(move,1)
                print("sent: " + move)
                lastmove = move
                if (boardSide == "b"):
                    cmd[1] = str(7 - int(cmd[1])) 
                    cmd[2] = str(7 - int(cmd[2])) 
                    cmd[3] = str(7 - int(cmd[3])) 
                    cmd[4] = str(7 - int(cmd[4])) 
               
                print("moving from " + cmd[1] + "," + cmd[2] + " to "  + cmd[3] + ","+ cmd[4])
                if enable == True:
                    hardware.gridMove(int(cmd[1]), int(cmd[2]), False)
                    hardware.gridMove(int(cmd[3]), int(cmd[4]), True)
                
            elif(cmd[0] == "remove" ):
                print(data)
                if (boardSide == "b"):
                    cmd[1] = str(7 - int(cmd[1])) 
                    cmd[2] = str(7 - int(cmd[2])) 
                print("removing " + cmd[1] + "," + cmd[2])
                if enable == True:
                    hardware.primitivRemove(int(cmd[1]) , int(cmd[2]))
            elif(cmd[0] == "castel" ):
                print(data)
                print("Castling " + cmd[1])
                if enable == True:
                    hardware.primitivCastling(int(cmd[1]), boardSide)
            elif(cmd[0] == "RGBW" ):
                print(data)
                print("RGBW")
            elif(cmd[0] == "Front" ):
                print(data)
                boardSide = cmd[1]
                print("boardside: " + boardSide)

        serverData = serverLib.get_data()
        #print("serverdata: " + serverData[0] + " last:" + lastmove)
        if(serverData[0] != lastmove):
            if(serverData[0] == "new"):
                kivyLib.send_data("hehe")
            else:
                kivyLib.send_data("move," + serverData[0])
            lastmove = serverData[0] 
        
        