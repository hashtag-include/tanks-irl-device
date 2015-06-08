#!/usr/bin/python
from socketIO_client import SocketIO, BaseNamespace
import serial
import time

serialPort = '/dev/ttyUSB0'
# serialPort = 'COM5'
playerNumber = 1

serialPort = serialPort
ser = serial.Serial(port=serialPort, baudrate=115200) # open serial connection

ser.write([128]) # start
time.sleep(.1) # per create 2 spec, wait until roomba can switch mode
ser.write([132]) # enter safe mode
time.sleep(.1) # per create 2 spec, wait until roomba can switch mode

ser.write('\xA4' + ' P%s ' % playerNumber) # write the player string to the LCD
ser.write('\x8B\x04\x00\xFF') # change the home LED color to green
time.sleep(1)

# move commands
UP = '\x89\x00\xC8\x80\x00'
DOWN = '\x89\xFF\x38\x80\x00'
LEFT = '\x89\x00\xC8\x00\x01'
RIGHT = '\x89\x00\xC8\xFF\xFF'


# Standard events
class Namespace(BaseNamespace):
    def on_connect(self):
        print('[Connection Established]')

# Custom events
def on_move(self, *args):
    print(self)
    if self == 'UP':
        ser.write(UP)
    elif self == 'DOWN':
        ser.write(DOWN)
    elif self == 'LEFT':
        ser.write(LEFT)
    elif self == 'RIGHT':
        ser.write(RIGHT)
    else:
        print 'wtf'
        return
    time.sleep(.2)
    ser.write('\x89\x00\x00\x80\x00')

def on_exit(self, *args):
    ser.write([173])
    ser.close() # close the serial connection

# socketIO = SocketIO('http://localhost', 1337, Namespace)
socketIO = SocketIO('https://tanks-irl.azurewebsites.net', verify=False)
socketIO.on('MOVE', on_move)
socketIO.on('EXIT', on_exit)
socketIO.wait()
