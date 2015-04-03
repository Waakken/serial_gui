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


    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(ArduinoguiWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutArduinoguiDialog
        self.PreferencesDialog = PreferencesArduinoguiDialog

        self.spinbox_list = []

        # Code for other initialization actions should be added here.
        self.sendbutton = self.builder.get_object("sendbutton")
        self.textbuffer = self.builder.get_object("textbuffer")
        self.arduino_entry = self.builder.get_object("arduino_entry")
        self.serial_label = self.builder.get_object("serial_label");




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
        
        default_value = 0.1
        for spinbox in self.spinbox_list:
          adj = Gtk.Adjustment()
          adj.configure(0.00, 0, 3, 0.01, 0.01, 0.01)
          spinbox.set_adjustment(adj)
          adj.set_value(default_value)
          default_value += 0.1
      
        try:
          self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout = 0.1)
          self.serial_label.set_text("Connected to serial device")
        except serial.serialutil.SerialException:
          print "Unable to create serial connection"
          self.serial_label.set_text("Unable to create serial connection")
        except OSError:
          print "Unable to create serial connection"
          self.serial_label.set_text("Unable to create serial connection")
    

    def on_sendbutton_clicked(self, widget):
        res = 1
        message = self.gatherData(self.spinbox_list)
        response = ""
        #Send message:
        try:
          self.ser.write("\x0d")
          self.ser.write("\x0d")
          self.ser.write("\x0d")
          self.ser.write(message)
        except AttributeError:
          print "No serial connection"
          self.serial_label.set_text("No serial connection")
          return
        self.ser.write("\x0d")
        #Receive response:
        while True:
          res = self.ser.read()
          if not res:
            break
          response += res
        print response
        self.textbuffer.set_text(response)

    def on_arduino_entry_activate(self, widget):
      new_file = widget.get_text()
      print "Trying serial connect to: ", new_file
      try:
        self.ser.close()
      except AttributeError:
        pass
      try:
        self.ser = serial.Serial(new_file, 9600, timeout = 0.1)
        print "Connected to serial port"
        self.serial_label.set_text("Connected to serial device")
      except serial.serialutil.SerialException:
        print "Unable to create serial connection"
        self.serial_label.set_text("Unable to create serial connection")
      except OSError:
        print "Unable to create serial connection"
        self.serial_label.set_text("Unable to create serial connection")

