from math import sqrt
import gcodelib
import time
import threading
###################################################################
#                    HardwareLib Documentation 
# Features: Chess Grid movement, move with magnet drag compensation
# 
# Usage: 
#      init("[Serial Port]") --- Start connection with board 
#      gridMove([grid x coord (from 0 to 7)], [grid y coords (from 0 to 7)], [Magnet (True or False)] )
#      makeMove([Board Absolut x coord (from 0 to 400 in mm)], [Board Absolut y coord (from 0 to 410 in mm)], [Magnet (True or False)])
#
###################################################################
#Default Setting
boardXSize = 395
boardYSize = 395
softLimit = [400,410]
lastMove = [0,0]
offset = [10,70] 
chessGridSize = 50
chessCenterOffset = 25
magnetDragOffset = 5

#Startup Routing
def init(port):
    global conn
    conn=gcodelib.Connection(port)
    conn.console_read()
    conn.reset()
    time.sleep(0.4)
    conn.home()
    time.sleep(2)
def gridMove(posx, posy, magnet):
    #check for limitation
    if(posx < 0 or posx > 8 or posy < 0 or posy > 8 ):
        return
    else:
        xCoord = (boardXSize/8)*posx + offset[0] 
        yCoord = (boardYSize/8)*posy + offset[1]  
        makeMove(xCoord, yCoord, magnet)
        time.sleep(0.4)
def makeMove(x, y, magnet):
    global lastMove
    if (magnet == True): 
        conn.magnet_control(True)
    #calculate dir vektor 
    vec = [ x -lastMove[0] , y - lastMove[1] ]
    #useless movement prevention
    #if(vec[0] == 0 & vec[1] == 0):
     #   conn.magnet_control(False)
     #   return
    #Magnet drag prevention
    vec = [vec[0]/ sqrt(vec[0]*vec[0] + vec[1]*vec[1]),vec[1] /sqrt(vec[0]*vec[0] + vec[1]*vec[1])]
    vec = [vec[0]*3,vec[1]*3]
    vec = [vec[0] + x,vec[1] +y]
    print(vec)
    #Machine soft limit check 
    if(vec[0] > softLimit[0]):
        vec[0] = softLimit[0]
    if(vec[1] > softLimit[1]):
        vec[1] = softLimit[1]
    #Move logic 
    conn.send_coords(vec[0],vec[1])
    conn.wait_for_movement_start()
    while (conn._status != "Idle"):
        conn.print_coords()
        time.sleep(1/5)
    if (magnet == True): 
        conn.magnet_control(False)
    lastMove = [x, y]

#test code 
if __name__ == '__main__':
    init("COM4")
    for x in range(8):
        for y in range(8):
            gridMove(x, y, True)
            time.sleep(0.4)
            print(lastMove)

