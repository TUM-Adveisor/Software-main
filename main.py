import kivyLib
import hardware
import serverLib
import time
#from operator import truediv
#import RPi.GPIO as GPIO
#from RpiMotorLib import RpiMotorLib
#mymotor = RpiMotorLib.BYJMotor("MyMotor", "28BYJ")

boardDesignation = 1
lastmove = ""
#notation conversion
def to_chess_notation(move_from, move_to):
	x = "abcdefgh"
	y = "12345678"
	return x[move_from[0]] + y[move_from[1]] + x[move_to[0]]+ y[move_to[1]]

if __name__ == '__main__':
    #wait for kivy start
    #hardware.init("COM5")
    #CameraUp(GpioPins)
    time.sleep(4)
    #start chessboard
    kivyLib.send_data("hehe")
    #get initial server data 
    serverData = serverLib.get_data()
    lastmove = serverData[0]
    while True:
        
        cmd = kivyLib.processData()
        if(cmd[0] != "False"):
            if(cmd[0] == "move" ):
                print(cmd)
                #hardware.gridMove(int(cmd[1]), int(cmd[2]), False)
                #hardware.gridMove(int(cmd[3]), int(cmd[4]), True)
                print("moving from " + cmd[1] + "," + cmd[2] + " to "  + cmd[3] + ","+ cmd[4])
                move = to_chess_notation([int(cmd[1]), int(cmd[2])],[int(cmd[3]), int(cmd[4])])
                serverLib.set_data(move,1)
                lastmove = move
        serverData = serverLib.get_data()
        print("serverdata: " + serverData[0] + " last:" + lastmove)
        if(serverData[0] != lastmove):
            kivyLib.send_data("move," + serverData[0])
            lastmove = serverData[0] 
        
        