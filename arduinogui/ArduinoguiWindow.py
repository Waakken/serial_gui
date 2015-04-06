# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from locale import gettext as _

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('arduinogui')

import serial
import struct
import datetime

from arduinogui_lib import Window
from arduinogui.AboutArduinoguiDialog import AboutArduinoguiDialog
from arduinogui.PreferencesArduinoguiDialog import PreferencesArduinoguiDialog

# See arduinogui_lib.Window.py for more details about how this class works
class ArduinoguiWindow(Window):
    __gtype_name__ = "ArduinoguiWindow"
    
    def gatherData(self, spinbox_list):
      float_array = []
      for spinbox in spinbox_list:
        float_array.append(spinbox.get_adjustment().get_value())
      buf = struct.pack("%sf" % (len(float_array)), *float_array)
      return buf

    def unpackBinaryPid(self, data):
      float_str = "\n"
      i = 0
      packet_size = len(data)/4
      print "Received data is %d bytes long. Unpacking %d floats" % (len(data), packet_size)
      floats = struct.unpack("%sf" % (packet_size), data)
      for flo in floats:
        float_str += (str(round(flo, 2)) + "  ")
        i += 1
        if not (i % 4):
          float_str += "\n"
      return float_str

    def unpackBinarySensor(self, data):
      float_str = "\n"
      i = 0
      print "Received data is %d bytes long" % (len(data))
      floats = struct.unpack("fffhhh", data)
      for flo in floats:
        float_str += (str(flo) + "  ")
        i += 1
        if not (i % 4):
          float_str += "\n"
      return float_str

    def serialWrite(self, msg):
        try:
          self.ser.write(msg)
        except AttributeError:
          print "No serial connetion"
          self.serial_label.set_text("No serial connection")
          return -1
        return 0

    def serialRead(self, binary = False):
        response = ""
        byte_count = 0
        while True:
          res = self.ser.read(1)
          if res:
            response += res
            byte_count += 1
          else:
            break
        self.bytes_label.set_text(str(byte_count))
        if not binary:
          self.textbuffer.set_text(response)
        else:
          self.textbuffer.set_text("Data is in binary form")
        self.time_label.set_text(str(datetime.datetime.now().strftime("%H:%M:%S")))
        return response


    def connectSerial(self):
      new_file = self.arduino_entry.get_text()
      print "Trying serial connect to: ", new_file
      try:
        self.ser.close()
      except AttributeError:
        pass
      try:
        self.ser = serial.Serial(new_file, int(self.baud_entry.get_text()), timeout = 2)
        print "Connected to serial device"
        self.serial_label.set_text("Connected to serial device")
      except serial.serialutil.SerialException:
        print "Unable to create serial connection."
        self.serial_label.set_text("Unable to create serial connection")
      except OSError:
        print "Unenable to connect to a serial device"
        self.serial_label.set_text("Unenable to connect to a serial device")
      except ValueError:
        print "Error with connection caused propably by a bad baud rate"
        self.serial_label.set_text("Error with connection caused propably by a bad baud rate")

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(ArduinoguiWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutArduinoguiDialog
        self.PreferencesDialog = PreferencesArduinoguiDialog

        self.spinbox_list = []

        # Code for other initialization actions should be added here.
        self.sendbutton = self.builder.get_object("sendbutton")
        self.test_button = self.builder.get_object("test_button")
        self.request_pid_button = self.builder.get_object("request_pid_button")
        self.request_sensor_button = self.builder.get_object("request_sensor_button")
        self.reset_button = self.builder.get_object("reset_button")
        self.read_button = self.builder.get_object("reset_button")

        self.textbuffer = self.builder.get_object("textbuffer")

        self.arduino_entry = self.builder.get_object("arduino_entry")
        self.baud_entry = self.builder.get_object("baud_entry")

        self.serial_label = self.builder.get_object("serial_label");
        self.bytes_label = self.builder.get_object("bytes_label");
        self.time_label = self.builder.get_object("time_label");


        self.roll_angle_p = self.builder.get_object("roll_angle_p")
        self.spinbox_list.append(self.roll_angle_p)
        self.roll_angle_i = self.builder.get_object("roll_angle_i")
        self.spinbox_list.append(self.roll_angle_i)
        self.roll_angle_d = self.builder.get_object("roll_angle_d")
        self.spinbox_list.append(self.roll_angle_d)

        self.roll_rate_p = self.builder.get_object("roll_rate_p")
        self.spinbox_list.append(self.roll_rate_p)
        self.roll_rate_i = self.builder.get_object("roll_rate_i")
        self.spinbox_list.append(self.roll_rate_i)
        self.roll_rate_d = self.builder.get_object("roll_rate_d")
        self.spinbox_list.append(self.roll_rate_d)

        self.pitch_angle_p = self.builder.get_object("pitch_angle_p")
        self.spinbox_list.append(self.pitch_angle_p)
        self.pitch_angle_i = self.builder.get_object("pitch_angle_i")
        self.spinbox_list.append(self.pitch_angle_i)
        self.pitch_angle_d = self.builder.get_object("pitch_angle_d")
        self.spinbox_list.append(self.pitch_angle_d)

        self.pitch_rate_p = self.builder.get_object("pitch_rate_p")
        self.spinbox_list.append(self.pitch_rate_p)
        self.pitch_rate_i = self.builder.get_object("pitch_rate_i")
        self.spinbox_list.append(self.pitch_rate_i)
        self.pitch_rate_d = self.builder.get_object("pitch_rate_d")
        self.spinbox_list.append(self.pitch_rate_d)

        self.yaw_angle_p = self.builder.get_object("yaw_angle_p")
        self.spinbox_list.append(self.yaw_angle_p)
        self.yaw_angle_i = self.builder.get_object("yaw_angle_i")
        self.spinbox_list.append(self.yaw_angle_i)
        self.yaw_angle_d = self.builder.get_object("yaw_angle_d")
        self.spinbox_list.append(self.yaw_angle_d)

        self.yaw_rate_p = self.builder.get_object("yaw_rate_p")
        self.spinbox_list.append(self.yaw_rate_p)
        self.yaw_rate_i = self.builder.get_object("yaw_rate_i")
        self.spinbox_list.append(self.yaw_rate_i)
        self.yaw_rate_d = self.builder.get_object("yaw_rate_d")
        self.spinbox_list.append(self.yaw_rate_d)
        
        # Add adjustment to each spinbox and give them incrementing default values
        #default_value = 0.1
        for spinbox in self.spinbox_list:
          adj = Gtk.Adjustment()
          adj.configure(0.00, 0, 3, 0.01, 0.01, 0.01)
          spinbox.set_adjustment(adj)
          #adj.set_value(default_value)
          #default_value += 0.1
      
        self.connectSerial()    

    def on_sendbutton_clicked(self, widget):
        res = 1
        #Create message that contains 18 4-byte float values
        message = self.gatherData(self.spinbox_list)
        response = ""
        #Tell MCU that we're going to send PIDs:
        if(self.serialWrite("n") == -1):
          return
        #Send message:
        self.serialWrite(message)
        #Receive response:
        self.serialRead()

    def on_test_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("t") == -1):
          return
        #Receive response:
        self.serialRead()

    def on_reset_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("r") == -1):
          return
        #Receive response:
        self.serialRead()

    def on_read_button_clicked(self, widget):
        res = 1
        response = ""
        #Read buffer
        try:
          self.serialRead()
        except AttributeError:
          print "No serial connetion"
          self.serial_label.set_text("No serial connection")

    def on_request_pid_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("a") == -1):
          return
        #Receive response:
        response = self.serialRead(binary = True)
        floats = self.unpackBinaryPid(response)
        floats = "Unpacked and formatted binary data: " + str(floats)
        self.textbuffer.set_text(floats)

    def on_request_sensor_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("s") == -1):
          return
        #Receive response:
        response = self.serialRead(binary = True)
        floats = self.unpackBinarySensor(response)
        floats = "Unpacked and formatted binary data: " + str(floats)
        self.textbuffer.set_text(floats)

    def on_baud_entry_activate(self, widget):
      self.connectSerial()
        
    def on_arduino_entry_activate(self, widget):
      self.connectSerial()

