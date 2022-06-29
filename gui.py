import socket
from turtle import pos
from kivyClient import *
from kivy.clock import Clock
from threading import Thread
from kivy.uix.colorpicker import *
from kivy.uix.popup import *
#Basic Imports 
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty

#Graphic interface imports 
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition

from kivy.graphics import Rectangle

#Server Communivation
import requests
#url = 'http://localhost/adveisor/data.php'
url = 'http://adveisor.de/data.php'


#Chess engine 
from stockfish import Stockfish
stockfish = Stockfish(path="stockfish_14.1_win_x64_avx2.exe", depth=12, parameters={"Threads": 2, "Minimum Thinking Time": 5})

#Basic Settings
Window.size = (320,480)
Window.borderless = False
#Window.maximize()


###### 					 ___  ___   ___  ___  					######
###### 					|_ _|| . | | . \| . | 					######
######			   		 | | | | | | | || | | 					######
######  				 |_| `___' |___/`___' 					######
#	- Add Boundary to piece draggable Position
#	- Add prevention of grid position outside boards and related crash issue
#	- Load/Output with Forsyth–Edwards Notation
#	- Implement restart game function Fix start game button will spawn new pieces above existing ones 
#	- Remake and restyle right side of GUI (Terminal and command) and Implement new functions
#	- Implement check mate check and response, including
#		> Pawn Promotion
#		> Castling 
#		> En Passant Capture
#	- Implement control / config screen
# 	- Implement more functionality 
# 	- Implement communication with server and data syncronization
#	- Implement music player and sound effects 
#	- Implement timed chess function
# 	- Implement command line input
#	- Implement bottom Status bar
#	- Make everything look better by Implementing better color scheme and better layout
#	- Create Public and Private class for better access
#Global Variable 
checker_size = [0.0,0.0]
board_size = [0.0,0.0]
bottom_margin = 0.0
GlobalLayout = None
autoPlay = False
machineMove = True
data = []
counter = 0
en_passant_square = ""
rgbw = [0,0,0,0]
movementLock = True
player_color = "w"
boardFront = "w"
#Position Conversion
def load_FEN_notation(position):
	cmd = [['',''],['',''],['',''],['',''],['',''],['',''],['',''],['','']]
	fen = position.split(" ")
	pos = fen[0].split("/")
	for x in range(len(pos)):
		for y in range(len(pos[x])):
			if(pos[x][y].isnumeric() == True):
				for z in range(int(pos[x][y])):
					cmd[x][0] = cmd[x][0] + '0'
					cmd[x][1] = cmd[x][1] +'0'
			elif (pos[x][y].islower() == True):
				cmd[x][0] = cmd[x][0] + pos[x][y]
				cmd[x][1] = cmd[x][1] + 'w'
			else:
				cmd[x][0] = cmd[x][0] + pos[x][y].lower()
				cmd[x][1] = cmd[x][1] + 'b'
	GlobalLayout.ids.chess_board.turn = fen[1]
	print(fen[1])
	return cmd
def get_en_passant(position):
	fen = position.split(" ")
	return fen[3] 
def algebraic_to_move(chess_notation):
	movePos = [0,0]
	x = "abcdefgh"
	y = "12345678"
	for j in range(8):
		if x[j] == chess_notation[0]:
			movePos[0] = j
		if y[j] == chess_notation[1]:
			movePos[1] = j
	return movePos
def to_chess_notation(move_from, move_to):
	x = "abcdefgh"
	y = "12345678"
	return x[move_from[0]] + y[move_from[1]] + x[move_to[0]]+ y[move_to[1]]
def to_move_position(chess_notation):
	x = "abcdefgh"
	y = "12345678"
	movePos = [0,0,0,0]
	for i in range(2):
		for j in range(8):
			if x[j] == chess_notation[i*2]:
				movePos[i*2] = j
			if y[j] == chess_notation[i*2+1]:
				movePos[i*2+1] = j
	return movePos
def position_to_coordinate(pos): 
	if(boardFront == "b"):
		piece_coordinate = (checker_size[0] * (7 - pos[0]) , checker_size[1] * (7 - pos[1]) + bottom_margin )
	else:
		piece_coordinate = (checker_size[0] * pos[0] , checker_size[1] * pos[1] + bottom_margin )
	return piece_coordinate
