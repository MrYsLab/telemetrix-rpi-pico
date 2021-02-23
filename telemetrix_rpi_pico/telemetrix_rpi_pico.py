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
import struct
import sys
import threading
import time
from collections import deque

import serial
# noinspection PyPackageRequirementscd
from serial.serialutil import SerialException
# noinspection PyPackageRequirements
from serial.tools import list_ports

from telemetrix_rpi_pico.private_constants import PrivateConstants


# noinspection PyPep8,PyMethodMayBeStatic
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
        self.report_dispatch.update({PrivateConstants.UNIQUE_ID_REPORT: self._report_unique_id})
        self.report_dispatch.update(
            {PrivateConstants.SERVO_UNAVAILABLE: self._servo_unavailable})
        self.report_dispatch.update(
            {PrivateConstants.I2C_READ_REPORT: self._i2c_read_report})
        self.report_dispatch.update(
            {PrivateConstants.I2C_TOO_FEW_BYTES_RCVD: self._i2c_too_few})
        self.report_dispatch.update(
            {PrivateConstants.I2C_TOO_MANY_BYTES_RCVD: self._i2c_too_many})
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

        self.i2c_1_active = False
        self.i2c_2_active = False

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

        self.the_reporter_thread.start()
        self.the_data_receive_thread.start()

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

    def pwm_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: pico pin number

        :param value: pin value (0-255)

        """
        value_msb = value >> 8
        value_lsb = value & 0xff
        command = [PrivateConstants.PWM_WRITE, pin, value_msb, value_lsb]
        self._send_command(command)

    def digital_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: pico pin number

        :param value: pin value (1 or 0)

        """

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

        :param pin: Analog pin number. For example for A0, the number is 0.

        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_ANALOG_DISABLE, pin]
        self._send_command(command)

    def disable_digital_reporting(self, pin):
        """
        Disables digital reporting for a single digital input.

        :param pin: Pin number.

        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DIGITAL_DISABLE, pin]
        self._send_command(command)

    def enable_analog_reporting(self, pin):
        """
        Enables analog reporting for the specified pin.

        :param pin: Analog pin number. For example for A0, the number is 0.


        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_ANALOG_ENABLE, pin]
        self._send_command(command)

    def enable_digital_reporting(self, pin):
        """
        Enable reporting on the specified digital pin.

        :param pin: Pin number.
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
                 callback=None, i2c_port=0):
        """
        NOT YET IMPLEMENTED!!!

        Read the specified number of bytes from the specified register for
        the i2c device.


        :param address: i2c device address

        :param register: i2c register (or None if no register selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report i2c data as a
                   result of read command

       :param i2c_port: 0 = default, 1 = secondary


        callback returns a data list:
        [I2C_READ_REPORT, address, register, count of data bytes, data bytes, time-stamp]

        """

        self._i2c_read_request(address, register, number_of_bytes,
                               callback=callback, i2c_port=i2c_port)

    # TBD
    def i2c_read_restart_transmission(self, address, register,
                                      number_of_bytes,
                                      callback=None, i2c_port=0):
        """
        NOT YET IMPLEMENTED!!!

        Read the specified number of bytes from the specified register for
        the i2c device. This restarts the transmission after the read. It is
        required for some i2c devices such as the MMA8452Q accelerometer.


        :param address: i2c device address

        :param register: i2c register (or None if no register
                                                    selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report i2c data as a
                   result of read command

       :param i2c_port: 0 = default 1 = secondary


        callback returns a data list:

        [I2C_READ_REPORT, address, register, count of data bytes, data bytes, time-stamp]

        """

        self._i2c_read_request(address, register, number_of_bytes,
                               stop_transmission=False,
                               callback=callback, i2c_port=i2c_port)

    # TBD
    def _i2c_read_request(self, address, register, number_of_bytes,
                          stop_transmission=True, callback=None, i2c_port=0):
        """
        NOT YET IMPLEMENTED!!!

        This method requests the read of an i2c device. Results are retrieved
        via callback.

        :param address: i2c device address

        :param register: register number (or None if no register selection is needed)

        :param number_of_bytes: number of bytes expected to be returned

        :param stop_transmission: stop transmission after read

        :param callback: Required callback function to report i2c data as a
                   result of read command.

        """
        if not i2c_port:
            if not self.i2c_1_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Read: set_pin_mode i2c never called for i2c port 1.')

        if i2c_port:
            if not self.i2c_2_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Read: set_pin_mode i2c never called for i2c port 2.')

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('I2C Read: A callback function must be specified.')

        if not i2c_port:
            self.i2c_callback = callback
        else:
            self.i2c_callback2 = callback

        if not register:
            register = 0

        # message contains:
        # 1. address
        # 2. register
        # 3. number of bytes
        # 4. restart_transmission - True or False
        # 5. i2c port

        command = [PrivateConstants.I2C_READ, address, register, number_of_bytes,
                   stop_transmission, i2c_port]
        self._send_command(command)

    # TBD
    def i2c_write(self, address, args, i2c_port=0):
        """
        NOT YET IMPLEMENTED!!!

        Write data to an i2c device.

        :param address: i2c device address

        :param i2c_port: 0= port 1, 1 = port 2

        :param args: A variable number of bytes to be sent to the device
                     passed in as a list

        """
        if not i2c_port:
            if not self.i2c_1_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode i2c never called for i2c port 1.')

        if i2c_port:
            if not self.i2c_2_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode i2c never called for i2c port 2.')

        command = [PrivateConstants.I2C_WRITE, len(args), address, i2c_port]

        for item in args:
            command.append(item)

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

    def set_pin_mode_analog_input(self, pin_number, differential=0, callback=None):
        """
        Set a pin as an analog input.

        :param pin_number: ADC Number 0-3 - ADC 3 is the temp sensor

        :param differential: difference in previous to current value before
                             report will be generated

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for analog input pins = 2

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_ANALOG, differential,
                           callback=callback)

    def set_pin_mode_digital_input(self, pin_number, callback=None):
        """
        Set a pin as a digital input.

        :param pin_number: pico pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for digital input pins = 0

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT, callback=callback)

    def set_pin_mode_digital_input_pullup(self, pin_number, callback=None):
        """
        Set a pin as a digital input with pullup enabled.

        :param pin_number: pico pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for digital input pins with pullups enabled = 11

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT_PULLUP,
                           callback=callback)

    def set_pin_mode_digital_input_pull_down(self, pin_number, callback=None):
        """
        Set a pin as a digital input with pull down enabled.

        :param pin_number: pico pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for digital input pins with pullups enabled = 11

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT_PULL_DOWN,
                           callback=callback)

    def set_pin_mode_digital_output(self, pin_number):
        """
        Set a pin as a digital output pin.

        :param pin_number: pico pin number
        """

        self._set_pin_mode(pin_number, PrivateConstants.AT_OUTPUT)

    def set_pin_mode_pwm_output(self, pin_number, value_range=255):
        """
        Enable a pin as a PWM pin. Maximum number of PWMs is 16.

        :param pin_number: pico pin number

        :param value_range: value range - 16 bits
        """

        if self.pwm_active_count >= 15:
            raise RuntimeError(
                'set_pin_mode_pwm_output: number of active PWM pins is at maximum')

        if value_range > 0xffff:
            raise RuntimeError(
                'set_pin_mode_pwm_output: value_range is limited to 16 bits')

        self.pwm_active_count += 1

        self._set_pin_mode(pin_number, PrivateConstants.AT_PWM_OUTPUT,
                           value_range=value_range)

    # TBD
    def set_pin_mode_i2c(self, i2c_port=0):
        """
        NOT YET IMPLEMENTED!!!

        Establish the standard pico i2c pins for i2c utilization.

        :param i2c_port: 0 = i2c1, 1 = i2c2

        NOTES: 1. THIS METHOD MUST BE CALLED BEFORE ANY I2C REQUEST IS MADE
               2. Callbacks are set within the individual i2c read methods of this
              API.

              See i2c_read, or i2c_read_restart_transmission.

        """
        # test for i2c port 2
        if i2c_port:
            # if not previously activated set it to activated
            # and the send a begin message for this port
            if not self.i2c_2_active:
                self.i2c_2_active = True
            else:
                return
        # port 1
        else:
            if not self.i2c_1_active:
                self.i2c_1_active = True
            else:
                return

        command = [PrivateConstants.I2C_BEGIN, i2c_port]
        self._send_command(command)

    # TBD
    def set_pin_mode_dht(self, pin, callback=None):
        """
        NOT YET IMPLEMENTED!!!

        :param pin: connection pin

        :param callback: callback function

        Error Callback: [Callback 0=DHT REPORT, DHT_ERROR=0, PIN, Error Number, Time]

        Valid Data Callback: Callback 0=DHT REPORT, DHT_DATA=1, PIN, Humidity, Temperature Time]

        """

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('set_pin_mode_dht: A Callback must be specified')

        if self.dht_count < PrivateConstants.MAX_DHTS - 1:
            self.dht_callbacks[pin] = callback
            self.dht_count += 1

            command = [PrivateConstants.DHT_NEW, pin]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(
                f'Maximum Number Of DHTs Exceeded - set_pin_mode_dht fails for pin {pin}')

    # TBD
    # noinspection PyRedundantParentheses
    def set_pin_mode_servo(self, pin_number, min_pulse=544, max_pulse=2400):
        """
        NOT YET IMPLEMENTED!!!

        Attach a pin to a servo motor

        :param pin_number: pin

        :param min_pulse: minimum pulse width

        :param max_pulse: maximum pulse width

        """
        minv = (min_pulse).to_bytes(2, byteorder="big")
        maxv = (max_pulse).to_bytes(2, byteorder="big")

        command = [PrivateConstants.SERVO_ATTACH, pin_number,
                   minv[0], minv[1], maxv[0], maxv[1]]
        self._send_command(command)

    # TBD
    def set_pin_mode_sonar(self, trigger_pin, echo_pin,
                           callback=None):
        """
        NOT YET IMPLEMENTED!!!

        :param trigger_pin:

        :param echo_pin:

        :param callback: callback

        callback data: [PrivateConstants.SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]

        """

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('set_pin_mode_sonar: A Callback must be specified')

        if self.sonar_count < PrivateConstants.MAX_SONARS - 1:
            self.sonar_callbacks[trigger_pin] = callback
            self.sonar_count += 1

            command = [PrivateConstants.SONAR_NEW, trigger_pin, echo_pin]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(
                f'Maximum Number Of Sonars Exceeded - set_pin_mode_sonar fails for pin {trigger_pin}')

    # TBD
    def servo_write(self, pin_number, angle):
        """
        NOT YET IMPLEMENTED!!!

        Set a servo attached to a pin to a given angle.

        :param pin_number: pin

        :param angle: angle (0-180)

        """
        command = [PrivateConstants.SERVO_WRITE, pin_number, angle]
        self._send_command(command)

    # TBD
    def servo_detach(self, pin_number):
        """
        NOT YET IMPLEMENTED!!!

        Detach a servo for reuse

        :param pin_number: attached pin

        """
        command = [PrivateConstants.SERVO_DETACH, pin_number]
        self._send_command(command)

    def _set_pin_mode(self, pin_number, pin_state, differential=0, value_range=0,
                      callback=None):

        """
        A private method to set the various pin modes.

        :param pin_number: pico pin number

        :param pin_state: INPUT/OUTPUT/ANALOG/PWM/PULLUP
                         For SERVO use: set_pin_mode_servo
                         For DHT   use: set_pin_mode_dht

        :param differential: for analog inputs - threshold
                             value to be achieved for report to
                             be generated

        :param value_range: valid value range

        :param callback: A reference to a call back function to be
                         called when pin data value changes

        """
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
                       PrivateConstants.AT_PWM_OUTPUT, value_range >> 8,
                       value_range & 0xff]

        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('Unknown pin state')

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

        :param data:            data[0] = report sub type - DHT_DATA or DHT_ERROR

                                data[1] = pin number

                                data[2] = humidity high order byte or error value if DHT_ERROR

                                data[3] = humidity byte 2

                                data[4] = humidity byte 3

                                data[5] = humidity byte 4

                                data[6] = temperature high order byte for data

                                data[7] = temperature byte 2

                                data[8] = temperature byte 3

                                data[9] = temperature byte 4
        """

        if data[0]:  # DHT_ERROR
            # error report
            # data[0] = report sub type, data[1] = pin, data[2] = error message
            if self.dht_callbacks[data[1]]:
                # Callback 0=DHT REPORT, DHT_ERROR=0, PIN, Error Number, Time
                message = [PrivateConstants.DHT_REPORT, data[0], data[1], data[2],
                           time.time()]
                self.dht_callbacks[data[1]](message)
        else:
            # got valid data DHT_DATA
            f_humidity = bytearray(data[2:6])
            f_temperature = bytearray(data[6:])
            message = [PrivateConstants.DHT_REPORT, data[0], data[1],
                       (struct.unpack('<f', f_humidity))[0],
                       (struct.unpack('<f', f_temperature))[0],
                       time.time()]

            self.dht_callbacks[data[1]](message)

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

        :param data: [I2C_READ_REPORT, i2c_port, number of bytes read, address, register, bytes read..., time-stamp]
        """

        # we receive [# data bytes, address, register, data bytes]
        # number of bytes of data returned

        # data[0] = number of bytes
        # data[1] = i2c_port
        # data[2] = number of bytes returned
        # data[3] = address
        # data[4] = register
        # data[5] ... all the data bytes

        cb_list = [PrivateConstants.I2C_READ_REPORT, data[0], data[1]] + data[2:]
        cb_list.append(time.time())

        if cb_list[1]:
            self.i2c_callback2(cb_list)
        else:
            self.i2c_callback(cb_list)

    # TBD
    def _i2c_too_few(self, data):
        """
        I2c reports too few bytes received

        :param data: data[0] = device address
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'i2c too few bytes received from i2c port {data[0]} i2c address {data[1]}')

    # TBD
    def _i2c_too_many(self, data):
        """
        I2c reports too few bytes received

        :param data: data[0] = device address
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'i2c too many bytes received from i2c port {data[0]} i2c address {data[1]}')

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

    # TBD
    def _sonar_distance_report(self, report):
        """

        :param report: data[0] = trigger pin, data[1] and data[2] = distance

        callback report format: [PrivateConstants.SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]
        """

        # get callback from pin number
        cb = self.sonar_callbacks[report[0]]

        # build report data
        cb_list = [PrivateConstants.SONAR_DISTANCE, report[0],
                   ((report[1] << 8) + report[2]), time.time()]

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

                    # print(response_data)

                    # get the report type and look up its dispatch method
                    # here we pop the report type off of response_data
                    report_type = response_data.pop(0)
                    # print(report_type)

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
