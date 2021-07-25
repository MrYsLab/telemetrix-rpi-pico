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

import sys
import time
from telemetrix_rpi_pico import telemetrix_rpi_pico
"""
This example sets up and control an MPU9250 spi accelerometer.
It will continuously print data the raw xyz data from the device.
"""

class MPU9250_SPI:
    """
        This class provides control of an MPU9250 accelerometer using SPI.
    """
    def __init__(self, spi_port, miso,  mosi, clock_pin,
                              chip_select_list, qualify_pins):
        """

        :param spi_port: 0 or 1
        :param miso: miso pin
        :param mosi: mosi pin
        :param clock_pin: clock pin
        :param chip_select_list: chip select pin list
        :param qualify_pins: qualify pins again standard set
        """
        self.spi_port = spi_port
        self.mosi = mosi
        self.miso = miso
        self.clock_pin = clock_pin
        self.chip_select_list = chip_select_list
        self.cs = chip_select_list[0]

        self.pico = telemetrix_rpi_pico.TelemetrixRpiPico()

        # initialize the spi0 to use a "non-standard" set of pins
        self.pico.set_pin_mode_spi(spi_port, miso=self.miso, mosi=self.mosi,
                                   clock_pin=self.clock_pin,
                                  chip_select_list=[5], qualify_pins=False)
        self.run_the_example()

    def run_the_example(self):
        """
        configure the mpu9250 to get x, y, and z values.
        """

        # reset the mpu9250
        self.reset_mpu9250()

        # get the

    def reset_mpu9250(self):
        """
        Reset the chip
        """
        self.pico.write_blocking_spi([0x6B, 0x00], spi_port=self.spi_port,
                                     chip_select_pin=self.cs)


    def read_registers(self):

# the call back function to print the adxl345 data
def the_callback(data):
    """
    Data is supplied by the library.
    :param data: [report_type, i2c port, Device address, device read register,
    number of bytes returned, x data pair, y data pair, z data pair
    time_stamp]
    """

    print(data)
    time_stamp = data.pop()
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_stamp))
    print(f'Raw Data:  {data}')
    print(f'MPU9250 Report On: {date}: ')
    print(f'\t\ti2c_port={ data[1]} x-pair={data[5]}, '
          f'{data[6]}  y-pair={data[7]}, '
          f'{data[8]} z-pair={data[9]}, '
          f'{data[10]}')
    print()


def mpu9250(my_board):
    # initialize spi0 with MOSI=7  MISO=5  CLK=6 CS=5
    my_board.set_pin_mode_spi(0, miso=5, mosi=7, clock_pin=6,
                              chip_select_list=5, qualify_pins=False)
    time.sleep(.2)

    # reset the mpu9250
    my_board.write_blocking_spi([0x6B, 0x00], spi_port=0, chip_select_pin=5)



    # set up power and control register
    my_board.i2c_write(83, [45, 0])
    # time.sleep(.2)
    my_board.i2c_write(83, [45, 8])
    # time.sleep(.2)

    # set up the data format register
    my_board.i2c_write(83, [49, 8])
    # time.sleep(.5)
    my_board.i2c_write(83, [49, 3])
    # time.sleep(.1)

    # read_count = 20
    while True:
        # read 6 bytes from the data register
        try:
            my_board.i2c_read(83, 50, 6, the_callback)
            # time.sleep(.3)
        except (KeyboardInterrupt, RuntimeError):
            my_board.shutdown()
            sys.exit(0)


board = telemetrix_rpi_pico.TelemetrixRpiPico()
try:
    mpu9250(board)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