def coordinate_to_position(coordinate): 
	if(boardFront == "b"):
		piece_position = (7 - (round(coordinate[0]/ checker_size[0])), 7 - (round((coordinate[1] - bottom_margin ) / checker_size[1])))
	else:
		piece_position = (round(coordinate[0]/ checker_size[0]), round((coordinate[1] - bottom_margin ) / checker_size[1]))
	return piece_position
#Sloppy resizing method, but hey it Works 
def grid_sizeing(self, x, y):
	global checker_size, bottom_margin, board_size
	board_size = (GlobalLayout.ids.chess_board.size[0] , GlobalLayout.ids.chess_board.size[1])
	checker_size = (board_size[0] / 8.1 , board_size[1] / 8.1)
	bottom_margin = board_size[1] * 0.1 + GlobalLayout.ids.terminal.size[1]
	if(boardFront == "b"):
		piece_position = (checker_size[0] * (7 - x) , checker_size[1] * (7 - y) + bottom_margin)
	else:
		piece_position = (checker_size[0] * x , checker_size[1] * y + bottom_margin)
	return piece_position

#Classes for enabling mulitple screens
class WindowManager(ScreenManager):
	pass
class ConfigLayout(Screen,Widget):
	def __init__(self, **kwargs):
		super(ConfigLayout, self).__init__(**kwargs)

	def colorSelection(self):
		global player_color
		if player_color == "w": 
			player_color = "b"
			self.ids.ColorSelection.text = "Player Side: Black" 
		else: 
			player_color = "w"
			self.ids.ColorSelection.text = "Player Side: White" 
	def playerMovementLock(self):
		global movementLock
		if movementLock == False: 
			movementLock = True
			self.ids.playerColorLock.text = "Player Color Lock: True" 
		else: 
			movementLock = False
			self.ids.playerColorLock.text = "Player Color Lock: False" 
	def boardFrontSide(self):
		global boardFront
		if boardFront == "w": 
			boardFront = "b"
			sock.send_data( "Front,"+ "b"+ "-")
			self.ids.boardFrontSide.text = "Board Front Color: Black" 
		else: 
			boardFront = "w"
			sock.send_data( "Front,"+ "w"+ "-")
			self.ids.boardFrontSide.text = "Board Front Color: White" 
	def toggleGamemode(self):
		global autoPlay
		if autoPlay == True: 
			autoPlay = False
			print("AI Enemy: off" )
			self.ids.AiToggle.text = "AI Enemy: off" 
		else: 
			autoPlay = True
			self.ids.AiToggle.text = "AI Enemy: on" 
	def toggleMovemode(self):
		global machineMove
		if machineMove == True: 
			machineMove = False
			print("AI Enemy: off" )
			self.ids.MoveToggle.text = "Machine Move: off" 
		else: 
			machineMove = True
			self.ids.MoveToggle.text = "Machine Move: on" 
	def updateRGBW(self, r,g,b,w):
		global sock
		sock.send_data( "RGBW," + str(r) + ","+ str(g) + ","+ str(b)+ ","+ str(w) + "-")
	

def loop():
	global data, GlobalLayout
	if (len(data) == 0):
		return
	for x in range(len(data)):
		cmd = data.pop(0).split(",")
		if(cmd[0] == "hehe"):
			print("starting game: ")
			GlobalLayout.start_game()
		if(cmd[0] == "hoho"):
			print("closing game: ")
			GlobalLayout.reset_board()
		if(cmd[0] == "move"):
			print(cmd[1])
			if stockfish.is_move_correct(cmd[1]) == True: 
				make_move(cmd[1])
			if autoPlay == True:
				bestMove = stockfish.get_best_move()
				print(bestMove)
				make_move(bestMove)
	counter == 0
