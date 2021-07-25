# This is a working branch to implement an SPI interface.
## An update log is below:

* July 21 2021
  * Created the spi branch.

* July 23 2021
  * Created stubs for the SPI methods. API can be viewed [here.](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix-rpi-pico/blob/spi/html/telemetrix_rpi_pico/index.html)
    * set_pin_mode spi
    * spi_read16_blocking
    * spi_read_blocking
    * spi_set_format
    * spi_write16_blocking
    * spi_write16_read16_blocking
    * spi_write_blocking
    * spi_write_read_blocking
    
* July 24 2021
    * Coded set_pin_mode_spi. Not yet tested.
    * Added message definitions for various SPI commands to private constants file.
    * Coded spi_read_blocking. Not yet tested.
    * Coded spi_write_blocking. Not yet tested.
    NOTE: I am going to code the pico side to test the new commands and return to code 
      the rest when I get basics working across the interface.
      
* July 25
    * Implemented read_blocking_spi method. Not yet tested.
    * Began to implement example to test with mpu9250. Not yet tested.
    * Seperated chip select and deselect as a seperate method from reads and writes.
  

# Telemetrix-RPi-Pico

Interact and monitor  a Raspberry  Pi Pico remotely  from your PC using Python.

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



