## set_pin_mode_analog_input

This method enables one of the four ADC ports. Once this method is called, data change 
reporting is enabled for that port. A report is generated 
when the previously read value differs from the current value. Initially, the 
previously read value is set to zero. Therefore, the first report will be generated 
when the current value is non-zero.

```python
 def set_pin_mode_analog_input(self, adc_number, differential=0, callback=None)

    Set a pin as an analog input.

    :param adc_number: ADC Number 0-4

                   ADC numbers are mapped as following:
                   ADC0 = GPIO 26 (Physical Pin 31)
                   ADC1 = GPIO 27 (Physical Pin 32)
                   ADC2 = GPIO 28 (Physical Pin 34)

                   Internal Mapping
                   ADC3 = GPIO 29 (Physical Pin 35) ADC Reference Voltage
                   ADC4 = GPIO 30 (No Physical pin - mapped internally)
                                  CPU temperature

    :param differential: difference in previous to current value before report will be generated

    :param callback: callback function

    callback returns a data list:

    [ANALOG_REPORT, pin_number, pin_value, raw_time_stamp]

    The ANALOG_REPORT = 3

```
### Parameters:

#### adc_number

The Pico supports 4 ADC inputs. ADC3 is hardwired to the internal temperature sensor. 
Associate the desired ADC port with your device using this parameter.

| ADC Number                     |       GPIO Number       | Physical Pin Number       |
|--------------------------------|:-----------------------:|:--------------------------|
| ADC 0                          |           26            | 31                        |
| ADC 1                          |           27            | 32                        |
| ADC2                           |           28            | 34                        |
| ADC 3  (ADC Reference Voltage) |           29            | 35                        | 
| ADC 4   (CPU Temperature)      | N/A (Mapped Internally) | N/A (Mapped Internally)   | 


#### differential

The differential parameter is used to qualify reported values by comparing the last 
value read and determining if the current value differs from the previous value 
(plus or minus) by the differential value.
If the _differential_ is
set to zero, then all changes are reported. Otherwise, the data value must change by a 
value, plus or minus the differential value.
 So if the differential 
value is set to 5, and the last reading was a
value of 1000, a report will be generated when the current value is greater 
than 1005 or less than 995.


#### callback
You must specify a callback function using this parameter. Data returned to the 
callback for an analog input is: 

**[pin_type, pin_number, pin_value, raw_time_stamp]**

The pin type is used to differentiate the pin type that generated the report. For 
analog inputs, this value is 3. The pin number contains the reporting ADC number. The 
timestamp is in raw time form. 

## disable_analog_reporting

Reporting is automatically enabled when you set the pin mode. There are times you may 
wish to turn  off reporting for a specific ADC. This method allows you to do that.

```python
 def disable_analog_reporting(self, pin)

    Disables analog reporting for a single analog pin.

    :param pin: Analog pin number. For example for ADC0, the number is 0.
```

## enable_analog_reporting

You may re-enable reporting for a selected ADC using this method.

```python
 def enable_analog_reporting(self, pin)

    Enables analog reporting for the specified pin.

    :param pin: Analog pin number. For example for ADC0, the number is 0.
```

## disable_all_reporting

This method disables reporting for all analog and digital pins configured as inputs.

To re-enable, you will need to re-enable each pin individually.

```python
 def disable_all_reporting(self)

    Disable reporting for all digital and analog input pins
```

## Example: [analog_input.py](https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/examples/analog_input.py)

## Example Sample Output:

```python
ADC Report Type: 3 ADC: 4 Value: 870 Time Stamp: 2021-03-18 14:11:12
```
<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
