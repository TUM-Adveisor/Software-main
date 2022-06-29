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
softLimit = [400,415]
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
def primitivRemove(posx, posy):
    print(posx)
    print(posy)
    gridMove(posx,posy,False)
    offsetMove(posx, posy, 0, -25, True)
    offsetMove(7, posy, 50, -25, True)
    offsetMove(7, 0, 50, -50, True)

def primitivCastling (pos,side):
    coffset = 0
    if(side == "b"):
        coffset = 1
        if pos == 0: 
            pos = 3
        elif pos == 1:
            pos = 2
        elif pos == 2:
            pos = 1
        elif pos == 3:
            pos = 0
    offset = [[-25,5], [25,5], [-25,0], [25,0]]
    position = [[4 - coffset,7],[4 - coffset,7],[4 - coffset,0],[4 - coffset,0]]
    position1 = [[0,7],[7,7],[0,0],[7,0]]
    position2 = [[2 - coffset,7],[6- coffset,7],[2- coffset,0],[6- coffset,0]]
    position3 = [[3 - coffset,7],[5- coffset,7],[3- coffset,0],[5- coffset,0]]
    haltPos = [[2 - coffset,7],[5 - coffset,7],[2 - coffset,0],[5 - coffset,0]]
    haltPos1 = [[2 - coffset,6],[5 - coffset,6],[2 - coffset,1],[5 - coffset,1]]
    gridMove(position[pos][0],position[pos][1],False)
    offsetMove(haltPos[pos][0], haltPos[pos][1], offset[pos][0],offset[pos][1], True)
    offsetMove(haltPos1[pos][0], haltPos1[pos][1], offset[pos][0],offset[pos][1], True)

    gridMove(position1[pos][0],position1[pos][1],False)
    gridMove(position[pos][0],position[pos][1],True)

    offsetMove(haltPos1[pos][0], haltPos1[pos][1], offset[pos][0],offset[pos][1], False)
    offsetMove(haltPos[pos][0], haltPos[pos][1], offset[pos][0],offset[pos][1], True)
    gridMove(position2[pos][0],position2[pos][1],True)

    gridMove(position[pos][0],position[pos][1],False)
    gridMove(position3[pos][0],position3[pos][1],True)

def offsetMove(posx, posy, offsetx, offsety, magnet):
    #check for limitation
    if(posx < 0 or posx > 8 or posy < 0 or posy > 8 ):
        return
    else:
        xCoord = (boardXSize/8)*posx + offset[0] + offsetx
        yCoord = (boardYSize/8)*posy + offset[1] + offsety
        makeMove(xCoord, yCoord, magnet)
        time.sleep(0.4)
def makeMove(x, y, magnet):
    global lastMove
    if (magnet == True): 
        conn.magnet_control(True)
    #calculate dir vektor 
    vec = [ x -lastMove[0] , y - lastMove[1] ]
    #useless movement prevention
    if(vec == [0,0]):
        conn.magnet_control(False)
        return
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
        time.sleep(1/3)
    if (magnet == True): 
        conn.magnet_control(False)
    lastMove = [x, y]

#test code 
if __name__ == '__main__':
    init("COM5")
    time.sleep(3)
    primitivCastling(3)
    #gridMove(1, 1, True)
    #gridMove(1, 1, True)
    #primitivRemove(6,4)
    # for x in range(8):
    #     for y in range(8):
    #         gridMove(x, y, True)
    #         time.sleep(0.4)
    #         print(lastMove)

