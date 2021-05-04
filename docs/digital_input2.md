## set_pin_mode_digital_input
```python
 async def set_pin_mode_digital_input(self, pin_number, callback=None)

    Set a pin as a digital input.

    :param pin_number: pico pin number

    :param callback: callback function

    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for digital input pins = 2
```
## set_pin_mode_digital_input_pull_down
```python
async def set_pin_mode_digital_input_pull_down(self, pin_number, callback=None)

    Set a pin as a digital input with pull down enabled.

    :param pin_number: pico pin number

    :param callback: callback function

    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for digital input pins with pullups enabled = 2
```

## set_pin_mode_digital_input_pullup
```python
 async def set_pin_mode_digital_input_pullup(self, pin_number, callback=None)

    Set a pin as a digital input with pullup enabled.

    :param pin_number: pico pin number

    :param callback: callback function

    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for digital input pins with pullups enabled = 2
```

The signature for all three of these methods is identical. The only difference is how 
the Pico controls its internal resistor.

This method enables one of the selected GPIO pins for digital input. Once this method is 
called, data 
change 
reporting is enabled for that pin. A report is generated 
when the previously read value differs from the current value. Initially, the 
previously read value is set to zero. Therefore, the first report will be generated 
when the current value is non-zero.

The pin type in the report is used to differentiate the pin type that 
generated the 
report. 
For 
digital inputs, this value is 2. The pin number contains the reporting GPIO pin number. 
The 
timestamp is in raw time form. 

## disable_digital_reporting

Reporting is automatically enabled when you set the pin mode. There are times you may 
wish to turn off reporting for a specific digital input pin. This method allows you to do 
that.

```python
 async def disable_digital_reporting(self, pin)

    Disables digital reporting for a single digital input.

    :param pin: Pin number.
```

## enable_digital_reporting

You may re-enable reporting for a selected digital input pin using this method.

```python
 async def enable_digital_reporting(self, pin)

    Enable reporting on the specified digital pin.

    :param pin: Pin number.
```

## disable_all_reporting

This method disables reporting for all analog and digital pins configured as inputs.

To re-enable, you will need to re-enable each pin individually.

```python
 async def disable_all_reporting(self)

    Disable reporting for all digital and analog input pins
```

## Example: [digital_input_pullup.py](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/digital_input_pullup.py)

## Example Sample Output:

```python
Report Type: 2 Pin: 12 Value: 0 Time Stamp: 2021-03-18 14:37:08
Report Type: 2 Pin: 12 Value: 1 Time Stamp: 2021-03-18 14:37:09
Disabling reporting for pin 12 3 seconds. All others enabled
Re-enabling reporting for pin 12.
Report Type: 2 Pin: 12 Value: 0 Time Stamp: 2021-03-18 14:37:16
Report Type: 2 Pin: 12 Value: 1 Time Stamp: 2021-03-18 14:37:16
```
<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
