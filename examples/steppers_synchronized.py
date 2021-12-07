#!/usr/bin/python3  
#-*- coding: utf-8 -*-
"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,f
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 DHT support courtesy of Martyn Wheeler
 Based on the DHTNew library - https://github.com/RobTillaart/DHTNew
"""

import sys
import time

from telemetrix_rpi_pico import telemetrix_rpi_pico

"""
...

Recommended stepper homing procedure:

"""

# Create a Telemetrix instance.
board = telemetrix_rpi_pico.TelemetrixRpiPico(sleep_tune=.001) # the computer's response is up to 2-5x sleep_tune 

STEPPER_X = 0
STEPPER_Y = 1
board.stepper_new(STEPPER_X, dir_pin=10, step_pin=11, endswitch_pin=18, disable_pin=0, motor_inertia=32*4)
board.stepper_new(STEPPER_Y, dir_pin=12, step_pin=13, endswitch_pin=19, disable_pin=0, motor_inertia=32*4)

HOMING_DISTANCE = -25000 # slightly more than physical range of the motors



def triangular_path():
    yield(1000, 1000) # set motors to first corner...
    yield(1000, 9000) # in next callback, go to second corner...
    yield(3000, 9500) # etc.
    yield(1000, 1000) # ... and finish the triangle

path_generator = triangular_path()

def stepper_cb_synchronized(my_stepper_group, error, msg):
    if error: raise RuntimeError(msg)

    try:
        new_pos = path_generator.__next__()
        board.stepper_move(stepper_ids=my_stepper_group, 
                target_micropos=new_pos, 
                max_speeds=450, 
                callback=stepper_cb_synchronized,
                reset_nanopos=None) # None = resets once after homing
    except StopIteration:
        print(f'Stepper group {my_stepper_group} has just finished path')


board.stepper_move(
        stepper_ids=[STEPPER_X, STEPPER_Y], 
        target_micropos=[HOMING_DISTANCE, HOMING_DISTANCE], 
        max_speeds=50, 
        callback=stepper_cb_synchronized, 
        endstop_expected=1) # moving in sync
# program execution continues immediately, until the 2D path is finished

def the_callback(data): # independent printout of how stepper no. 1 moves
    print(data[3+4]*2**24+data[4+4]*2**16+data[5+4]*2**8+data[6+4]*2**0, 
            data[3]*2**24+data[4]*2**16+data[5]*2**8+data[6]) # time.time(), 

while any(board.stepper_action.values()): 
    board.get_stepper_status(1, callback=the_callback)
    time.sleep(.01) # avoid communicating faster than 300/s, stepper control would slow down 

print('All stepper moves finished, restarting the board and quitting')
board.shutdown(); time.sleep(.5) 
