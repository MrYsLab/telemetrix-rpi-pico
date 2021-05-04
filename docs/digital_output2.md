## set_pin_mode_digital_output
```python
  async def set_pin_mode_digital_output(self, pin_number)

    Set a pin as a digital output pin.

    :param pin_number: pico pin number
```

**NOTE:** This method must be called before calling digital_write.
## digital_write
```python
 async def digital_write(self, pin, value)

    Set the specified pin to the specified value.

    :param pin: pico pin number

    :param value: pin value (1 or 0)
```
 
## Example: [blink.py](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/blink.py)


<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
