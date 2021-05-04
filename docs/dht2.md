## set_pin_mode_dht
```python
 async def set_pin_mode_dht(self, pin, callback=None)

    :param pin: connection pin

    :param callback: callback function

    callback returns a data list:

    DHT REPORT, DHT_DATA=1, PIN, Humidity, Temperature (c),Time]

    DHT_REPORT = 12

```
A maximum of 2 DHT devices is supported. Reporting will begin immediately after
executing this method. Reports are generated every 2 seconds.
<br>
<br>

## Example: [dht.py](https://github.com/MrYsLab/tmx-pico-aio/blob/master/examples/dht.py)

## Example Sample Output:

```python
TelemetrixRpiPicoAio:  Version 1.0

Copyright (c) 2021 Alan Yorinks All Rights Reserved.

Opening all potential serial ports...
	/dev/ttyACM0
Retrieving pico ID...
Pico Unique ID: [230, 96, 88, 56, 131, 120, 0, 0]
Telemetrix4RPiPico Version Number: 1.0
DHT Data Report:Pin: 2 Humidity: 39.0 Temperature:  25.0c  77f  Time: 2021-05-04 17:14:20
DHT Data Report:Pin: 15 Humidity: 49.79 Temperature:  24.1c  75f  Time: 2021-05-04 17:14:22
DHT Data Report:Pin: 2 Humidity: 42.0 Temperature:  24.0c  75f  Time: 2021-05-04 17:14:24
DHT Data Report:Pin: 15 Humidity: 45.79 Temperature:  23.79c  75f  Time: 2021-05-04 17:14:26
DHT Data Report:Pin: 2 Humidity: 40.0 Temperature:  24.0c  75f  Time: 2021-05-04 17:14:28
DHT Data Report:Pin: 15 Humidity: 45.7 Temperature:  23.79c  75f  Time: 2021-05-04 17:14:30

```


Copyright (C) 2021 Alan Yorinks. All Rights Reserved.