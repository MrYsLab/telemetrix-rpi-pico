## set_pin_mode_sonar

```python
 async def set_pin_mode_sonar(self, trigger_pin, echo_pin, callback=None)

    :param trigger_pin: Sensor trigger gpio pin

    :param echo_pin: Sensor echo gpio pin

    :param callback: callback

    callback returns a data list:

    [ SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]

    SONAR_DISTANCE = 11
```

A maximum of  4 HC-SR04 type devices is supported. Reporting will immediately begin 
when this method is invoked.
<br>
<br>

## Example: [hc_sr04.py](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/hc_sr04.py)

## Example Sample Output (example modified for a single sensor):

```python
TelemetrixRpiPicoAio:  Version 1.0

Copyright (c) 2021 Alan Yorinks All Rights Reserved.

Opening all potential serial ports...
	/dev/ttyACM0
Retrieving pico ID...
Pico Unique ID: [230, 96, 88, 56, 131, 120, 0, 0]
Telemetrix4RPiPico Version Number: 1.0
2021-05-04 17:18:52	 Trigger Pin::	16	 Distance(cm):	32.06
2021-05-04 17:18:52	 Trigger Pin::	16	 Distance(cm):	32.06
2021-05-04 17:18:52	 Trigger Pin::	16	 Distance(cm):	31.17
2021-05-04 17:18:52	 Trigger Pin::	16	 Distance(cm):	30.22
```

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.