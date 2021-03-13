"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import time
import sys
from telemetrix_rpi_pico import telemetrix_rpi_pico
from random import randint


def neopixel_demo2(my_board):
    """
    Run
    :param my_board: Pico board instance
    """

    # enable neopixel support on the Pico
    my_board.set_pin_mode_neopixel()
    t = 0.3
    for pixel in range(8):
        my_board.neo_pixel_set_value(pixel, 4, 0, 0, True)
        time.sleep(t)
        t = t - 0.03
    my_board.neopixel_clear()
    t = 0.3
    for pixel in range(8, 0, -1):
        my_board.neo_pixel_set_value(pixel, 0, 4, 0, True)
        time.sleep(t)
        t = t - 0.03
    time.sleep(.3)

    for i in range(5):
        my_board.neopixel_fill(0, 0, 4)
        time.sleep(.2)
        my_board.neopixel_clear()
        time.sleep(.2)

    for i in range(30):
        my_board.neo_pixel_set_value(randint(0, 7), randint(0, 4), randint(0, 8),
                                     randint(0, 8), True)
        time.sleep(.2)
        my_board.neo_pixel_set_value(randint(0, 7), 0, 0, 0, True)

    my_board.neopixel_clear()


board = telemetrix_rpi_pico.TelemetrixRpiPico()
try:
    neopixel_demo2(board)
    board.shutdown()

except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
