## Importing
To import this package, the standard import string is:

```python
from telemetrix_rpi_pico import telemetrix_rpi_pico
```

Here is an example of instantiating the library and blinking the board LED 
until the user enters Control-C to end the application.


```python
import sys
import time
from telemetrix_rpi_pico import telemetrix_rpi_pico

# The GPIO pin number for the built-in LED
BOARD_LED = 25

# LED States
ON = 1
OFF = 0

# instantiate the library
board = telemetrix_rpi_pico.TelemetrixRpiPico()

# Set the DIGITAL_PIN as an output pin
board.set_pin_mode_digital_output(BOARD_LED)

try:
    while True:
        # turn led on
        board.digital_write(BOARD_LED, ON)
        time.sleep(1)
        # turn led off
        board.digital_write(BOARD_LED, OFF)
        time.sleep(1)

except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)

```

To exit your 
application cleanly, you should always call the **_shutdown_** method.


## The \__init__ Method

For most applications, when instantiating the library, you can accept all the default 
parameters.

```python
board = telemetrix_rpi_pico.TelemetrixRpiPico()
```

However, several parameters offered by the \__init__ method allow for some additional 
control.

```python

    def __init__(self, com_port=None, pico_instance_id=None,
                 sleep_tune=0.000001,
                 shutdown_on_exception=True,
                 reset_on_shutdown=True):

        """

        :param com_port: e.g. COM3 or /dev/ttyACM0.
                         Only use if you wish to bypass auto com port
                         detection.

        :param pico_instance_id: If not specified, than don't do id check.
                                 Else contains a board' s pico unique ID.
                                 This is passed as an array.

        :param sleep_tune: A tuning parameter (typically not changed by user)

        :param shutdown_on_exception: call shutdown before raising
                                      a RunTimeError exception, or
                                      receiving a KeyboardInterrupt exception

        :para reset_on_shutdown: Reset the board upon shutdown
```

Let's take a look at these parameters.


### com_port
If you have a single Pico connected to your computer, the library automatically 
finds and connects to the correct com port for your board.   You 
may, however, override the auto-discovery routine 
and explicitly specify the port to use. This feature may be helpful if you wish to 
select the port manually.



### pico_instance_id
Every Pico board has its own unique ID. This ID is displayed by the library whenever an 
application begins.

```python
Retrieving pico ID...
Pico Unique ID: [230, 96, 68, 48, 67, 85, 0, 0]
```
You may use this parameter to ensure that a connection is made to the desired Pico 
board.

### sleep_tune
This parameter is the sleep value expressed in seconds and is used at several strategic
points in the client. For example, the serial receiver continuously checks the serial 
port receive
buffer for an available
character to process. If there is no character in the
buffer, the client sleeps for the sleep_tune period before checking again.

Typically, you would accept the default value.

### shutdown_on_exception
When this parameter is set to True, the library _shutdown_ method is automatically
called when an exception is detected and all reporting is disabled.

By setting this parameter to False, the Pico may continue to send data to
your application even after restarting it.

The default is True and is recommended to be used.

### reset_on_shutdown
When set to True (the default), this parameter will send a message to the Pico 
to reset itself. After resetting, the Pico board LED 
will flash twice, indicating the Pico has been reset.


   
<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
