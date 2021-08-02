# noinspection GrazieInspection
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

"""
This example initializes an MPU9250 and then reads the accelerometer
and gyro values and prints them to the screen.

The processing of the data returned from the MPU9250 is done within 
the callback functions.
"""

import sys
import time

from telemetrix_rpi_pico import telemetrix_rpi_pico

# Instantiate the TelemetrixRpiPico class accepting all default parameters.
pico = telemetrix_rpi_pico.TelemetrixRpiPico()

"""
 CALLBACKS
 
 These functions process the data returned from the MPU9250
"""


def the_device_callback(report):
    """
    Verify the device ID
    :param report: [SPI_REPORT, SPI_PORT, Number of bytes, device id]
    """
    if report[3] == 0x71:
        print('MPU9250 Device ID confirmed.')
    else:
        print(f'Unexpected device ID: {report[3]}')


# noinspection GrazieInspection
def accel_callback(report):
    """
    Print the AX, AY and AZ values.
    :param report: [SPI_REPORT, SPI_PORT, Number of bytes, AX-msb, AX-lsb
    AY-msb, AY-lsb, AX-msb, AX-lsb]
    """
    print(f"AX = {int.from_bytes(report[3:5], byteorder='big', signed=True)}  "
          f"AY = {int.from_bytes(report[5:7], byteorder='big', signed=True)}  "
          f"AZ = {int.from_bytes(report[7:9], byteorder='big', signed=True)}  ")


def gyro_callback(report):
    # noinspection GrazieInspection
    """
        Print the GX, GY, and GZ values.

        :param report: [SPI_REPORT, SPI_PORT, Number of bytes, GX-msb, GX-lsb
        GY-msb, GY-lsb, GX-msb, GX-lsb]
        """
    print(f"GX = {int.from_bytes(report[3:5], byteorder='big', signed=True)}  "
          f"GY = {int.from_bytes(report[5:7], byteorder='big', signed=True)}  "
          f"GZ = {int.from_bytes(report[7:9], byteorder='big', signed=True)}  ")


# This is a utility function to read SPI data
def read_data_from_device(register, number_of_bytes, callback):
    # noinspection GrazieInspection
    """
    This function reads the number of bytes using the register value.
    Data is returned via the specified callback.

    :param register: register value
    :param number_of_bytes: number of bytes to read
    :param callback: callback function
    """
    # OR in the read bit
    data = register | 0x80

    # activate chip select
    pico.spi_cs_control(5, 0)

    # select the register
    pico.spi_write_blocking([data], 0)
    time.sleep(.1)

    # read the data back
    pico.spi_read_blocking(number_of_bytes, 0, call_back=callback)

    # deactivate chip select
    pico.spi_cs_control(5, 1)
    time.sleep(.1)


# Convenience values for the pins.
# Note that the CS value is within a list

# These are "non-standard" pin-numbers, and therefore
# the qualify_pins parameter is set to FALSe

SPI_PORT = 0
MISO = 4
MOSI = 7
CLK = 6
CS = [5]
CS_PIN = 5

NUM_BYTES_TO_READ = 6
FREQ = 500000

# initialize the device
pico.set_pin_mode_spi(SPI_PORT, MISO, MOSI, CLK,
                      FREQ, CS, qualify_pins=False)

# reset the device
pico.spi_cs_control(CS_PIN, 0)
pico.spi_write_blocking([0x6B, 0], SPI_PORT)
pico.spi_cs_control(CS_PIN, 1)

time.sleep(.3)

# get the device ID
read_data_from_device(0x75, 1, the_device_callback)

while True:
    try:
        # get the acceleration values
        read_data_from_device(0x3b | 0x80, 6, accel_callback)

        # get the gyro values
        read_data_from_device(0x43 | 0x80, 6, gyro_callback)
        time.sleep(.1)
    except KeyboardInterrupt:
        pico.shutdown()
        sys.exit(0)
