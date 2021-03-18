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


def dummy_callback(data):
    pass


# Create a Telemetrix instance.
board = telemetrix_rpi_pico.TelemetrixRpiPico()

# set some pins to different modes
board.set_pin_mode_digital_output(4)
board.set_pin_mode_digital_input(6, callback=dummy_callback)
board.set_pin_mode_analog_input(1, callback=dummy_callback)
board.set_pin_mode_digital_input_pullup(9, callback=dummy_callback)
board.set_pin_mode_neopixel(14)
board.set_pin_mode_i2c(0, 4, 5)

print(board.get_pico_pins())

board.shutdown()
