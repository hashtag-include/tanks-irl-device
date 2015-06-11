#!/usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
import sys
import getopt
import serial
import time

# const variables
localServerUrl = 'http://localhost'
hostedServerUrl = 'https://tanks-irl.azurewebsites.net'
playerNumber = 1
playerDisplayName = '\xA4' + ' P%s ' % playerNumber
mainLEDGreen = '\x8B\x04\x00\xFF'

# move commands
UP = '\x89\x00\xC8\x80\x00'
DOWN = '\x89\xFF\x38\x80\x00'
LEFT = '\x89\x00\xC8\x00\x01'
RIGHT = '\x89\x00\xC8\xFF\xFF'
STOP = '\x89\x00\x00\x80\x00'

# parses the command line arguements into variables. example of valid roombaPorts: '/dev/ttyUSB0' and 'COM5'
def parseArgs(argv):
    roombaPort = None
    production = False
    clientRunSyntax = 'client.py -r <roombaPort> [-p]'

    try:
        opts, args = getopt.getopt(argv,"hr:s",["roombaPort=", "production="])
    except getopt.GetoptError:
        print(clientRunSyntax)
        sys.exit(-1)
    if len(opts) <= 0:
        print(clientRunSyntax)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(clientRunSyntax)
            sys.exit(2)
        elif opt in ("-r", "--roombaPort"):
            roombaPort = arg
        elif opt in ("-p", "--production"):
            production = True
        else:
            print('opt =', opt)
            print(clientRunSyntax)
            sys.exit(2)
    return (roombaPort, production)

# Standard events
class Namespace(BaseNamespace):
    def on_connect(self):
        print('[Connection Established]')

# Custom events
def onMove(self, *args):
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
        return
    time.sleep(.2)
    ser.write(STOP)

def onExit(self, *args):
    ser.write([173])
    ser.close() # close the serial connection
    sys.exit(1)

def main(argv):
    (roombaPort, production) = parseArgs(argv)
    ser = serial.Serial(port=roombaPort, baudrate=115200) # open serial connection

    ser.write([128]) # start
    time.sleep(.1) # per create 2 spec, wait until roomba can switch mode
    ser.write([132]) # enter safe mode
    time.sleep(.1) # per create 2 spec, wait until roomba can switch mode

    ser.write(playerDisplayName) # write the player string to the LCD
    ser.write(mainLEDGreen) # change the home LED color to green
    time.sleep(1)

    socketIO = SocketIO(hostedServerUrl, verify=False) if production else ocketIO(localServerUrl, 1337, Namespace)
    
    socketIO.on('MOVE', onMove)
    socketIO.on('EXIT', onExit)
    socketIO.wait()

if __name__ == "__main__":
   main(sys.argv[1:])