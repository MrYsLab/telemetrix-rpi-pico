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
"""

import sys
import time
from telemetrix_rpi_pico import telemetrix_rpi_pico


"""
This program monitors 2 DHT  devices
"""
DHT_PIN = 2
DHT_PIN2 = 15

# indices into callback data for valid data
REPORT_TYPE = 0
PIN = 1
HUMIDITY = 2
TEMPERATURE = 3
TIME = 4


# A callback function to display the distance
def the_callback(data):
    """
    The callback function to display the current humidity and temperature
    :param data: [report_type = PrivateConstants.DHT_REPORT, pin  humidity,
                                temperature (celsius), timestamp]

    """
    # pretty print the info
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[TIME]))
    temperature_c = data[TEMPERATURE]
    temperature_f =  temperature_c * 9/5 +  32
    print(f'DHT Data Report:'   
          f'Pin: {data[PIN]} Humidity: {data[HUMIDITY]} Temperature:  '
          f'{temperature_c}c  {temperature_f}f  Time: {date}')


# instantiate a pico
board = telemetrix_rpi_pico.TelemetrixRpiPico()

# set  2 pins to DHT mode
board.set_pin_mode_dht(DHT_PIN, the_callback)
board.set_pin_mode_dht(DHT_PIN2, the_callback)

# wait forever
while True:
    try:
        time.sleep(.01)
    except KeyboardInterrupt:
        board.shutdown()
        sys.exit(0)