def make_move(move):
	#pawn promotion
	#coordinate transformation
	move_pos = to_move_position(move)
	#pawn promotion
	for piece in GlobalLayout.ids.chess_board.children:
		if (piece.previous_position[0], piece.previous_position[1]) == (move_pos[0], move_pos[1]):
			if (piece.type == "p" and  (move_pos[3] == 7 or move_pos[3] == 0)):
				print("yes????")
				move = move + "q"
				print(move)
				print(stockfish.is_move_correct(move))
				if stockfish.is_move_correct(move) == True:
					stockfish.make_moves_from_current_position([move])
					for checkpiece in GlobalLayout.ids.chess_board.children:
						if (checkpiece.previous_position[0], checkpiece.previous_position[1]) == (move_pos[0], move_pos[1]):
							GlobalLayout.ids.chess_board.remove_widget(checkpiece)
							if move_pos[3] == 7:
								newPiece = queen("w")
							else:
								newPiece = queen("b")
							newPiece.pos = grid_sizeing(GlobalLayout, move_pos[2], move_pos[3])
							newPiece.previous_position = (move_pos[2], move_pos[3])
							GlobalLayout.ids.chess_board.add_widget(newPiece)
							GlobalLayout.ids.cmd_out.text = GlobalLayout.ids.cmd_out.text + "\n" + piece.side + ": " + move 
							GlobalLayout.ids.cmd_out.text = GlobalLayout.ids.cmd_out.text + "\n"+ "Pawn Promotion to Queen!"
								#change round
							if GlobalLayout.ids.chess_board.turn ==  'w':
								GlobalLayout.ids.chess_board.turn =  'b'
								print('Now Blacks Turn')
							else:
								#print('hmm_[B]:' + self.parent.turn)
								GlobalLayout.ids.chess_board.turn = 'w'
								print('Now White Turn') 
					return
	if stockfish.is_move_correct(move):
		
		#kivyLib communication
		en_passant_square =  get_en_passant(stockfish.get_fen_position())
		stockfish.make_moves_from_current_position([move])
		#Server communication
		#dataToSend = {'game_round': '1', 'game_type': 'chess', 'game_data': move, 'is_new_round': 0}
		#requests.post(url, data = dataToSend)
		print(move)
		#moving logic 
		
		for piece in GlobalLayout.ids.chess_board.children:
			if coordinate_to_position((piece.pos[0], piece.pos[1])) == (move_pos[0], move_pos[1]):
				piece.previous_position  = (move_pos[2],move_pos[3]) 
				GlobalLayout.ids.cmd_out.text = GlobalLayout.ids.cmd_out.text + "\n" + piece.side + ": " + move
				for checkpiece in GlobalLayout.ids.chess_board.children:
					if coordinate_to_position((checkpiece.pos[0], checkpiece.pos[1])) == (move_pos[2], move_pos[3]) and checkpiece.side !=  piece.side:
						GlobalLayout.ids.chess_board.remove_widget(checkpiece)
						sock.send_data( "remove," + str(move_pos[2]) + ","+ str(move_pos[3])+ "-" )
						break
				piece.pos = position_to_coordinate((move_pos[2], move_pos[3]))
				#check castling 
				#last minute spaghetti code 
				if(piece.type == "k"):
					flag = False
					rook_pos = [0,0]
					castling_code = 0
					if (move == "e1g1"):
						rook_pos = [[7,0],[5,0]]
						castling_code = 3
						flag = True
					elif (move == "e1c1"): 
						rook_pos = [[0,0], [3,0]]
						castling_code = 2
						flag = True
					elif (move == "e8g8"): 
						rook_pos = [[7,7], [5,7]]
						castling_code = 1
						flag = True
					elif (move == "e8c8"): 
						rook_pos = [[0,7], [3,7]]
						castling_code = 0
						flag = True
					if (flag == True):
						for checkpiece in GlobalLayout.ids.chess_board.children:
							if (checkpiece.pos[0], checkpiece.pos[1]) == position_to_coordinate(rook_pos[0]) and checkpiece.type == "r":
								print("castling ")
								sock.send_data( "castel," + str(castling_code)+ "-" )
								checkpiece.pos = position_to_coordinate(rook_pos[1])
								checkpiece.previous_position = rook_pos[1]
								#change round
								if GlobalLayout.ids.chess_board.turn ==  'w':
									GlobalLayout.ids.chess_board.turn =  'b'
									print('Now Blacks Turn')
								else:
									GlobalLayout.ids.chess_board.turn = 'w'
									print('Now White Turn')
								return

				#check en passant
				if(piece.type == "p" and en_passant_square != "-"):
					en_passant_pos = algebraic_to_move(en_passant_square)
					if (move_pos[2], move_pos[3]) == en_passant_pos and checkpiece.type == "p":
						if (move_pos[3] == 6):
							en_passant_pos = [en_passant_pos[0], 4]
						else:
							en_passant_pos = [en_passant_pos[0], 3]
						for checkpiece in GlobalLayout.ids.chess_board.children:
							if (checkpiece.pos[0], checkpiece.pos[1]) == en_passant_pos and checkpiece.type == "p" and checkpiece.side != piece.side:
								sock.send_data( "remove," + str(en_passant_pos[0]) + ","+ str(en_passant_pos[1]) + "-")
								GlobalLayout.ids.chess_board.remove_widget(checkpiece)
				sock.send_data( "move," +str(move_pos[0]) + "," +str(move_pos[1]) + "," + str(move_pos[2]) + ","+ str(move_pos[3])+ "-" )
				if GlobalLayout.ids.chess_board.turn ==  'w':
					GlobalLayout.ids.chess_board.turn =  'b'
					print('Now Blacks Turn')
				else:
					GlobalLayout.ids.chess_board.turn = 'w'
					print('Now White Turn')
				break
	else:
		print("false move!")

