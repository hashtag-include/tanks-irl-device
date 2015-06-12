#!/usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
from serial import Serial, SerialException
import const
import sys
import getopt
import time

# parses the command line arguements into variables. example of valid roombaPorts: '/dev/ttyUSB0' and 'COM5'
def parse_args(argv):
    roombaPort = None
    production = False
    syntax = 'client.py -r <roombaPort> [-p]'

    try:
        opts, args = getopt.getopt(argv,"h:r:p",["roombaPort=", "production="])
    except getopt.GetoptError:
        print(syntax)
        sys.exit(-1)
    if len(opts) <= 0:
        print(syntax)
        sys.exit(-1)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(syntax)
            sys.exit(-1)
        elif opt in ('-r', '--roombaPort'):
            roombaPort = arg
        elif opt in ('-p', '--production'):
            production = True
    return (roombaPort, production)

# events in the CommandControl namespace
class CommandControl(BaseNamespace):
    def on_connect(self):
        print('[Connection Established]')

# event when move command is issued
def on_move(self, *args):
    print(self)
    if self == 'UP':
        ser.write(const.SEQ_MOVE_UP)
    elif self == 'DOWN':
        ser.write(const.SEQ_MOVE_DOWN)
    elif self == 'LEFT':
        ser.write(const.SEQ_MOVE_LEFT)
    elif self == 'RIGHT':
        ser.write(const.SEQ_MOVE_RIGHT)
    else:
        return
    time.sleep(.1)
    ser.write(const.SEQ_MOVE_STOP)

# event when exit command is issued
def on_exit(self, *args):
    ser.write(const.SEQ_STOP)
    time.sleep(1)
    ser.close() # close the serial connection
    sys.exit(1)

def main(argv):
    (roombaPort, production) = parse_args(argv)

    global ser # define ser is unscoped global variable
    try:
        ser = Serial(port = roombaPort, baudrate = const.ROOMBA_BAUD_RATE) # open serial connection
    except SerialException:
        print('Serial connection to Roomba over %s could not be established' % roombaPort)
        sys.exit(-1)

    ser.write(const.SEQ_START) # start
    time.sleep(1)
    ser.write(const.SEQ_MODE_SAFE) # enter safe mode
    time.sleep(0.2)

    ser.write(const.SEQ_PLAYER_NUMBER) # write the player string to the LCD
    ser.write(const.SEQ_MAIN_LED_GREEN) # change the home LED color to green
    time.sleep(0.2)

    socketIO = SocketIO(const.PROD_SERVER_HOST, const.PROD_SERVER_PORT, CommandControl, verify = False) if production else SocketIO(const.DEV_SERVER_HOST, const.DEV_SERVER_PORT, CommandControl)
    
    socketIO.on('MOVE', on_move)
    socketIO.on('EXIT', on_exit)
    socketIO.wait()

if __name__ == "__main__":
   main(sys.argv[1:])