
# Telemetrix-RPi-Pico

Interact and monitor  a Raspberry  Pi Pico remotely  from your PC using Python.
It is similar to Arduino Firmata, but written specifically for the Raspberry Pi
Pico.

![](images/tmx.png)

A full User's Guide is [available online.](https://mryslab.github.io/telemetrix-rpi-pico/)

Python API documentation  may be found [here.](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix-rpi-pico/blob/master/html/telemetrix_rpi_pico/index.html) 

The Pico server code may be viewed [here.](https://github.com/MrYsLab/Telemetrix4RpiPico)

The following functionality is implemented in this release:

* Analog Input
* Digital Input, Digital Input Pullup, Digital Input Pulldown
* PWM output
* Loopback (for client/server link debugging)
* I2C Support
* SPI Support
* NeoPixel Support
* Servo Support
* HC-SR04 Type Sonar Distance Sensor Support
* DHT 11 and 22 Humidity/Temperature Sensor Support
* Autodetect PICO device over USB Serial.
* Automatic board reset of the PICO using the watchdog timer when application exits.
    * Board will blink twice upon reset.
* Retrieval of the PICO's unique ID.


## To install The Client Library:

**Linux/macOS:**

```bash
sudo pip3 install telemetrix-rpi-pico
```


**Windows:**


```bash
pip install telemetrix-rpi-pico 
```

### If you are upgrading from a previously installed version:

**Linux/macOS:**

```bash
sudo pip3 install telemetrix-rpi-pico --upgrade
```


**Windows:**


```bash
pip install telemetrix-rpi-pico --upgrade
```

## To Install The Pico Server Application
1. [Download](https://github.com/MrYsLab/Telemetrix4RpiPico/raw/master/cmake-build-release/Telemetrix4RpiPico.uf2) 
   and save the .uf2 file.
2. Place the Pico in file upload mode:
   
   A. Press and hold the BOOTSEL button while applying power. 
   
   B. Release the BOOTSEL button.
   
   C. In your file explorer, you should see a new folder appear called: RPI-RP2.
   
   D. Drag the .uf2 file into this folder to upload the code.

## Download And Run The Examples
   
1. [Download,](https://github.com/MrYsLab/telemetrix-rpi-pico/archive/master.zip) 
   save, and uncompress the teletmetrix-rpi-pico Github repository.
   
2. Open the _examples_ directory and run any of the examples. You may
modify them to suit your needs.



