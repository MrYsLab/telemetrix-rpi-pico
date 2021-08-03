These methods are not specific to a given spi device but instead allow you to control
any spi device by implementing the device's protocol as specified by the 
manufacturer's datasheet.

## set_pin_mode_spi
```python
 def set_pin_mode_spi(self, spi_port=0, miso=16, mosi=19, clock_pin=18,
                         clk_frequency=500000, chip_select_list=None,
                         qualify_pins=True):
        """
        Specify the SPI port, SPI pins, clock frequency and an optional
        list of chip select pins. The SPI port is configured as a "master".
        :param spi_port: 0 = spi0, 1 = spi1
        :param miso: SPI data receive pin
        :param mosi: SPI data transmit pin 
        :param clock_pin: clock pin
        :param clk_frequency: clock frequency in Hz.
        :param chip_select_list: this is a list of pins to be used for
                           chip select. The pins will be configured as output,
                           and set to high ready to be used for chip select.
                           NOTE: You must specify the chips select pins here!
        :param qualify_pins: If true validate
                            for spi0:
                                 MOSI=19
                                 MISO=16
                                 CLOCK=18
                             for spi1:
                                 MOSI=15
                                 MISO=12
                                 CLOCK=14
        cammand message: [command, spi port, mosi, miso, clock, freq msb,
                          freq 3, freq 2, freq 1, number of cs pins, cs pins...]
                          
        
        """
```

This method must be called before calling any other spi method. You may choose
to use the "standard" MOSI, MISO, and Clock pins as listed above, or if you wish to use
a different set of pins, set *qualify_pins* to False. 

All chip select pins for the select SPI port are specified when calling this method.

## spi_cs_control
```python
 def spi_cs_control(self, chip_select_pin, select)

    Control an SPI chip select line :param chip_select_pin: pin connected to CS

    :param select: 0=select, 1=deselect
    
```
This method is used to set the state of the selected chip select pin. The chip select pin 
must be
one of the pins specified when calling set_pin_mode_spi.


## spi_read_blocking

```python
 def spi_read_blocking(self, number_of_bytes, spi_port=0, call_back=None, 
                       repeated_tx_data=0)

    Read the specified number of bytes from the specified SPI port and call 
    the callback function with the reported data.

    :param number_of_bytes: Number of bytes to read

    :param spi_port: SPI port 0 or 1

    :param call_back: Required callback function to report spi data as a result 
                      of read command

    :param repeated_tx_data: repeated data to send

    callback returns a data list:
        [SPI_READ_REPORT, spi_port, count of data bytes, data bytes, time-stamp]

        SPI_READ_REPORT = 13

```
This method retrieves the requested number of bytes and returns 
the result within the specified callback method. 

The callback argument is not optional and must be specified.

## spi_write_blocking

```python
 def spi_write_blocking(self, bytes_to_write, spi_port=0)

    Write a list of bytes to the SPI device.

    :param bytes_to_write: A list of bytes to write. This must be in the form of a list.

    :param spi_port: SPI port 0 or 1

```
This method writes a list of bytes to the specified SPI port.

## spi_set_format

```python
 def spi_set_format(self, spi_port=0, data_bits=8, spi_polarity=0, spi_phase=0)

    Configure how the SPI serializes and de-serializes data on the wire.

    :param spi_port: SPI port 0 or 1

    :param data_bits: Number of data bits per transfer. Valid range = 4-16

    :param spi_polarity: clock polarity. 0 or 1.

    :param spi_phase: clock phase. 0 or 1.
```
This method allows you to specify serialization specifics for SPI data transfers.


## Example: [spi_mpu9250.py](https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/examples/spi_mpu9250.py)

## Example Sample Output:
```python
TelemetrixRpiPico:  Version 1.1

Copyright (c) 2020-2021 Alan Yorinks All Rights Reserved.

Opening all potential serial ports...
	/dev/ttyACM0
Serial compatible device found and connected to /dev/ttyACM0
Retrieving pico ID...
Pico Unique ID: [230, 96, 88, 56, 131, 120, 0, 0]

Retrieving Telemetrix4pico firmware ID...
Telemetrix4pico firmware version: 1.1
Unexpected device ID: 0
AX = -1056  AY = 56  AZ = 16468  
GX = -384  GY = 345  GZ = -91  
AX = -1016  AY = 4  AZ = 16420  
GX = -394  GY = 339  GZ = -80  
```

<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
