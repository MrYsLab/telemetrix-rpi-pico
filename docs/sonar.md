## set_pin_mode_sonar

```python
 def set_pin_mode_sonar(self, trigger_pin, echo_pin, callback=None)

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

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.