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
    launcherPort = None
    production = False
    syntax = 'client.py -r <roombaPort> -l <launcherPort> [-p]'

    try:
        opts, args = getopt.getopt(argv,"h:r:l:p",["roombaPort=", "launcherPort=", "production="])
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
        elif opt in ('-l', '--launcherPort'):
            launcherPort = arg
        elif opt in ('-p', '--production'):
            production = True
    return (roombaPort, launcherPort, production)

def id_generator(size = 4, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def update_id():
    global tankId
    tankId = id_generator()
    roomba.write(const.SEQ_LCD_PREFIX + tankId) # write the player string to the LCD
    roomba.write(const.SEQ_MAIN_LED_RED) # change the home LED color to red
    socket.emit('client-connect', {'id': tankId, 'type': 'tank'})

def move(command):
    print(command)
    if command == 'MOVE_UP':
        roomba.write(const.SEQ_MOVE_UP)
    elif command == 'MOVE_RIGHT':
        roomba.write(const.SEQ_MOVE_RIGHT)
    elif command == 'MOVE_DOWN':
        roomba.write(const.SEQ_MOVE_DOWN)
    elif command == 'MOVE_LEFT':
        roomba.write(const.SEQ_MOVE_LEFT)
    else:
        return
    time.sleep(.15)
    roomba.write(const.SEQ_MOVE_STOP)

# @TODO
def aim(command):
    print(command)
    if(command == const.COM_TILT_UP):
        launcher.write('u')
    elif(command == const.COM_TILT_DOWN):
        launcher.write('d')

# event when exit command is issued
def exit(command):
    print(command)
    roomba.write(const.SEQ_LCD_PREFIX + '    ') # clear the LCD screen
    roomba.write(const.SEQ_MAIN_LED_GREEN) # change the home LED color to green
    roomba.write(const.SEQ_STOP)
    time.sleep(1)
    roomba.close() # close the roomba connection
    launcher.close() # close the launcher connection
    sys.exit(1)

# @TODO
def fire(command):
    print(command)
    launcher.write('f')

# events in the CommandControl namespace
class CommandControl(BaseNamespace):
    def on_connect(self):
        print('[Connection Established]')
        global socket
        socket = self
        update_id()

# event when command is issued
def on_command(self, *args):
    try:
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
    except SerialException, e:
        print("should reconnect, due to %s" % e)
        reconnect_hack()

def on_client_disconnect(self, *args):
    if self['type'] == 'controller':
        if self['id'] == tankId:
            update_id()

def reconnect_hack():
    global launcher_port
    global launcher
    real_port = int(launcher_port[-1])
    time.sleep(1)
    
    isSet = False
    for port in range(real_port-2, real_port+2):
        try:
            test_port = launcher_port[:-1] + str(port)
            launcher = Serial(port = test_port, baudrate = const.LAUNCHER_BAUD_RATE, writeTimeout = None) # open serial connection to launcher
            launcher_port = test_port
            print("launcher now on %s" % launcher_port)
            isSet = True
        except (OSError, SerialException):
            pass
    if (not isSet):
        print("failed to reconnect launcher")
        sys.exit(-2)

    global roomba_port
    global roomba
    real_port = int(roomba_port[-1])
    time.sleep(1)
    
    isSet = False
    for port in range(real_port-2, real_port+2):
        try:
            test_port = roomba_port[:-1] + str(port)
            roomba = Serial(port = test_port, baudrate = const.ROOMBA_BAUD_RATE) # open serial connection to roomba
            roomba_port = test_port
            print("roomba now on %s" % roomba_port)
            isSet = True
        except (OSError, SerialException):
            pass
    if (not isSet):
        print("failed to reconnect roomba")
        sys.exit(-2)

def main(argv):
    (roombaPort, launcherPort, production) = parse_args(argv)

    global launcher_port
    launcher_port = launcherPort
    print("launcher on port %s" % launcher_port)
    global roomba_port
    roomba_port = roombaPort
    print("roomba on port %s" % roomba_port)

    global roomba # define roomba as unscoped global variable
    global launcher # define launcher as unscoped global variable
    try:
        roomba = Serial(port = roombaPort, baudrate = const.ROOMBA_BAUD_RATE) # open serial connection to roomba
    except SerialException:
        print('Serial connection to Roomba over %s could not be established' % roombaPort)
        sys.exit(-1)

    try:
        launcher = Serial(port = launcherPort, baudrate = const.LAUNCHER_BAUD_RATE, writeTimeout = None) # open serial connection to launcher
    except SerialException:
        print('Serial connection to launcher over %s could not be established' % launcherPort)
        sys.exit(-1)

    roomba.write(const.SEQ_START) # start
    time.sleep(1)
    roomba.write(const.SEQ_MODE_SAFE) # enter safe mode
    time.sleep(0.2)

    socketIO = SocketIO(const.PROD_SERVER_HOST, const.PROD_SERVER_PORT, CommandControl, verify = False) if production else SocketIO(const.DEV_SERVER_HOST, const.DEV_SERVER_PORT, CommandControl)
    
    socketIO.on('command', on_command)
    socketIO.on('client-disconnect', on_client_disconnect)
    socketIO.wait()

if __name__ == "__main__":
   main(sys.argv[1:])
