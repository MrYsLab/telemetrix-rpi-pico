## Importing
To import this package, the standard import string is:

```python
from tmx_pico_aio import tmx_pico_aio
```

Here is an example of instantiating the library and blinking the board LED 
until the user enters Control-C to end the application.


```python



import asyncio
import sys

from tmx_pico_aio import tmx_pico_aio

"""
Setup a pin for digital output 
and toggle the pin 5 times.
"""

# some globals
DIGITAL_PIN = 25  # the board LED


async def blink(my_board, pin):
    # Set the DIGITAL_PIN as an output pin
    # set the pin mode
    await my_board.set_pin_mode_digital_output(pin)

    # toggle the pin 4 times and exit
    for x in range(4):
        print('ON')
        await my_board.digital_write(pin, 1)
        await asyncio.sleep(1)
        print('OFF')
        await my_board.digital_write(pin, 0)
        await asyncio.sleep(1)


# get the event loop
loop = asyncio.get_event_loop()
try:
    board = tmx_pico_aio.TmxPicoAio()
except KeyboardInterrupt:
    sys.exit()

try:
    # start the main function
    loop.run_until_complete(blink(board, DIGITAL_PIN))
    loop.run_until_complete(board.reset_board())
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)



```

To exit your 
application cleanly, you should always call the **_shutdown_** method.

You may also wish to call the reset_board method when exiting to do
a hardware reset of the Pico.


## The \__init__ Method

For most applications, when instantiating the library, you can accept all the default 
parameters.

```python
board = tmx_pico_aio.TmxPicoAio()
```

However, several parameters offered by the \__init__ method allow for some additional 
control.

```python

    def __init__(self, com_port=None, pico_instance_id=None,
                 sleep_tune=0.000001,
                 autostart=True,
                 loop=None,
                 shutdown_on_exception=True,
                 close_loop_on_shutdown=True,
                 reset_on_shutdown=True):

        """

        :param com_port: e.g. COM3 or /dev/ttyACM0.
                         Only use if you wish to bypass auto com port
                         detection.

        :param pico_instance_id: If not specified, than don't do id check.
                                 Else contains a board' s pico unique ID.
                                 This is passed as an array.

        :param sleep_tune: A tuning parameter (typically not changed by user)

        :param autostart: If you wish to call the start method within
                          your application, then set this to False.

        :param loop: optional user provided event loop

        :param shutdown_on_exception: call shutdown before raising
                                      a RunTimeError exception, or
                                      receiving a KeyboardInterrupt exception

        :param close_loop_on_shutdown: stop and close the event loop loop
                                       when a shutdown is called or a serial
                                       error occurs

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

### autostart

Typically, you wish to have your program start all tasks automatically, 
however, you may delay startup by setting this parameter to False and add
your custom code before calling the start_aio method

### loop

You may specify an asyncio loop to use. The default is to allow the system
to use the default event loop.

### shutdown_on_exception
When this parameter is set to True, the library _shutdown_ method is automatically
called when an exception is detected and all reporting is disabled.

By setting this parameter to False, the Pico may continue to send data to
your application even after restarting it.

The default is True and is recommended to be used.

### close_loop_on_shutdown
Typically the event loop is shutdown when the application exits. If you
wish to leave event loop open, set this parameter False.

### reset_on_shutdown
When set to True (the default), this parameter will send a message to the Pico 
to reset itself. After resetting, the Pico board LED 
will flash twice, indicating the Pico has been reset.


   
<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
