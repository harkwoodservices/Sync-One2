#!/usr/bin/env python3
"""  
Starter code for using Sync-One2 v2 via it's API interface

Sync-One2 v2 Firmware v2.2.4 or above required for all commands to operate correctly

Dependant on PySerial 

Version 1.0.1   Fix an error in calibrate
Version 1.0.2   Fix an error in Custom Splsh 2 command

Copyright (c) 2022 Harkwood Services Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import serial
import time


class SyncOne2:
    """ Class to assist with using the Sync-One2 API with Python

        When using pass the serial port Sync-One2 is attached to, for example
            Sone2 = SyncOne2("COM3)
            Sone2 = SyncOne2("/dev/cu.usbmodem14201")

        Commands follow those of the Sync-One2 API manual
    """

    def __init__(self, serial_port):
        self.__serial_port = serial_port
        self.__in_API = False

    def __open_port(self):
        try:
            self.__com_port = serial.Serial(
                port=self.__serial_port, baudrate=115200, timeout=1, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False, dsrdtr=False)
        except serial.SerialException as error:            
            return (False)
        self.__com_port.reset_input_buffer()
        return (True)

    def __close_port(self):
        self.__com_port.close()
        return (None)

    def __get_reply(self):
        reply = self.__com_port.read_until(b'\r')
        reply = self.__parse_line(reply)
        return (reply)

    def __send_command(self, string):
        string = string + "\r"
        self.__com_port.write(string.encode())
        return (None)

    def __wait_for_string(self, string):
        reply = self.__com_port.read_until(b'\r')
        reply = self.__parse_line(reply)
        while string not in reply:
            reply = self.__com_port.read_until(b'\r')
            reply = self.__parse_line(reply)
            if not reply:
                return (False)
        return (True)

    def __parse_line(self, line_data):
        line_data = line_data.decode()
        line_data = line_data.replace('\r', '')
        return (line_data)

    def __commmand_and_reply(self, cmd_string):
        self.__send_command(cmd_string)
        reply = self.__get_reply()
        return (reply)

    def enter_API(self):
        """ Enter API mode

        Returns:
            bool : True for OK, False for error
        """
        # attempt to open the serial port
        if (self.__open_port()) == False:
            return (False)

        # Port opened OK, attempt to go into API mode
        self.__send_command("API")
        result = self.__wait_for_string("OK")
        if result:
            self.__in_API = True
        else:
            self.__in_API = False
        return (result)

    def audio_in(self):
        """ Returns the audio input setting

        Returns:
            Str:  Input source selected, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("AUDIO IN")
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def calibrate(self):
        """ Calibrates the sensors

        Returns:
            Str:  OK, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            # increase serial timeout to 10 seconds, to give time calibration to run
            self.__com_port.timeout = 10
            self.__send_command("CALIBRATE")
            reply = self.__wait_for_string("OK")
            # return serial timeout to  1 second
            self.__com_port.timeout = 1
            return ("OK", reply)
        else:
            return("ERR Not in API mode", False)

    def clear_stats(self):
        """ Clears the stats buffer

        Returns:
            Str:  OK, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            self.__send_command("CLEAR STATS")
            reply = self.__wait_for_string("OK")
            return ("OK", reply)
        else:
            return ("ERR Not in API mode", False)

    def custom_splash_1(self, message):
        """ Sets a custom splash message on display line 1

        Args:
            message (str): The message to be displayed, max 16 characters

        Returns:
            Str:  OK, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(f'CUSTOM SPLASH 1 "{message}" ')
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def custom_splash_2(self, message):
        """ Sets a custom splash message on display line 2

        Args:
            message (str): The message to be displayed, max 16 characters

        Returns:
            Str:  OK, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(f'CUSTOM SPLASH 2 "{message}" ')
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def exit_API(self):
        """ Exits from the API to measurement mode

        Returns:
            Str:  OK, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            self.__send_command("EXIT")
            self.__in_API = False
            reply = self.__wait_for_string("OK")
            self.__close_port()
            return ("OK", reply)
        else:
            return ("ERR Not in API mode", False)

    def extended_mode(self):
        """ Get the Extended Mode status

        Returns:
            Str:  Extended mode status, or ERR message
            Bool: True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("EXTENDED MODE")
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def frame_rate(self):
        """ Get the current frame rate

        Returns:
            int / str: frame rate as int / ERR message
            Bool:      True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("FRAME RATE")
            reply = int(reply)
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def mask_len(self):
        """ Get the current Mask Length

        Returns:
            int / str: Mask time as int / ERR message
            Bool:      True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("MASK LEN")
            reply = int(reply)
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def offset(self):
        """ Get the current Offset

        Returns:
            int / str: offset as int / ERR message
            Bool:      True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("OFFSET")
            reply = float(reply)
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def reset_settings(self):
        """ Resets the settings to default

        Returns:
            str:    OK, or ERR message
            Bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("RESET SETTINGS")
            return ("OK", True)
        else:
            return ("ERR Not in API mode", False)

    def set_audio_in(self, audio_port="AUTO"):
        """ Sets the audio input selection

        Args:
            audio_port (str): Input selection as per API manual. Defaults to "AUTO".

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET AUDIO IN {audio_port}")
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def set_audio_trigger_level(self, trigger_level=4):
        """ Sets the audio trigger level

        Args:
            trigger_level (int): The trigger level between as per API manual

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET AUDIO TRIGGER LEVEL {str(trigger_level)}")
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def ser_extended_mode(self, mode=""):
        """ Sets extended mode status

        Args:
            mode (str): Extended mode status. Defaults to "OFF".

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET EXTENDED MODE {mode}")
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def set_frame_rate(self, frames):
        """ Sets the frame rate

        Args:
            frames (int): The frame rate to be set

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET FRAME RATE {str(frames)}")

            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def set_mask_len(self, mask):
        """ Sets the mast length

        Args:
            frames (int): The mast length to be set

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET MASK LEN {str(mask)}")

            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def set_offset(self, offset):
        """ Sets the user offset

        Args:
            frames (int): The offset to be applied

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET OFFSET {str(offset)}")

            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def set_speaker_dist(self, distance):
        """ Sets the speaker distance

        Args:
            frames (int): The offset to be applied

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET SPEAKER DIST {str(distance)}")

            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def set_video_trigger_level(self, trigger_level):
        """ Sets the video trigger level

        Args:
            frames (int): The trigger level to be applied

        Returns:
            str:    OK or ERR message
            bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply(
                f"SET VIDEO TRIGGER LEVEL {str(trigger_level)}")
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def settings(self):
        """ Returns the current unit settings

        Returns:
            list of settings :  
                    [0]: str (serial number)
                    [1]: str (firmware version)
                    [2]: int (frame rate)
                    [3]: int (manual offset)
                    [4]: float (speaker distance)
                    [5]: int (mask time)
                    [6]: str (audio input selection)
                    [7]: int (auto off time)
                    [8]: int (audio trigger level)
                    [9]: int (video trigger level)

            bool:   True for OK, False for error

        """
        if self.__in_API:
            reply = reply = self.__commmand_and_reply(
                'SETTINGS')
            settings_data = list(reply.split(","))
            # Convert numerical elements of the list to their respective types
            settings_data[2] = int(settings_data[2])
            settings_data[3] = int(settings_data[3])
            settings_data[4] = float(settings_data[4])
            settings_data[5] = int(settings_data[5])
            settings_data[7] = int(settings_data[7])
            settings_data[8] = int(settings_data[8])
            settings_data[9] = int(settings_data[9])
            return (settings_data, True)
        else:
            return ("ERR Not in API mode", False)

    def speaker_dist(self):
        """ Get the sepaker distance set

        Returns:
            int / str: speaker distance / ERR message
            Bool:      True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("SPEAKER DIST")
            distance = list(reply.split(","))
            # Convert list elements to their respevice types
            distance[0] = float(distance[0])
            distance[1] = int(distance[1])
            distance[2] = int(distance[2])
            return (distance, True)
        else:
            return ("ERR Not in API mode", False)

    def support_code(self):
        """ Generate a support code

        Returns:
            int / str: support code / ERR message
            Bool:      True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("SUPPORT CODE")
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def start(self):
        """ Start to take measurements

        Returns:
            str:    START / ERR message
            Bool:   True for OK, False for error
        """
        if self.__in_API:
            self.__com_port.timeout = 10
            reply = self.__commmand_and_reply("START")
            self.__wait_for_string("START")
            self.__com_port.timeout = 1
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def start_nocal(self):
        """ Start to take measurements, without re-calibrating

        Returns:
            str:    START / ERR message
            Bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("START NOCAL")
            self.__wait_for_string("START")
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def stats(self):
        """ Returns the stats in the buffer

        Returns:
            2d list of stats :  
                    [0]: int (reading in ms)
                    [1]: float (reading in frames)
                    [2]: int (buffer average in ms)
                    [3]: float (buffer average in frames)
                    [4]: int (span of buffer in ms)
                    [5]: float (span of buffer in frames)
                    [6]: str (E if reading taken from external port)
                    [7]: str (S if reading taken with speaker distance set)
                    [8]: str (O if reading taken with manual offset set)

            Bool:    True for OK, False for error
        """
        stats_list = []
        if self.__in_API:
            self.__send_command("STATS")
            read_line = self.__get_reply()
            if "ERR" not in read_line:
                while read_line:
                    stats_list.append(read_line.split(","))
                    read_line = self.__get_reply()
                # Convert list elements to their respevice types
                for row in stats_list:
                    for col in range(6):
                        row[col] = float(row[col])
                return (stats_list, True)
            return (read_line, False)
        else:
            return ("ERR Not in API mode", False)

    def stats_avg(self):
        """ Returns the average of the stats buffer

        Returns:
            list:  
                    [0]: int (average in ms)
                    [1]: float (average in frames)                    

            Bool:   True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("STATS AVG")
            if "ERR" not in reply:
                # Convert list elements to their respevice types
                avg_stats = list(reply.split(","))
                avg_stats[0] = int(avg_stats[0])
                avg_stats[1] = float(avg_stats[1])
                return (avg_stats, True)
            return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def stats_count(self):
        """ Return how many stats are in the buffer

        Returns:
            int / str: No of stats in buffer / ERR message
            Bool:      True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("STATS COUNT")
            reply = int(reply)
            return (reply, True)
        else:
            return ("ERR Not in API mode", False)

    def stats_span(self):
        """ Returns the span of the stats buffer

        Returns:
            list:  
                    [0]: int (span in ms)
                    [1]: float (span in frames)                    

            Bool:    True for OK, False for error
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("STATS SPAN")
            if "ERR" not in reply:
                span = list(reply.split(","))
                # Convert list elements to their respevice types
                span[0] = int(span[0])
                span[1] = float(span[1])
                return (span, True)
            else:
                span = reply
                return (span, False)
        else:
            return ("ERR Not in API mode", False)

    def stats_trim(self):
        """ Trims the stats buffer

        Returns:
            str:    OK or ERR message
            Bool:   True for OK, False for error 
        """
        if self.__in_API:
            reply = self.__commmand_and_reply("STATS TRIM")
            if "ERR" not in reply:
                return (reply, True)
            else:
                return (reply, False)
        else:
            return ("ERR Not in API mode", False)

    def stop(self):
        """ Stops taking readings

        Returns:
            str:    OK or ERR message
            Bool:   True for OK, False for error 
        """
        if self.__in_API:
            self.__send_command("STOP")
            reply = self.__wait_for_string("OK")
            return ("OK", True)
        else:
            return ("ERR Not in API mode", False)

    def get_reading(self):
        """ Return the reading taken

        Returns:
            int:    reading taken in ms, type is None if reading invalid
            bool:   True of the reading is valid
                    False if the reading timed out, reading invalid
        """
        if self.__in_API:
            reading = self.__get_reply()
            if reading:
                reading = int(reading)
                return (reading, True)
            else:
                return (None, False)
        else:
            return ("ERR Not in API mode", False)

"""

Example usage to enter the API, get 5 readings, print them and then quit the API.

# for Mac
# Sone2 = SyncOne2("/dev/cu.usbmodem14201")
# for PC
Sone2 = SyncOne2("COM3")
if Sone2.enter_API():
    # To get 5 readings
    reading, OK = Sone2.start()
    i = 0
    while (i < 5):
        reading, OK = Sone2.get_reading()
        if OK:
            i += 1
            print(reading)
    Sone2.stop()
else:
    print("Could not enter the API")
"""