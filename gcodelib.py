import threading
import serial
import re
import time

class Connection:
    def __init__(self, port, debug=False):
        self._pos=(0,0,0)
        self._status = "Idle" # Status polled from "?" - we default for Idle for consistency
        self._debug = debug # In debug mode gcodelib will put output from grbl onto console
        self._serial = serial.Serial(
            write_timeout=0,
            port = port,
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1/12
        )
        time.sleep(2) # Serial initialization on Arduino takes a while
                      # we give some time for it to make sure it's connected
        print("Connection with Arduino initialized...")
    
    def poll_coords(self):
        self._send_instruction("?")
        reading = str(self._serial.read(1000).decode())
        # print(reading)
        explode = re.search(r"<(.*)\|MPos:([\d.]*),([\d.]*),([\d.]*)", reading, re.MULTILINE)
        if explode:            
            self._pos = (explode.group(2), explode.group(3), explode.group(4))
            self._status = explode.group(1)

    def print_coords(self):
        #print(self._pos)
        pass

    def wait_for_movement_stop(self):
        while self._status != "Idle":
            time.sleep(0.01)

    def spindle_to_low(self):
        self._serial.write(("$31 = 0\n").encode("ascii", "ignore"))

    def wait_for_movement_start(self):
        while self._status != "Run":
            time.sleep(0.01)

    def get_status(self):
        return self._status

    def send_coords(self, x, y):
        self._serial.write((self.get_move_gcode(x, y)+"\n").encode("ascii", "ignore"))
    
    def home(self):
        self._serial.write(("$31 = 0\n").encode("ascii", "ignore"))
        self._serial.write(("$H\n").encode("ascii", "ignore"))
    
    def magnet_control(self,boolean):
        if boolean:
            self._serial.write(("M3\n").encode("ascii", "ignore"))
        else:
            self._serial.write(("M5\n").encode("ascii", "ignore"))
    def reset(self):
        self._serial.write(("ctrl-x\n").encode("ascii", "ignore"))
    def _send_instruction(self, instr):
        self._serial.write((instr + "\n").encode("ascii", "ignore"))

    def get_move_gcode(self, x, y):
        return "G0 X" + str(x) + " Y" + str(y) + "F6000" 

    def console_read(self):
        def _console_read_routine():
            print("Listening from serial...")
            while (True):
                self.poll_coords()
                # reading = str(self._serial.read(1000).decode())
                # if reading:
                #     print(reading)

        thread = threading.Thread(target=_console_read_routine)
        thread.daemon = True
        thread.start()