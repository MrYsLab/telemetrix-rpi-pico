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


def neopixel_demo(my_board):
    """
    Run
    :param my_board: Pico board instance
    """

    # enable neopixel support on the Pico
    my_board.set_pin_mode_neopixel()

    # set some values and the show them
    my_board.neo_pixel_set_value(5, 255, 0, 0)
    my_board.neo_pixel_set_value(1, 0, 64, 0)
    my_board.neo_pixel_set_value(7, 0, 0, 64)
    my_board.neopixel_show()

    time.sleep(1)

    # clear the NeoPixels
    my_board.neopixel_clear()

    time.sleep(1)

    # fill the NeoPixels
    my_board.neopixel_fill(50, 0, 120)

    time.sleep(1)

    # set pixel value and update immediately
    my_board.neo_pixel_set_value(3, 0, 65, 64, True)
    time.sleep(1)

    my_board.neopixel_clear()
    # pixel sequence
    while True:
        for pixel in range(8):
            my_board.neo_pixel_set_value(pixel, 0, 0, 64, True)
            time.sleep(.1)
            my_board.neopixel_clear()


board = telemetrix_rpi_pico.TelemetrixRpiPico()
try:
    neopixel_demo(board)
    board.shutdown()

except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
