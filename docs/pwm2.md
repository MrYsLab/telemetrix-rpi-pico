## set_pin_mode_pwm_output

```python
 async def set_pin_mode_pwm_output(self, pin_number):
    """
    Enable a pin as a PWM pin. Maximum number of PWMs is 16.
    The frequency is fixed at 50 hz.

    Note: There are up to 16 pins that can be assigned as
    PWM. Servo pins share the 16 PWM pins.


    :param pin_number: pico GPIO pin number

```
The Pico allows up to 16 GPIO pins to be assigned as PWM outputs.

**NOTE:** Servo assigned pins are a special case of PWM so they share in the 16 pins.

## pwm_write

```python
 async def pwm_write(self, pin, duty_cycle=0, raw=False)

    Set the specified pin to the specified value.

    :param pin: pico GPIO pin number

    :param duty_cycle: if the raw parameter is False, then this is expressed as a percentage between 0 and 100

                    if the raw parameter is True, then the valid range
                    of values is from 0 - 19999

    :param raw: Sets how the duty-cycle parameter is perceived.
```

## Example: [fade.py](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/fade.py)
<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.