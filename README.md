# Adveisor Software
Software to be run on the raspberry Pi or any end terminal to control the to - be - built remote controlled board game 
## Dependencies
Require Python, Kivy (UI Library), Stockfish (Chess engine) and its API for Python
## Current Feature
- A working chess display with drag and drop piece movement
- Start a new game with human vs human

## Required steps 
### Getting started
* Install [Python](https://www.python.org/downloads/) 
* Install [Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html) and [Stockfish API for Python](https://pypi.org/project/stockfish/)  or use the uploaded kivy_venv virtual enviromnent folder if on Windows by navigating to the downloaded folder usind command line and execute 
	```
	kivy_venv\Scripts\activate
	```
	to activate the python virtual environment

* Download the code as ZIP file and extract it into a folder	or clone the repository
* Download [Stockfish](https://stockfishchess.org/download/) and replace the executable Stockfish programm with the downloaded programm if not on windows 
### Executing program
* run program by entering 
	```
	python gui.py
	```
## To Do List

 - Add Boundary to piece draggable Position

 - Add prevention of grid position outside boards and related crash issue

 - Load/Output with Forsyth–Edwards Notation

 - Implement restart game function, Fix start game button will spawn new pieces above existing ones

 - Remake and restyle right side of GUI (Terminal and command) and Implement new functions

 - Implement check mate check and response, including

	 >	 Pawn Promotion

	 > 	Castling

	 > 	En Passant Capture

 - Implement control / config screen

 - Implement more functionality

 - Implement communication with server and data syncronization

 - Implement music player and sound effects

 - Implement timed chess function

 - Implement command line input

 - Implement bottom Status bar

 - Make everything look better by Implementing better color scheme and better layout

 - Create Public and private class for Better access


## Version History


* 0.1 pre Alpha Prototype
    * Initial Upload

## Documentation and further readings 
See [Kivy examples](https://kivy.org/doc/stable/examples/gallery.html) and [Kivy Documentation](https://kivy.org/doc/stable/api-kivy.html)
