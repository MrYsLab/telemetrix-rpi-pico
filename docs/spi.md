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
        :param chip_select_list: this is a list of pins to be used for chip select.
                           The pins will be configured as output, and set to high
                           ready to be used for chip select.
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
to use the "standard" MOSI, MISO and Clock pins as listed above, or if you wish to use
a different set of pins, set *qualify_pins* to False. 

All chip select pins for the select SPI port are specified when calling this method.

## spi_cs_control
```python
 def spi_cs_control(self, chip_select_pin, select)

    Control an SPI chip select line :param chip_select_pin: pin connected to CS

    :param select: 0=select, 1=deselect
    
```
## i2c_read

```python
 def i2c_read(self, address, register, number_of_bytes, callback=None, i2c_port=0, no_stop=False)

    Read the specified number of bytes from the specified register for the i2c device.

    :param address: i2c device address

    :param register: i2c register (or None if no register selection is needed)

    :param number_of_bytes: number of bytes to be read

    :param callback: Required callback function to report i2c data as a result of read command

    :param i2c_port: 0 = port 0, 1 = port 1

    :param no_stop: If true, master retains control of the bus at the end of the transfer (no Stop is issued), and the next transfer will begin with a Restart rather than a Start.

    callback returns a data list: [I2C_READ_REPORT, i2c_port, i2c_device_address, count of data bytes, data bytes, time-stamp]

    I2C_READ_REPORT = 10
```

This method allows you to read a specified number of bytes from the device. 

The **address** parameter specifies the i2c address of the device.

The **register** parameter specifies the i2c register to use. If the device does not 
require a register to be specified, this parameter is set to None.

The **number_of_bytes** parameter specifies how many bytes are to be read from the device.
Data is returned via callback, and therefore you must specify a **callback** parameter.

The **i2c_port** specifies which of the two i2c ports to use for this device. The SDA 
and SCL pins are implied as a result of the call to  _set_pin_mode_i2c_.

Some devices require that after a read, the i2c master retain control of the bus. The 
**no_stop** parameter allows you to select this behavior.

The data returned to the callback is similar to all other callbacks. The items in the 
list passed to the callback function are:

[I2C_READ_REPORT, i2c_port, i2c_device_address, count of data bytes, data bytes, time-stamp]

The first element is the report type, and I2C_READ_REPORT has a value of 10. The 
i2c_port, the device's i2c address, the number of the bytes returned, the actual data 
bytes, and a time-stamp are also contained in the report.

## i2c_write

```python
 def i2c_write(self, address, args, i2c_port=0, no_stop=False)

    Write data to an i2c device.

    :param address: i2c device address

    :param args: A variable number of bytes to be sent to the device passed in as a list. 
                  NOTE: THIS MUST BE IN THE FORM OF A LIST.

    :param i2c_port: 0= port 0, 1 = port 1

    :param no_stop: If true, master retains control of the bus at the end of the 
                    transfer (no Stop is issued), and the next transfer will begin with a 
                    Restart rather than a Start.
```
This method is used to write a variable number of bytes to an i2c device. You specify 
the i2c address, a list of the bytes to send, the i2c port to use, and a flag to 
indicate if the master retains control of the bus at the end of the transfer.


## Example: [i2c_adxl345_accelerometer.py](https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/examples/i2c_adxl345_accelerometer.py)

## Example Sample Output:
```python

TelemetrixRpiPicoAio:  Version 1.0

Copyright (c) 2021 Alan Yorinks All Rights Reserved.

Opening all potential serial ports...
	/dev/ttyACM0
Retrieving pico ID...
Pico Unique ID: [230, 96, 88, 56, 131, 120, 0, 0]
Telemetrix4RPiPico Version Number: 1.0
Raw Data:  [10, 0, 83, 50, 6, 248, 255, 7, 0, 97, 0]
ADXL345 Report On: 2021-05-04 17:36:52: 
		i2c_port=0 x-pair=248, 255  y-pair=7, 0 z-pair=97, 0
		
TelemetrixRpiPicoAio:  Version 1.0

Copyright (c) 2021 Alan Yorinks All Rights Reserved.

Opening all potential serial ports...
	/dev/ttyACM0
Retrieving pico ID...
Pico Unique ID: [230, 96, 88, 56, 131, 120, 0, 0]
Telemetrix4RPiPico Version Number: 1.0
Raw Data:  [10, 0, 83, 50, 6, 248, 255, 7, 0, 97, 0]
ADXL345 Report On: 2021-05-04 17:36:52: 
		i2c_port=0 x-pair=248, 255  y-pair=7, 0 z-pair=97, 0
		
```

<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
