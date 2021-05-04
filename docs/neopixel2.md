## set_pin_mode_neopixel

```python
 async def set_pin_mode_neopixel(self, pin_number=28, num_pixels=8, fill_r=0, fill_g=0, 
                            fill_b=0)

    Initialize the pico for NeoPixel control. Fill with rgb values specified.

    Default: Set all the pixels to off.

    :param pin_number: neopixel GPIO control pin

    :param num_pixels: number of pixels in the strip

    :param fill_r: initial red fill value 0-255

    :param fill_g: initial green fill value 0-255

    :param fill_b: initial blue fill value 0-255
```

With this method, you establish the GPIO pin-number for NeoPixel control, 
the number of LEDs in the strip, and optional fill color.

All LEDs will be set to the specified fill color. By default, all LEDs are turned off.

## neo_pixel_set_value

```python
 async def neo_pixel_set_value(self, pixel_number, r=0, g=0, b=0, auto_show=False)

    Set the selected pixel in the pixel array on the Pico to the value provided.

    :param pixel_number: pixel number

    :param r: red value 0-255

    :param g: green value 0-255

    :param b: blue value 0-255

    :param auto_show: call show automatically
```
This method is used to set the RGB values of the specified LED in the string. You may 
display the request immediately by setting **auto_show** to True. Otherwise, the change 
for 
all LEDs will display when _neo_pixel_show_ is called.

## neopixel_clear

```python
 async def neopixel_clear(self, auto_show=True)

    Clear all pixels

    :param auto_show: call show automatically

```

This method turns all LEDs off. You may delay the action until _neopixel_show_ is called 
by setting **auto_show** to False. 

## neopixel_fill

```python
 async def neopixel_fill(self, r=0, g=0, b=0, auto_show=True)

    Fill all pixels with specified value

    :param r: 0-255

    :param g: 0-255

    :param b: 0-255

    :param auto_show: call show automatically
```

This method sets all the LEDs in the string to the same color. You may delay the action 
until _neopixel_show_ is called 
by setting **auto_show** to False. 
<br>

## neopixel_show

```python
 async def neopixel_show(self)

    Write the NeoPixel buffer stored in the Pico to the NeoPixel strip.
```


This method is used to display color updates for all LEDs.

## Example: [neopixels.py](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/neopixels.py)

<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
