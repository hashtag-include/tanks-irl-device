#!/usr/bin/python

### Constants

# socket server
DEV_SERVER_HOST = 'http://localhost'
DEV_SERVER_PORT = 1337
PROD_SERVER_HOST = 'https://tanks-irl.azurewebsites.net'
PROD_SERVER_PORT = 443

# baudrate constants
ROOMBA_BAUD_RATE = 115200
LAUNCHER_BAUD_RATE = 9600

# main roomba sequences
SEQ_START = [128]
SEQ_STOP = [173]
SEQ_MODE_SAFE = [132]

# misc roomba sequences
SEQ_LCD_PREFIX = '\xA4'
SEQ_MAIN_LED_GREEN = '\x8B\x04\x00\x80'
SEQ_MAIN_LED_RED = '\x8B\x04\xFF\x80'

# socket events
COM_MOVE_UP = 'MOVE_UP'
COM_MOVE_RIGHT = 'MOVE_RIGHT'
COM_MOVE_DOWN = 'MOVE_DOWN'
COM_MOVE_LEFT = 'MOVE_LEFT'
COM_TILT_UP = 'TILT_UP'
COM_PAN_RIGHT = 'PAN_RIGHT'
COM_TILT_DOWN = 'TILT_DOWN'
COM_PAN_LEFT = 'PAN_LEFT'
COM_EXIT = 'EXIT'
COM_FIRE = 'FIRE'

# roomba move sequences
SEQ_MOVE_UP = '\x89\x00\xFA\x80\x00' # move straight @ 250 mm/s
SEQ_MOVE_DOWN = '\x89\xFF\x06\x80\x00' # move straight @ -250 mm/s
SEQ_MOVE_LEFT = '\x89\x00\x64\x00\x01' # move left @ 100 mm/s
SEQ_MOVE_RIGHT = '\x89\x00\x64\xFF\xFF' # move right @ 100 mm/s
SEQ_MOVE_STOP = '\x89\x00\x00\x80\x00' # move straight @ 0 mm/s