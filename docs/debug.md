# Diagnostic Aids

Two methods have been provided to aid in debugging.

## loopback
This method allows you to check that there is serial communication between the client and the server.

```python
  def loop_back(self, start_character, callback=None)

    This is a debugging method to send a character to the pico device, 
    and have the device loop it back.

    :param start_character: The character to loop back. It should be an integer.

    :param callback: Looped back character will appear in the callback method
```

## Example: [loop_back](https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/examples/loop_back.py)


## get_pico_pins

```python
 def get_pico_pins(self):

    This method returns the pico_pins dictionary

    :return: pico_pins
```
The keys in the dictionary returned from this method are the GPIO pin-numbers. The 
value is 
the 
pin type assigned to the pin:

Pin Mode MAP:

|           **PIN TYPE**         | **VALUE** |
|:-----------------------:|:--------------:|
|      DIGITAL_INPUT      |        0       |
|      DIGITAL_OUTPUT     |        1       |
|        PWM_OUTPUT       |        2       |
|   DIGITAL_INPUT_PULLUP  |        3       |
| DIGITAL_INPUT_PULL_DOWN |        4       |
|       ANALOG_INPUT      |        5       |
|           i2c           |        9       |
|        NEO_PIXEL        |       10       |
|       MODE_NOT_SET      |       255      |

## Example: [get_pico_pins.py](https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/examples/get_pico_pins.py)

### Sample Output

Sending: A
Sending: B
Sending: Z
Looped back: A
Looped back: B
Looped back: Z

## send_debug_info reports

Telemetrix4RpiPico contains the send_debug_info function that allows you to send 
internal values back to the client and display them on the console.

```
void send_debug_info(byte id, int value)
```

The report is formatted as follows:

DEBUG ID: _**byte_id**_ Value: **_int_value_**


<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
