## set_pin_mode_dht
```python
 def set_pin_mode_dht(self, pin, callback=None)

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

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.