## set_pin_mode_pwm_output

```python
 def set_pin_mode_pwm_output(self, pin_number, value_range=255)

    Enable a pin as a PWM pin. Maximum number of PWMs is 16.

    :param pin_number: pico pin number

    :param value_range: value range - 16 bits
```
The Pico allows up to 16 GPIO pins to be assigned as PWM outputs. The **value_range** 
parameter is used to set how many bits represent the full voltage measurement. 

## pwm_write

```python
 def pwm_write(self, pin, value)

    Set the specified pin to the specified value.

    :param pin: pico pin number

    :param value: pin value - size is determined by what was set for value_range
        when set_pin_mode_pwm_output was called.
```

## Example: [fade.py](https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/examples/fade.py)
<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.