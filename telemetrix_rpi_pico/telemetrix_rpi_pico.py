"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,f
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import sys
import threading
import time
from collections import deque

import serial
# noinspection PyPackageRequirementscd
from serial.serialutil import SerialException
# noinspection PyPackageRequirements
from serial.tools import list_ports

# noinspection PyUnresolvedReferences
from telemetrix_rpi_pico.private_constants import PrivateConstants


# noinspection PyPep8,PyMethodMayBeStatic,GrazieInspection
class TelemetrixRpiPico(threading.Thread):
    """
    This class exposes and implements a Telemetrix type
    API for the Raspberry Pi Pico.
    It uses threading to accommodate concurrency.
    It includes the public API methods as well as
    a set of private methods.

    """

    def __init__(self, com_port=None, pico_instance_id=None,
                 sleep_tune=0.000001,
                 shutdown_on_exception=True,
                 reset_on_shutdown=True):

        """

        :param com_port: e.g. COM3 or /dev/ttyACM0.
                         Only use if you wish to bypass auto com port
                         detection.

        :param pico_instance_id: If not specified, than don't do id check.
                                 Else contains a board' s pico unique ID.
                                 This is passed as an array.

        :param sleep_tune: A tuning parameter (typically not changed by user)

        :param shutdown_on_exception: call shutdown before raising
                                      a RunTimeError exception, or
                                      receiving a KeyboardInterrupt exception

        :para reset_on_shutdown: Reset the board upon shutdown
        """

        # initialize threading parent
        threading.Thread.__init__(self)

        # create the threads and set them as daemons so
        # that they stop when the program is closed

        # create a thread to interpret received serial data
        self.the_reporter_thread = threading.Thread(target=self._reporter)
        self.the_reporter_thread.daemon = True

        self.the_data_receive_thread = threading.Thread(target=self._serial_receiver)

        # flag to allow the reporter and receive threads to run.
        self.run_event = threading.Event()

        # check to make sure that Python interpreter is version 3.7 or greater
        python_version = sys.version_info
        if python_version[0] >= 3:
            if python_version[1] >= 7:
                pass
            else:
                raise RuntimeError("ERROR: Python 3.7 or greater is "
                                   "required for use of this program.")

        # save input parameters as instance variables
        self.com_port = com_port
        self.pico_instance_id = pico_instance_id
        self.sleep_tune = sleep_tune
        self.shutdown_on_exception = shutdown_on_exception
        self.reset_on_shutdown = reset_on_shutdown

        # create a deque to receive and process data from the pico
        self.the_deque = deque()

        # The report_dispatch dictionary is used to process
        # incoming report messages by looking up the report message
        # and executing its associated processing method.

        self.report_dispatch = {}

        # To add a command to the command dispatch table, append here.
        self.report_dispatch.update(
            {PrivateConstants.LOOP_COMMAND: self._report_loop_data})
        self.report_dispatch.update(
            {PrivateConstants.DEBUG_PRINT: self._report_debug_data})
        self.report_dispatch.update(
            {PrivateConstants.DIGITAL_REPORT: self._digital_message})
        self.report_dispatch.update(
            {PrivateConstants.ANALOG_REPORT: self._analog_message})
        self.report_dispatch.update(
            {PrivateConstants.FIRMWARE_REPORT: self._firmware_message})
        self.report_dispatch.update(
            {PrivateConstants.UNIQUE_ID_REPORT: self._report_unique_id})
        self.report_dispatch.update(
            {PrivateConstants.SERVO_UNAVAILABLE: self._servo_unavailable})
        self.report_dispatch.update(
            {PrivateConstants.I2C_READ_REPORT: self._i2c_read_report})
        self.report_dispatch.update(
            {PrivateConstants.I2C_WRITE_FAILED: self._i2c_write_failed})
        self.report_dispatch.update(
            {PrivateConstants.I2C_READ_FAILED: self._i2c_read_failed})
        self.report_dispatch.update(
            {PrivateConstants.SONAR_DISTANCE: self._sonar_distance_report})
        self.report_dispatch.update({PrivateConstants.DHT_REPORT: self._dht_report})

        # up to 16 pwm pins may be simultaneously active
        self.pwm_active_count = 0

        # dictionaries to store the callbacks for each pin
        self.analog_callbacks = {}

        self.digital_callbacks = {}

        self.i2c_callback = None
        self.i2c_callback2 = None

        self.i2c_0_active = False
        self.i2c_1_active = False

        # the trigger pin will be the key to retrieve
        # the callback for a specific HC-SR04
        self.sonar_callbacks = {}

        self.sonar_count = 0

        self.dht_callbacks = {}

        self.dht_count = 0

        # serial port in use
        self.serial_port = None

        # flag to indicate we are in shutdown mode
        self.shutdown_flag = False

        # debug loopback callback method
        self.loop_back_callback = None

        # flag to indicate the start of a new report
        # self.new_report_start = True

        # firmware version to be stored here
        self.firmware_version = []

        # reported pico_id
        self.reported_pico_id = []

        # flag to indicate if i2c was previously enabled
        self.i2c_enabled = False

        # Create a dictionary to store the pins in use.
        # Notice that gpio pins 23, 24 and 25 are not included
        # because the Pico does not support these GPIOs.

        # This dictionary is a list of gpio pins updated with the pin mode when a pin mode
        # is set.
        # It is created initially using a dictionary comprehension.
        self.pico_pins = {gpio_pin: PrivateConstants.AT_MODE_NOT_SET for gpio_pin in
                          range(23)}

        # skip over unavailable pins
        for pin in range(25, 29):
            self.pico_pins[pin] = PrivateConstants.AT_MODE_NOT_SET

        # creating a list of available sda and scl pins for i2c. If assigned the pins
        # value will be set to either 0 or 1 depending upon the i2c selected.
        self.i2c_sda_pins = {n: 255 for n in range(2, 21, 2)}
        self.i2c_sda_pins[26] = 255

        self.i2c_scl_pins = {n: 255 for n in range(3, 22, 2)}
        self.i2c_scl_pins[27] = 255

        # create a dictionary that holds all the servo ranges
        self.servo_ranges = {gpio_pin: [1000, 2000] for gpio_pin in
                             range(23)}

        # skip over unavailable pins
        for gpio_pin in range(25, 29):
            self.servo_ranges[gpio_pin] = [1000, 2000]

        self.the_reporter_thread.start()
        self.the_data_receive_thread.start()

        # neopixel data
        self.number_of_pixels = None

        self.neopixels_initiated = False

        print(f"TelemetrixRpiPico:  Version {PrivateConstants.TELEMETRIX_VERSION}\n\n"
              f"Copyright (c) 2020 Alan Yorinks All Rights Reserved.\n")

        # using the serial link

        if not self.com_port:
            # user did not specify a com_port
            try:
                self._find_pico()
            except KeyboardInterrupt:
                if self.shutdown_on_exception:
                    self.shutdown()
        else:
            # com_port specified - set com_port and baud rate
            try:
                self._manual_open()
            except KeyboardInterrupt:
                if self.shutdown_on_exception:
                    self.shutdown()

        if self.serial_port:
            print(
                f"Serial compatible device found and connected to"
                f" {self.serial_port.port}")

            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

        # no com_port found - raise a runtime exception
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('No pico Found or User Aborted Program')

        # allow the threads to run
        self._run_threads()

        print('Retrieving pico ID...')
        self._get_pico_id()
        # time.sleep(.2)
        print(f'Pico Unique ID: {self.reported_pico_id}')

        if self.pico_instance_id:
            if self.reported_pico_id != self.pico_instance_id:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(f'Incorrect pico ID: {self.reported_pico_id}')
            else:
                print('Valid pico ID Found.')
        # get pico firmware version and print it
        print('\nRetrieving Telemetrix4pico firmware ID...')
        self._get_firmware_version()
        # time.sleep(.3)
        if not self.firmware_version:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'Telemetrix4pico firmware version')

        else:
            print(f'Telemetrix4pico firmware version: {self.firmware_version[0]}.'
                  f'{self.firmware_version[1]}')
        command = [PrivateConstants.ENABLE_ALL_REPORTS]
        self._send_command(command)

        # Have the server reset its data structures
        command = [PrivateConstants.RESET_DATA]
        self._send_command(command)

    def _find_pico(self):
        """
        This method will search all potential serial ports for a pico
        board using its USB PID and VID.
        """

        # a list of serial ports to be checked
        serial_ports = []

        print('Opening all potential serial ports...')
        the_ports_list = list_ports.comports()
        for port in the_ports_list:
            if port.pid is None:
                continue
            if port.pid != 10 or port.vid != 11914:
                continue
            try:
                self.serial_port = serial.Serial(port.device, 115200,
                                                 timeout=1, writeTimeout=0)
            except SerialException:
                continue
            # create a list of serial ports that we opened
            # make sure this is a pico board
            if port.pid == 10 and port.vid == 11914:
                serial_ports.append(self.serial_port)

                # display to the user
                print('\t' + port.device)

                # clear out the serial buffers
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()

    def _manual_open(self):
        """
        Com port was specified by the user - try to open up that port

        """
        # if port is not found, a serial exception will be thrown
        try:
            print(f'Opening {self.com_port}...')
            self.serial_port = serial.Serial(self.com_port, 115200,
                                             timeout=1, writeTimeout=0)

            self._run_threads()
            # time.sleep(self.pico_wait)

            self._get_pico_id()
            if self.pico_instance_id:
                if self.reported_pico_id != self.pico_instance_id:
                    if self.shutdown_on_exception:
                        self.shutdown()
                    raise RuntimeError(f'Incorrect pico ID: {self.reported_pico_id}')
            print('Valid pico ID Found.')
            # get pico firmware version and print it
            print('\nRetrieving Telemetrix4pico firmware ID...')
            self._get_firmware_version()

            if not self.firmware_version:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(f'Telemetrix4pico Sketch Firmware Version Not Found')

            else:
                print(f'Telemetrix4pico firmware version: {self.firmware_version[0]}.'
                      f'{self.firmware_version[1]}')
        except KeyboardInterrupt:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('User Hit Control-C')

    def pwm_write(self, pin, duty_cycle=0, raw=False):
        """
        Set the specified pin to the specified value.

        :param pin: pico GPIO pin number

        :param duty_cycle: if the raw parameter is False, then this is expressed
                           as a percentage between 0 and 100

                           if the raw parameter is True, then the valid range
                           of values is from 0 - 19999

       :param raw: Sets how the duty-cycle parameter is perceived.

        """
        if self.pico_pins[pin] != PrivateConstants.AT_PWM_OUTPUT \
                and self.pico_pins[pin] != PrivateConstants.AT_SERVO:
            raise RuntimeError('pwm_write: You must set the pin mode before performing '
                               'a PWM write.')
        if raw:
            if not (0 <= duty_cycle < PrivateConstants.MAX_RAW_DUTY_CYCLE):
                raise RuntimeError('Raw PWM duty cycle out of range')
            # else:
            #     dc = duty_cycle
        else:
            if not (0 <= duty_cycle <= 99):
                raise RuntimeError('Raw PWM duty cycle percentage of range')
            # calculate percentage of duty cycle
            else:
                duty_cycle = ((PrivateConstants.MAX_RAW_DUTY_CYCLE * duty_cycle) // 100)
                # print(duty_cycle)

        value_msb = duty_cycle >> 8
        value_lsb = duty_cycle & 0x00ff

        command = [PrivateConstants.PWM_WRITE, pin, value_msb, value_lsb]
        self._send_command(command)

    def digital_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: pico GPIO pin number

        :param value: pin value (1 or 0)

        """
        if self.pico_pins[pin] != PrivateConstants.AT_OUTPUT:
            raise RuntimeError('pwm_write: You must set the pin mode before performing '
                               'a digital write.')
        command = [PrivateConstants.DIGITAL_WRITE, pin, value]
        self._send_command(command)

    def disable_all_reporting(self):
        """
        Disable reporting for all digital and analog input pins
        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DISABLE_ALL, 0]
        self._send_command(command)

    def disable_analog_reporting(self, pin):
        """
        Disables analog reporting for a single analog pin.

        :param pin: Analog pin number. For example for ADC, the number is 0.

        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_ANALOG_DISABLE, pin]
        self._send_command(command)

    def disable_digital_reporting(self, pin):
        """
        Disables digital reporting for a single digital input.

        :param pin: GPIO Pin number.

        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DIGITAL_DISABLE, pin]
        self._send_command(command)

    def enable_analog_reporting(self, pin):
        """
        Enables analog reporting for the specified pin.

        :param pin: Analog pin number. For example for ADC0, the number is 0.


        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_ANALOG_ENABLE, pin]
        self._send_command(command)

    def enable_digital_reporting(self, pin):
        """
        Enable reporting on the specified digital pin.

        :param pin: GPIO Pin number.
        """

        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DIGITAL_ENABLE, pin]
        self._send_command(command)

    def _get_pico_id(self):
        """
        Retrieve pico-telemetrix pico id

        """
        command = [PrivateConstants.RETRIEVE_PICO_UNIQUE_ID]
        self._send_command(command)
        # provide time for the reply
        time.sleep(.5)

    def _get_firmware_version(self):
        """
        This method retrieves the
        pico-telemetrix firmware version

        """
        command = [PrivateConstants.GET_FIRMWARE_VERSION]
        self._send_command(command)
        # provide time for the reply
        time.sleep(.5)

    # TBD
    def i2c_read(self, address, register, number_of_bytes,
                 callback=None, i2c_port=0, no_stop=False):
        """
        Read the specified number of bytes from the specified register for
        the i2c device.


        :param address: i2c device address

        :param register: i2c register (or None if no register selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report i2c data as a
                   result of read command

       :param i2c_port: 0 = port 0, 1 = port 1

       :param no_stop: If true, master retains control of the bus at the end of the
                       transfer (no Stop is issued), and the next transfer will
                       begin with a Restart rather than a Start.


        callback returns a data list:
        [I2C_READ_REPORT, i2c_port, i2c_device_address, count of data bytes,
        data bytes,
        time-stamp]

        I2C_READ_REPORT = 10

        """

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('I2C Read: A callback function must be specified.')

        # i2c_port = 0 for port 0
        if i2c_port == 0:
            if not self.i2c_0_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode_i2c never called for i2c port 0.')
            else:
                self.i2c_callback = callback

        else:
            if not i2c_port == 1:
                if not self.i2c_0_active:
                    if self.shutdown_on_exception:
                        self.shutdown()
                    raise RuntimeError(
                        'I2C Write: set_pin_mode_i2c never called for i2c port 1.')
                else:
                    self.i2c_callback2 = callback

        command = [PrivateConstants.I2C_READ, i2c_port, address, register,
                   number_of_bytes, no_stop]

        # no register specified
        if not register:
            command[3] = PrivateConstants.I2C_NO_REGISTER

        self._send_command(command)

    # TBD
    def i2c_write(self, address, args, i2c_port=0, no_stop=False):
        """
        Write data to an i2c device.

        :param address: i2c device address

        :param args: A variable number of bytes to be sent to the device
                     passed in as a list.
                     NOTE: THIS MUST BE IN THE FORM OF A LIST.

        :param i2c_port: 0= port 0, 1 = port 1

        :param no_stop: If true, master retains control of the bus at the end of the
                       transfer (no Stop is issued), and the next transfer will
                       begin with a Restart rather than a Start.

        """
        if not i2c_port:
            if not self.i2c_0_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode i2c never called for i2c port 0.')

        elif i2c_port:
            if not self.i2c_1_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode i2c never called for i2c port 2.')

        command = [PrivateConstants.I2C_WRITE, i2c_port, address, len(args), no_stop]

        for item in args:
            command.append(item)

        self._send_command(command)

    def neo_pixel_set_value(self, pixel_number, r=0, g=0, b=0, auto_show=False):
        """
        Set the selected pixel in the pixel array on the Pico to
        the value provided.

        :param pixel_number: pixel number

        :param r: red value 0-255

        :param g: green value 0-255

        :param b: blue value 0-255

        :param auto_show: call show automatically

        """
        if not self.neopixels_initiated:
            raise RuntimeError('You must call set_pin_mode_neopixel first')

        if pixel_number > self.number_of_pixels:
            raise RuntimeError('Pixel number is out of legal range')

        if r and g and b not in range(256):
            raise RuntimeError('Pixel value must be in the range of 0-255')

        command = [PrivateConstants.SET_NEO_PIXEL, pixel_number, r, g, b, auto_show]
        self._send_command(command)

        if auto_show:
            self.neopixel_show()

    def neopixel_clear(self, auto_show=True):
        """
        Clear all pixels

        :param auto_show: call show automatically

        """
        if not self.neopixels_initiated:
            raise RuntimeError('You must call set_pin_mode_neopixel first')
        command = [PrivateConstants.CLEAR_ALL_NEO_PIXELS, auto_show]
        self._send_command(command)
        if auto_show:
            self.neopixel_show()

    def neopixel_fill(self, r=0, g=0, b=0, auto_show=True):
        """
        Fill all pixels with specified value

        :param r: 0-255

        :param g: 0-255

        :param b: 0-255

        :param auto_show: call show automatically
        """
        if not self.neopixels_initiated:
            raise RuntimeError('You must call set_pin_mode_neopixel first')
        if r and g and b not in range(256):
            raise RuntimeError('Pixel value must be in the range of 0-255')
        command = [PrivateConstants.FILL_ALL_NEO_PIXELS, r, g, b, auto_show]
        self._send_command(command)

        if auto_show:
            self.neopixel_show()

    def neopixel_show(self):
        """
        Write the NeoPixel buffer stored in the Pico to the NeoPixel strip.

        """
        if not self.neopixels_initiated:
            raise RuntimeError('You must call set_pin_mode_neopixel first')
        command = [PrivateConstants.SHOW_NEO_PIXELS]
        self._send_command(command)

    def loop_back(self, start_character, callback=None):
        """
        This is a debugging method to send a character to the
        pico device, and have the device loop it back.

        :param start_character: The character to loop back. It should be
                                an integer.

        :param callback: Looped back character will appear in the callback method

        """
        command = [PrivateConstants.LOOP_COMMAND, ord(start_character)]
        self.loop_back_callback = callback
        self._send_command(command)

    def set_pin_mode_analog_input(self, adc_number, differential=0, callback=None):
        """
        Set a pin as an analog input.

        :param adc_number: ADC Number 0-3 - ADC 3 is the temp sensor

        :param differential: difference in previous to current value before
                             report will be generated

        :param callback: callback function


        callback returns a data list:

        [ANALOG_REPORT, pin_number, pin_value, raw_time_stamp]

        The ANALOG_REPORT  = 3

        """
        # make sure adc number is in range
        if not 0 < adc_number < 5:
            raise RuntimeError('Invalid ADC Number')
        self._set_pin_mode(adc_number, PrivateConstants.AT_ANALOG, differential,
                           callback=callback)

    def set_pin_mode_digital_input(self, pin_number, callback=None):
        """
        Set a pin as a digital input.

        :param pin_number: pico GPIO pin number

        :param callback: callback function


        callback returns a data list:

        [DIGITAL_REPORT, pin_number, pin_value, raw_time_stamp]

        DIGITAL_REPORT = 2

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT, callback=callback)

    def set_pin_mode_digital_input_pullup(self, pin_number, callback=None):
        """
        Set a pin as a digital input with pullup enabled.

        :param pin_number: pico GPIO pin number

        :param callback: callback function


        callback returns a data list:

        [DIGITAL_REPORT, pin_number, pin_value, raw_time_stamp]

        The DIGITAL_REPORT = 2

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT_PULLUP,
                           callback=callback)

    def set_pin_mode_digital_input_pull_down(self, pin_number, callback=None):
        """
        Set a pin as a digital input with pull down enabled.

        :param pin_number: pico GPIO pin number

        :param callback: callback function


        callback returns a data list:

        [DIGITAL_REPORT, pin_number, pin_value, raw_time_stamp]

        DIGITAL_REPORT= 2

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT_PULL_DOWN,
                           callback=callback)

    def set_pin_mode_digital_output(self, pin_number):
        """
        Set a pin as a digital output pin.

        :param pin_number: pico GPIO pin number
        """

        self._set_pin_mode(pin_number, PrivateConstants.AT_OUTPUT)

    def set_pin_mode_neopixel(self, pin_number=28, num_pixels=8,
                              fill_r=0, fill_g=0, fill_b=0):
        """
        Initialize the pico for NeoPixel control. Fill with rgb values specified.

        Default: Set all the pixels to off.

        :param pin_number: neopixel GPIO control pin

        :param num_pixels: number of pixels in the strip

        :param fill_r: initial red fill value 0-255

        :param fill_g: initial green fill value 0-255

        :param fill_b: initial blue fill value 0-255


        """
        if fill_r or fill_g or fill_g not in range(256):
            raise RuntimeError('Pixel value must be in the range of 0-255')

        self.number_of_pixels = num_pixels

        command = [PrivateConstants.INITIALIZE_NEO_PIXELS, pin_number,
                   self.number_of_pixels, fill_r, fill_g, fill_b]

        self._send_command(command)

        self.pico_pins[pin_number] = PrivateConstants.AT_NEO_PIXEL

        self.neopixels_initiated = True

    def set_pin_mode_pwm_output(self, pin_number):
        """
        Enable a pin as a PWM pin. Maximum number of PWMs is 16.
        The frequency is fixed at 50 hz.

        Note: There are up to 16 pins that can be assigned as
        PWM. Servo pins share the 16 PWM pins.


        :param pin_number: pico GPIO pin number

        """

        if pin_number in self.pico_pins:
            self.pico_pins[pin_number] = PrivateConstants.AT_PWM_OUTPUT
            if self.pwm_active_count >= 15:
                raise RuntimeError(
                    'pwm or servo set mode: number of active PWM pins is at maximum')

            self.pwm_active_count += 1

            self._set_pin_mode(pin_number, PrivateConstants.AT_PWM_OUTPUT)
        else:
            raise RuntimeError('Gpio Pin Number is invalid')

    def set_pin_mode_i2c(self, i2c_port=0, sda_gpio=4, scl_gpio=5):
        """
        Establish the standard pico i2c pins for i2c utilization.

        :param i2c_port: 0 = i2c0, 1 = i2c1

        :param sda_gpio: gpio pin assigned to SDA

        :param scl_gpio: gpio pin assigned to SCL


        NOTES:
               1. THIS METHOD MUST BE CALLED BEFORE ANY I2C REQUEST IS MADE <br>
               2. Callbacks are set within the individual i2c read methods of this
              API.

              See i2c_read, and i2c_write

        """
        # determine if the i2c port is specified correctly
        if i2c_port not in [0, 1]:
            raise RuntimeError('i2c port must be either a 0 or 1')
        # determine if the sda and scl gpio's are valid
        if sda_gpio not in self.i2c_sda_pins:
            raise RuntimeError(f'GPIO {sda_gpio} is an invalid i2c SDA GPIO')
        if scl_gpio not in self.i2c_scl_pins:
            raise RuntimeError(f'GPIO {scl_gpio} is an invalid i2c SCL GPIO')

        # are both GPIOs available?
        if not self.i2c_sda_pins[sda_gpio] == 255:
            raise RuntimeError(f'GPIO SDA pin {sda_gpio} is already in use.')
        if not self.i2c_scl_pins[scl_gpio] == 255:
            raise RuntimeError(f'GPIO SCL pin {scl_gpio} is already in use.')
        # both pins available - mark the sda and scl dictionaries appropriately
        self.i2c_sda_pins[sda_gpio] = self.i2c_scl_pins[scl_gpio] = i2c_port

        # now mark the pico_pins dictionary for these pins
        self.pico_pins[sda_gpio] = self.pico_pins[scl_gpio] = PrivateConstants.AT_I2C

        # determine if the specified sda or scl pin has already been
        # assigned.

        # test for i2c port 0
        if not i2c_port:
            self.i2c_0_active = True
        # port 1
        else:
            self.i2c_1_active = True

        command = [PrivateConstants.I2C_BEGIN, i2c_port, sda_gpio, scl_gpio]
        self._send_command(command)

    def set_pin_mode_dht(self, pin, callback=None):
        """
    
      :param pin: connection pin

      :param callback: callback function

      callback returns a data list:

    DHT REPORT, DHT_DATA=1, PIN, Humidity,  Temperature (c),Time]

    DHT_REPORT =  12

        """

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('set_pin_mode_dht: A Callback must be specified')

        if self.dht_count < PrivateConstants.MAX_DHTS:
            self.dht_callbacks[pin] = callback
            self.dht_count += 1
            self.pico_pins[pin] = PrivateConstants.AT_DHT
            command = [PrivateConstants.DHT_NEW, pin]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(
                f'Maximum Number Of DHTs Exceeded - set_pin_mode_dht fails for pin {pin}')

    # noinspection PyRedundantParentheses
    def set_pin_mode_servo(self, pin_number, min_pulse=1000, max_pulse=2000):
        """

        Attach a pin to a servo motor

        Servo mode is a specialized version of PWM Output mode.
        There are 16 PWM pins shared between the Servo and PWM Output modes.

        :param pin_number: pin

        :param min_pulse: minimum pulse width in microseconds

        :param max_pulse: maximum pulse width in microseconds

        """

        self._set_pin_mode(pin_number, PrivateConstants.AT_SERVO, min_pulse, max_pulse)
        self.pico_pins[pin_number] = PrivateConstants.AT_SERVO

    def servo_write(self, pin_number, value):
        """
        Write the value to the specified servo

        :param pin_number: GPIO pin number

        :param value: value between 0 and 180

        """

        if self.pico_pins[pin_number] != PrivateConstants.AT_SERVO:
            raise RuntimeError('You must call set_pin_mode_servo before trying to '
                               'write a value to a servo or servo was detached.')

        # get the min and max for the servo and calculate the duty-cycle
        min_duty = self.servo_ranges[pin_number][PrivateConstants.MIN_SERVO_DUTY_CYCLE]
        max_duty = self.servo_ranges[pin_number][PrivateConstants.MAX_SERVO_DUTY_CYCLE]

        servo_range = max_duty - min_duty

        duty_cycle = int(value / 180 * servo_range) + min_duty

        # use a raw pwm write from the calculated values
        self.pwm_write(pin_number, duty_cycle, True)

    def set_pin_mode_sonar(self, trigger_pin, echo_pin, callback=None):
        """
        :param trigger_pin:  Sensor trigger gpio pin

        :param echo_pin: Sensor echo gpio pin

        :param callback: callback

       callback returns a data list:

       [ SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]

       SONAR_DISTANCE =  11

        """

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('set_pin_mode_sonar: A Callback must be specified')

        if self.sonar_count < PrivateConstants.MAX_SONARS:
            self.sonar_callbacks[trigger_pin] = callback
            self.sonar_count += 1
            self.pico_pins[trigger_pin] = self.pico_pins[echo_pin] = \
                PrivateConstants.AT_SONAR

            command = [PrivateConstants.SONAR_NEW, trigger_pin, echo_pin]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('Maximum number of supported sonar devices exceeded.')

    def get_pico_pins(self):
        """
        This method returns the pico_pins dictionary

        Pin Modes MAP:

            DIGITAL_INPUT = 0

            DIGITAL_OUTPUT = 1

            PWM_OUTPUT = 2

            DIGITAL_INPUT_PULLUP = 3

            DIGITAL_INPUT_PULL_DOWN = 4

            ANALOG_INPUT = 5

            SERVO = 6

            SONAR = 7

            DHT = 8

            I2C = 9

            NEO_PIXEL = 10

            AT_MODE_NOT_SET = 255

        :return: pico_pins
        """
        return self.pico_pins

    def _set_pin_mode(self, pin_number, pin_state, differential=0, value_range=0,
                      callback=None):

        """
        A private method to set the various pin modes.

        :param pin_number: pico pin number

        :param pin_state: INPUT/OUTPUT/ANALOG/PWM/PULLUP

        :param differential: for analog inputs - threshold
                             value to be achieved for report to
                             be generated

                           : for servo we overload this variable to mean the minimum
                             duty cycle

        :param value_range: for servo this is the maximum duty cycle

        :param callback: A reference to a call back function to be
                         called when pin data value changes

        """
        # Map ADC to GPIO pin numbers
        if pin_state == PrivateConstants.AT_ANALOG:
            self.pico_pins[26 + pin_number] = PrivateConstants.AT_ANALOG
        else:
            if pin_number in self.pico_pins:
                self.pico_pins[pin_number] = pin_state
            else:
                raise RuntimeError('Gpio Pin Number is invalid')

        if callback:
            if pin_state == PrivateConstants.AT_INPUT:
                self.digital_callbacks[pin_number] = callback
            elif pin_state == PrivateConstants.AT_INPUT_PULLUP:
                self.digital_callbacks[pin_number] = callback
            elif pin_state == PrivateConstants.AT_INPUT_PULL_DOWN:
                self.digital_callbacks[pin_number] = callback
            elif pin_state == PrivateConstants.AT_ANALOG:
                self.analog_callbacks[pin_number] = callback

            else:
                print('{} {}'.format('set_pin_mode: callback ignored for '
                                     'pin state:', pin_state))

        if pin_state == PrivateConstants.AT_INPUT:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_INPUT, 1]

        elif pin_state == PrivateConstants.AT_INPUT_PULLUP:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_INPUT_PULLUP, 1]

        elif pin_state == PrivateConstants.AT_INPUT_PULL_DOWN:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_INPUT_PULL_DOWN, 1]

        elif pin_state == PrivateConstants.AT_OUTPUT:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_OUTPUT]

        elif pin_state == PrivateConstants.AT_ANALOG:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_ANALOG,
                       differential >> 8, differential & 0xff, 1]

        elif pin_state == PrivateConstants.AT_PWM_OUTPUT:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_PWM_OUTPUT]

        elif pin_state == PrivateConstants.AT_SERVO:
            # we reuse the PWM_OUTPUT command
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_PWM_OUTPUT]
            self.servo_ranges[pin_number] = [differential, value_range]

        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('Unknown pin state')

        if pin_state == PrivateConstants.AT_ANALOG:
            if pin_number == 0:
                self.pico_pins[26] = PrivateConstants.AT_ANALOG
            elif pin_number == 1:
                self.pico_pins[27] = PrivateConstants.AT_ANALOG
            elif pin_number == 13:
                self.pico_pins[28] = PrivateConstants.AT_ANALOG

        else:
            self.pico_pins[pin_number] = pin_state

        if command:
            self._send_command(command)

    def shutdown(self):
        """
        This method attempts an orderly shutdown
        If any exceptions are thrown, they are ignored.
        """
        self.shutdown_flag = True

        self._stop_threads()

        # try:
        command = [PrivateConstants.STOP_ALL_REPORTS]
        self._send_command(command)
        time.sleep(.2)
        if self.reset_on_shutdown:
            command = [PrivateConstants.RESET_BOARD]
            self._send_command(command)
            time.sleep(.2)

    '''
    report message handlers
    '''

    def _analog_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for analog messages.

        :param data: message data

        """
        pin = data[0]
        value = (data[1] << 8) + data[2]
        # set the current value in the pin structure
        time_stamp = time.time()
        # self.digital_pins[pin].event_time = time_stamp
        if self.analog_callbacks[pin]:
            message = [PrivateConstants.ANALOG_REPORT, pin, value, time_stamp]
            self.analog_callbacks[pin](message)

    # TBD
    def _dht_report(self, data):
        """
        This is the dht report handler method.

        :param data:

                                data[0] = report sub type - DHT_REPORT

                                data[1] = pin number

                                data[2] = humidity

                                data[3] = temperature

                                data[4] = timestamp


        """
        cb = self.dht_callbacks[data[0]]

        cb_list = [PrivateConstants.DHT_REPORT, data[0],
                   (data[1] + (data[2] / 100)), (data[3] + (data[4] / 100)), time.time()]
        cb(cb_list)

    def _digital_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for Digital Messages.

        :param data: digital message

        """
        pin = data[0]
        value = data[1]

        time_stamp = time.time()
        if self.digital_callbacks[pin]:
            message = [PrivateConstants.DIGITAL_REPORT, pin, value, time_stamp]
            self.digital_callbacks[pin](message)

    def _firmware_message(self, data):
        """
        Telemetrix4pico firmware version message
        :param data: data[0] = major number, data[1] = minor number
        """

        self.firmware_version = [data[0], data[1]]

    # TBD
    def _i2c_read_report(self, data):
        """
        Execute callback for i2c reads.

        :param data: [I2C_READ_REPORT, i2c_port, i2c_address,
        register, number of bytes read, bytes read..., time-stamp]
        """

        cb_list = [PrivateConstants.I2C_READ_REPORT, data[0], data[1]] + data[2:]

        cb_list.append(time.time())

        if cb_list[1]:
            self.i2c_callback2(cb_list)
        else:
            self.i2c_callback(cb_list)

    def _i2c_write_failed(self, data):
        """
        I2c write attempt failed

        :param data: data[0] = i2c_device
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'i2c Write Failed for I2C port {data[0]}')
        while True:
            time.sleep(1)

    def _i2c_read_failed(self, data):
        """
        I2c read failed

        :param data: data[0] = i2c device
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'i2c Read Failed for I2C port {data[0]}')
        while True:
            time.sleep(.1)

    def _report_unique_id(self, data):
        """
        Reply to are_u_there message
        :param data: pico id
        """

        for i in range(len(data)):
            self.reported_pico_id.append(data[i])

    def _report_debug_data(self, data):
        """
        Print debug data sent from pico
        :param data: data[0] is a byte followed by 2
                     bytes that comprise an integer
        :return:
        """
        value = (data[1] << 8) + data[2]
        print(f'DEBUG ID: {data[0]} Value: {value}')

    def _report_loop_data(self, data):
        """
        Print data that was looped back
        :param data: byte of loop back data
        :return:
        """
        if self.loop_back_callback:
            self.loop_back_callback(data)

    def _send_command(self, command):
        """
        This is a private utility method.


        :param command:  command data in the form of a list

        """
        # the length of the list is added at the head
        command.insert(0, len(command))
        # print(command)
        send_message = bytes(command)

        if self.serial_port:
            try:
                self.serial_port.write(send_message)
            except SerialException:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('write fail in _send_command')

    # TBD
    def _servo_unavailable(self, report):
        """
        Message if no servos are available for use.
        :param report: pin number
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'Servo Attach For Pin {report[0]} Failed: No Available Servos')

    def _sonar_distance_report(self, report):
        """

        :param report: data[0] = trigger pin, data[1] and data[2] = distance

        callback report format: [PrivateConstants.SONAR_DISTANCE, trigger_pin,
        distance  in centimeters, time_stamp]
        """

        # get callback from pin number
        cb = self.sonar_callbacks[report[0]]

        # build report data
        if report[1] == 0 and report[2] == 0:
            cb_list = [PrivateConstants.SONAR_DISTANCE, report[0],
                       0, time.time()]
        else:
            cb_list = [PrivateConstants.SONAR_DISTANCE, report[0],
                       (report[1] + (report[2] / 100)), time.time()]

        cb(cb_list)

    def _run_threads(self):
        self.run_event.set()

    def _is_running(self):
        return self.run_event.is_set()

    def _stop_threads(self):
        self.run_event.clear()

    def _reporter(self):
        """
        This is the reporter thread. It continuously pulls data from
        the deque. When a full message is detected, that message is
        processed.
        """
        self.run_event.wait()

        while self._is_running() and not self.shutdown_flag:
            if len(self.the_deque):
                # response_data will be populated with the received data for the report
                response_data = []
                packet_length = self.the_deque.popleft()

                if packet_length:
                    # get all the data for the report and place it into response_data
                    for i in range(packet_length):
                        while not len(self.the_deque):
                            time.sleep(self.sleep_tune)
                        data = self.the_deque.popleft()
                        response_data.append(data)

                    # get the report type and look up its dispatch method
                    # here we pop the report type off of response_data
                    report_type = response_data.pop(0)

                    # retrieve the report handler from the dispatch table
                    dispatch_entry = self.report_dispatch.get(report_type)

                    # if there is additional data for the report,
                    # it will be contained in response_data
                    # noinspection PyArgumentList
                    dispatch_entry(response_data)
                    continue

                else:
                    if self.shutdown_on_exception:
                        self.shutdown()
                    raise RuntimeError(
                        'A report with a packet length of zero was received.')
            else:
                time.sleep(self.sleep_tune)

    def _serial_receiver(self):
        """
        Thread to continuously check for incoming data.
        When a byte comes in, place it onto the deque.
        """
        self.run_event.wait()

        while self._is_running() and not self.shutdown_flag:
            # we can get an OSError: [Errno9] Bad file descriptor when shutting down
            # just ignore it
            try:
                if self.serial_port.inWaiting():
                    c = self.serial_port.read()
                    self.the_deque.append(ord(c))
                else:
                    time.sleep(self.sleep_tune)
                    # continue
            except OSError:
                pass
