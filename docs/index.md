

<div style="text-align:center;color:#990033; font-family:times, serif;font-size:3em"><i>The Telemetrix User's Guide</i></div>
<div style="text-align:center;color:#990033; font-family:times, serif;font-size:3em"><i>For The Raspberry Pi Pico  </i></div>

<br>


*Telemetry* is a system for collecting data on a remote device and then 
automatically transmitting the collected data back to local receiving equipment for 
processing.

The 
Telemetrix Project
for the Raspberry Pi Pico does just that.

Telemetrix for the Raspberry Pi Pico consists of two main software components. 
A resident Pico server, and a client, residing on a Windows, Linux, or macOS 
PC.  
The 
server is 
implemented using the 
[Raspberry Pico C SDK,](https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-c-sdk.pdf)
providing full access to all Pico processor features 
and providing the best possible performance. 
There are two Python clients to choose from. 
[Telemetrix-RPi-Pico](https://github.com/MrYsLab/telemetrix-rpi-pico)
is implemented using Python threading to 
implement concurrency, and 
[Tmx-Pico-Aio](https://github.com/MrYsLab/tmx-pico-aio)
uses Python asyncio for concurrency.


The server and client are physically connected using a USB cable, and they
communicate with each other over a serial transport running at 115000 baud.

With Telemetrix, you can do things such as establish a GPIO pin as a PWM output pin, 
and set its value to run a DC motor, or perhaps establish the pin as a control pin for a 
NeoPixel strip. With 
Telemetrix, you can even have the Pico communicate with your favorite i2c device.

![](./images/tmx.png)

Telemetrix gives the appearance that the Pico is being _programmed_ using a
[Traditional Python API.](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/html/telemetrix_rpi_pico/index.html)
or [Python asyncio API.](https://htmlpreview.github.io/?https://github.com/MrYsLab/tmx-pico-aio/blob/master/html/tmx_pico_aio/index.html#tmx_pico_aio.tmx_pico_aio.TmxPicoAio.reset_board)
But in fact, the Pico is running a fixed application and is not programmed in the 
traditional sense. Once the server is installed on the Pico, code is not generated nor 
uploaded to the Pico. Instead, 
the Pico awaits commands from the server and interprets and acts upon those commands.

If the client commands the Pico to establish a GPIO pin as an input, the Pico 
autonomously monitors the pin for data changes. When a change is detected, the 
Pico forms a report and relays it to the client over the serial link.


<br>

# Summary Of Major Features

* Applications are programmed using conventional Python 3.7 or greater.
* All Data change events are reported asynchronously via user registered callback functions. 
* Each data change event is time-stamped.
* Online API Reference Documentation is provided:
    * For the [Threaded Python Client.](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/html/telemetrix_rpi_pico/index.html)
    * For the [Asyncio Python Client.](https://htmlpreview.github.io/?https://github.com/MrYsLab/tmx-pico-aio/blob/master/html/tmx_pico_aio/index.html)
* A complete set of working examples is provided for both [traditional Python](https://github.com/MrYsLab/telemetrix-rpi-pico/tree/master/examples)
  and the [asyncio version.](https://github.com/MrYsLab/tmx-pico-aio/tree/master/examples)
* Integrated debugging methods are included as part of the Pico Server 
  SDK source code to aid in adding new features.

# Intuitive And Easy To Use APIs

For example, to receive asynchronous digital pin state data change notifications using 
traditional Python, you do the following:


### 1. Set a pin mode for the pin and register an associated callback function for the pin. 

The example below illustrates how this is done.

#### Callbacks

All callbacks are written to accept a single parameter. In the example below, this 
parameter is named _data_. 


```python
        def the_callback(data):
     
            # Your code here.
```
Upon receiving a data change report message from the Pico,
the client 
creates a 
list containing the data describing the change event and calls the associated callback 
function 
passing in the list as a parameter.

For a digital data change, the list would contain the following:
    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**[pin_type=digital input, pin_number, pin_value, time stamp]**

Each input pin type returns a unique list, as described in the API.

The first element in the list is the pin type. Knowing the pin type, you may 
optionally have a single callback function handle multiple event types using the 
pin type to identify the callback source.

### 2. Have your application sit in a loop, waiting for notifications.

 
# A Working Example   

Here is a Telemetrix example that monitors several digital input pins:

```python
import sys
import time

from telemetrix_rpi_pico import telemetrix_rpi_pico

"""
Monitor 4 digital input pins with pull-up enabled for each
"""


# Callback data indices
# When the callback function is called, the client fills in 
# the data parameter. Data is a list of values, and the following are 
# indexes into the list to retrieve report information

CB_PIN_MODE = 0 # The mode of the reporting pin (input, output, PWM, etc.)
CB_PIN = 1      # The GPIO pin number associated with this report
CB_VALUE = 2    # The data value reported
CB_TIME = 3     # A time stamp when the data change occurred


def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred
    :param data: [pin mode, pin, current reported value, pin_mode, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    print(f'Report Type: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} '
          f'Value: {data[CB_VALUE]} Time Stamp: {date}')


board = telemetrix_rpi_pico.TelemetrixRpiPico()
board.set_pin_mode_digital_input_pullup(12, the_callback)
board.set_pin_mode_digital_input_pullup(13, the_callback)
board.set_pin_mode_digital_input_pullup(14, the_callback)
board.set_pin_mode_digital_input_pullup(15, the_callback)

try:
    while True:
        time.sleep(.0001)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
```

And here is some sample output:

```python
TelemetrixRpiPico:  Version 0.7

Copyright (c) 2020 Alan Yorinks All Rights Reserved.

Opening all potential serial ports...
	/dev/ttyACM0
Serial compatible device found and connected to /dev/ttyACM0
Retrieving pico ID...
Pico Unique ID: [230, 96, 68, 48, 67, 85, 0, 0]

Retrieving Telemetrix4pico firmware ID...
Telemetrix4pico firmware version: 0.3
Report Type: 2 Pin: 12 Value: 1 Time Stamp: 2021-03-14 13:34:52
Report Type: 2 Pin: 13 Value: 1 Time Stamp: 2021-03-14 13:34:52
Report Type: 2 Pin: 14 Value: 1 Time Stamp: 2021-03-14 13:34:52
Report Type: 2 Pin: 15 Value: 1 Time Stamp: 2021-03-14 13:34:52
Report Type: 2 Pin: 13 Value: 0 Time Stamp: 2021-03-14 13:35:21
Report Type: 2 Pin: 13 Value: 1 Time Stamp: 2021-03-14 13:35:22
Report Type: 2 Pin: 14 Value: 0 Time Stamp: 2021-03-14 13:35:29
Report Type: 2 Pin: 14 Value: 1 Time Stamp: 2021-03-14 13:35:31
Report Type: 2 Pin: 15 Value: 0 Time Stamp: 2021-03-14 13:35:33
Report Type: 2 Pin: 15 Value: 1 Time Stamp: 2021-03-14 13:35:34


```
A [similar example](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/digital_input_pullup.py)
is provided for asyncio.


<br>
<br>

Copyright (C) 2022 Alan Yorinks. All Rights Reserved.

**Last updated 1 July 2022**