#Main GUI Menu
class GUILayout(Screen,Widget):
	def __init__(self, **kwargs):
		super(GUILayout, self).__init__(**kwargs)
		global sock
		sock = MySocket()
		t = Thread(target=self.getData)
		t.daemon = True		
		t.start()
		

	def getData(self):
		while True:
			global data
			data.append(sock.get_data().decode("ascii"))
			#print("got data" + data)

	#Widget layer conversion. Kivy quirky magic: set parameter? No! DELETE the widget and make a NEW one!?! :D 
	#How I wish the documentation is better then bunch of Stackoverflow posts....
	def bring_to_front(self, widget):
		for child in self.ids.chess_board.children:
			if child == widget:
				self.ids.chess_board.remove_widget(widget)
				self.ids.chess_board.add_widget(widget)
	def send_to_back(self, widget):
		for child in self.ids.chess_board.children:
			if child == widget:
				self.ids.chess_board.remove_widget(widget)
				self.ids.chess_board.add_widget(widget, -1)
	#create chess pieces on the boards 

	def start_game(self):
		#flush old game data 
		GlobalLayout.reset_board()
		dataToSend = {'connection': 'set','game_data': "new", 'game_id': 1}
		requests.post(url, data = dataToSend)
		#load chess board 
		stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		cmd = load_FEN_notation("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		for j in range(8):
			for k in range(8):
				newPiece = None
				if cmd[j][0][k] == 'r':
					newPiece = rook(cmd[j][1][k])
				elif cmd[j][0][k] == 'n':
					newPiece = knight(cmd[j][1][k])
				elif cmd[j][0][k] == 'b':
					newPiece = bishop(cmd[j][1][k])
				elif cmd[j][0][k] == 'q':
					newPiece = queen(cmd[j][1][k])
				elif cmd[j][0][k] == 'k':
					newPiece = king(cmd[j][1][k])
				elif cmd[j][0][k] == 'p':
					newPiece = pawn(cmd[j][1][k])
				else:
					continue
				newPiece.numid = j*10 + k
				newPiece.pos = grid_sizeing(self,k, j)
				newPiece.previous_position = (k, j)
				self.ids.chess_board.add_widget(newPiece)
				
	
	#Reset Chess Board
	def reset_board(self):
		pieces = [i for i in GlobalLayout.ids.chess_board.children]
		for piece in pieces:
			GlobalLayout.ids.chess_board.remove_widget(piece)

				
#main chess piece class
class Piece(DragBehavior, Label, Widget):
	def __init__(self, **args):
		super(Piece, self).__init__(**args)
		self.numid = 0
		self.size_hint = (0.125, 0.125)
		self.is_active = True
		self.previous_position = (0, 0)
		with self.canvas:
			self.rect = Rectangle(pos=self.pos, size=self.size)
		self.bind(pos=self.update_rect)
		self.bind(size=self.update_rect)
		#print('piece now at ' + str(self.pos))
	#Canvas related positioning 
	def update_rect(self, *args):
		self.rect.pos = self.pos
		self.rect.size = self.size

	def on_touch_down(self, touch):
		#prevent movement of chess pieces when not their turn
		if movementLock == True and player_color != self.parent.turn  :
			return False
		elif self.parent.turn != self.side and self.collide_point(*touch.pos):
			return False
		if self.collide_point(*touch.pos):
			#dirty quirky solution due to lazyness and lack of kivy documentation
			#must be a better way but i dont know python :D 
			#bring chess piece to the front of UI
			GlobalLayout.bring_to_front(self)
			#print(self.previous_position)
			#print(self.numid)
			#print("Working!")
		return super(Piece, self).on_touch_down(touch)


	def on_touch_up(self, touch):
		global checker_size, bottom_margin, en_passant_square
		if self.collide_point(*touch.pos):
			GlobalLayout.send_to_back(self)

			#snap to fit
			snap_pos = (round(self.pos[0]/ checker_size[0]) * checker_size[0],round((self.pos[1] - bottom_margin ) / checker_size[1])  * checker_size[1] + bottom_margin )
			#print("snap Pos:" + str(coordinate_to_position(snap_pos)))
			#get current move from chess piece, and chuck it into stockfish to do the move logic wizardy y
			move = to_chess_notation(self.previous_position, coordinate_to_position(snap_pos))
			move_pos = to_move_position(move)

			#pawn promotion
			for piece in GlobalLayout.ids.chess_board.children:
				if (piece.previous_position[0], piece.previous_position[1]) == (move_pos[0], move_pos[1]):
					if (piece.type == "p" and  (move_pos[3] == 7 or move_pos[3] == 0)):
						print("yes????")
						move = move + "q"
						print(move)
						print(stockfish.is_move_correct(move))
						if stockfish.is_move_correct(move) == True:
							stockfish.make_moves_from_current_position([move])
							for checkpiece in self.parent.children:
								if (checkpiece.previous_position[0], checkpiece.previous_position[1]) == (move_pos[0], move_pos[1]):
									self.parent.remove_widget(checkpiece)
									if move_pos[3] == 7:
										newPiece = queen("w")
									else:
										newPiece = queen("b")
									newPiece.pos = grid_sizeing(self, move_pos[2], move_pos[3])
									newPiece.previous_position = (move_pos[2], move_pos[3])
									GlobalLayout.ids.chess_board.add_widget(newPiece)
									GlobalLayout.ids.cmd_out.text = GlobalLayout.ids.cmd_out.text + "\n" + self.side + ": " + move 
									GlobalLayout.ids.cmd_out.text = GlobalLayout.ids.cmd_out.text + "\n"+ "Pawn Promotion to Queen!"
										#change round
									if GlobalLayout.ids.chess_board.turn ==  'w':
										GlobalLayout.ids.chess_board.turn =  'b'
										print('Now Blacks Turn')
									else:
										#print('hmm_[B]:' + self.parent.turn)
										GlobalLayout.ids.chess_board.turn = 'w'
										print('Now White Turn') 
							return
					
			if stockfish.is_move_correct(move):
				en_passant_square =  get_en_passant(stockfish.get_fen_position())
				stockfish.make_moves_from_current_position([move])
				#Send Data to Server
				dataToSend = {'game_round': '1', 'game_type': 'chess', 'game_data': move, 'is_new_round': 0}
				requests.post(url, data = dataToSend)

				#print(stockfish.get_board_visual())
				self.pos = snap_pos
				self.previous_position  = coordinate_to_position(snap_pos)

				#check castling 
				#last minute spaghetti code 
				if(self.type == "k"):
					flag = False
					rook_pos = [0,0]
					castling_code = 0
					if (move == "e1g1"):
						rook_pos = [[7,0],[5,0]]
						castling_code = 3
						flag = True
					elif (move == "e1c1"): 
						rook_pos = [[0,0], [3,0]]
						castling_code = 2
						flag = True
					elif (move == "e8g8"): 
						rook_pos = [[7,7], [5,7]]
						castling_code = 1
						flag = True
					elif (move == "e8c8"): 
						rook_pos = [[0,7], [3,7]]
						castling_code = 0
						flag = True
					if (flag == True):
						for checkpiece in self.parent.children:
							if (checkpiece.pos[0], checkpiece.pos[1]) == position_to_coordinate(rook_pos[0]) and checkpiece.type == "r":
								print("castling ")
								if(machineMove == True):
									sock.send_data( "castel," + str(castling_code) + "-")
								checkpiece.pos = position_to_coordinate(rook_pos[1])
								checkpiece.previous_position = rook_pos[1]
								#change round
								if self.parent.turn ==  'w':
									self.parent.turn =  'b'
									print('Now Blacks Turn')
								else:
									#print('hmm_[B]:' + self.parent.turn)
									self.parent.turn = 'w'
									print('Now White Turn')
								return
				#check en passant
				if(self.type == "p" and en_passant_square != "-"):
					en_passant_pos = algebraic_to_move(en_passant_square)
					print("en passant check " + str(en_passant_pos))
					if [move_pos[2], move_pos[3]] == en_passant_pos:
						
						if (en_passant_pos[1] == 5):
							en_passant_pos = [en_passant_pos[0], 4]
						else:
							en_passant_pos = [en_passant_pos[0], 3]
						print("en passant capture " + str(en_passant_pos))
						for checkpiece in self.parent.children:
							if (checkpiece.pos[0], checkpiece.pos[1]) == position_to_coordinate(en_passant_pos) and checkpiece.type == "p":
								print("en passant remove ")
								if(machineMove == True):
									sock.send_data( "remove," + str(en_passant_pos[0]) + ","+ str(en_passant_pos[1]) + "-")
								self.parent.remove_widget(checkpiece)
				#remove captured piece if there is any
				for piece in self.parent.children:
					if (piece.pos[0], piece.pos[1]) == snap_pos and piece.side != self.side:
						#print('removing captured piece at ' + str(snap_pos))
						if(machineMove == True):
							sock.send_data( "remove," + str(move_pos[2]) + ","+ str(move_pos[3])+ "," )
						self.parent.remove_widget(piece)
				if(machineMove == True):
					sock.send_data( "move," +str(move_pos[0]) + "," +str(move_pos[1]) + "," + str(move_pos[2]) + ","+ str(move_pos[3]) + "-" )
				#change round
				if self.parent.turn ==  'w':
					self.parent.turn =  'b'
					print('Now Blacks Turn')
				else:
					#print('hmm_[B]:' + self.parent.turn)
					self.parent.turn = 'w'
					print('Now White Turn')

				#Send Data to Server
				#dataToSend = {'game_round': '1', 'game_type': 'chess', 'game_data': move, 'is_new_round': 0}
				#requests.post(url, data = dataToSend)

				#Show move in terminal
				GlobalLayout.ids.cmd_out.text = GlobalLayout.ids.cmd_out.text + "\n" + self.side + ": " + move 
				###print(stockfish.get_board_visual())
				
				if autoPlay == True:
					bestMove = stockfish.get_best_move()
					make_move(bestMove)
			else:
				print("nope")
				self.pos = position_to_coordinate(self.previous_position)
		return super(Piece, self).on_touch_up(touch)
		
#Define different Chess Pieces 
class pawn(Piece):
	def __init__(self, side):
		super(pawn, self).__init__()
		self.side = side
		self.type = "p"
		self.rect.source = './img/' + side +  'P' + '.png'
class rook(Piece):
	def __init__(self, side):
		super(rook, self).__init__()
		self.side = side
		self.type = "r"
		self.rect.source = './img/' + side +  'R' + '.png'		
class knight(Piece):
	def __init__(self, side):
		super(knight, self).__init__()
		self.side = side
		self.type = "n"
		self.rect.source = './img/' + side +  'N' + '.png'
class bishop(Piece):
	def __init__(self, side):
		super(bishop, self).__init__()
		self.side = side
		self.type = "b"
		self.rect.source = './img/' + side +  'B' + '.png'
class king(Piece):
	def __init__(self, side):
		super(king, self).__init__()
		self.side = side
		self.type = "k"
		self.rect.source = './img/' + side +  'K' + '.png'
class queen(Piece):
	def __init__(self, side):
		super(queen, self).__init__()
		self.side = side
		self.type = "q"
		self.rect.source = './img/' + side +  'Q' + '.png'

#load .kv style sheet
Builder.load_file('gui.kv')
class MyApp(App): 
	def build(self):
		global GlobalLayout, Configlayout
		GlobalLayout =  GUILayout()
		Configlayout = ConfigLayout()
		ScrManager = ScreenManager(transition=WipeTransition())
		ScrManager.add_widget(GlobalLayout)
		ScrManager.add_widget(Configlayout)
		return ScrManager

if __name__ == '__main__':
	Clock.schedule_interval(lambda dt: loop(), 0.1)
	MyApp().run()
	