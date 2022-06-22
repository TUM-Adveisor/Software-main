# https://github.com/gavinlyonsrepo/RpiMotorLib/blob/master/Documentation/28BYJ.md

from operator import truediv
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

# GpioPins = [27, 22, 23, 24]

# Declare an named instance of class pass a name and motor type
mymotor = RpiMotorLib.BYJMotor("MyMotor", "28BYJ")

# call the function pass the parameters
# mymotor.motor_run(GPIOPins, wait, steps, counterclockwise, verbose, steptype, initdelay)
# full revolution is 512 steps

def CameraUp(GpioPins):
    mymotor.motor_run(GpioPins , .01, 512 / 4, True, False, "half", .05)
    

def CameraDown(GpioPins):
    mymotor.motor_run(GpioPins , .01, 512 / 4, False, False, "half", .05)

# good practise to cleanup GPIO at some point before exit
GPIO.cleanup()