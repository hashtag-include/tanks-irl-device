#!/usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
from serial import Serial, SerialException
import const
import sys
import getopt
import time
import random
import string

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

def id_generator(size = 4, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def update_id():
    global tankId
    tankId = id_generator()
    socket.emit('client-connect', {'id': tankId, 'type': 'tank'})

def move(command):
    print(command)
    return
    if command == 'MOVE_UP':
        ser.write(const.SEQ_MOVE_UP)
    elif command == 'MOVE_RIGHT':
        ser.write(const.SEQ_MOVE_RIGHT)
    elif command == 'MOVE_DOWN':
        ser.write(const.SEQ_MOVE_DOWN)
    elif command == 'MOVE_LEFT':
        ser.write(const.SEQ_MOVE_LEFT)
    else:
        return
    time.sleep(.1)
    ser.write(const.SEQ_MOVE_STOP)

# @TODO
def aim(command):
    print(command)

# event when exit command is issued
def exit(command):
    print(command)
    ser.write(const.SEQ_STOP)
    time.sleep(1)
    ser.close() # close the serial connection
    sys.exit(1)

# @TODO
def fire(command):
    print(command)

# events in the CommandControl namespace
class CommandControl(BaseNamespace):
    def on_connect(self):
        print('[Connection Established]')
        global socket
        socket = self
        update_id()

# event when command is issued
def on_command(self, *args):
    # command issued to the correct player
    if(self['player']['id'] == tankId):
        if(self['command'] in (const.COM_MOVE_UP, const.COM_MOVE_RIGHT, const.COM_MOVE_DOWN, const.COM_MOVE_LEFT)):
            move(self['command'])
        elif(self['command'] in (const.COM_TILT_UP, const.COM_PAN_RIGHT, const.COM_TILT_DOWN, const.COM_PAN_LEFT)):
            aim(self['command'])
        elif(self['command'] == const.COM_EXIT):
            exit(self['command'])
        elif(self['command'] == const.COM_FIRE):
            fire(self['command'])

def on_client_disconnect(self, *args):
    if self['type'] == 'controller':
        if self['id'] == tankId:
            update_id()

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
    
    socketIO.on('command', on_command)
    socketIO.on('client-disconnect', on_client_disconnect)
    socketIO.wait()

if __name__ == "__main__":
   main(sys.argv[1:])