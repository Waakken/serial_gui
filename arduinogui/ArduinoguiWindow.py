# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from locale import gettext as _

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('arduinogui')

import serial

from arduinogui_lib import Window
from arduinogui.AboutArduinoguiDialog import AboutArduinoguiDialog
from arduinogui.PreferencesArduinoguiDialog import PreferencesArduinoguiDialog

# See arduinogui_lib.Window.py for more details about how this class works
class ArduinoguiWindow(Window):
    __gtype_name__ = "ArduinoguiWindow"
    try:
      ser = serial.Serial("/dev/ttyACM0", 9600, timeout = 1)
    except serial.serialutil.SerialException:
      print "Unable to create serial connection"
    
    def gatherData(self):
      message = ""
      message += "Roll P: %d" % int(self.roll_p_adj.get_value())
      message += " Roll I: %d" % int(self.roll_i_adj.get_value())
      message += " Roll D: %d" % int(self.roll_d_adj.get_value())
      message += "\n"
      message += "Pitch P: %d" % int(self.pitch_p_adj.get_value())
      message += " Pitch I: %d" % int(self.pitch_i_adj.get_value())
      message += " Pitch D: %d" % int(self.pitch_d_adj.get_value())
      message += "\n"
      message += "Yaw P: %d" % int(self.yaw_p_adj.get_value())
      message += " Yaw I: %d" % int(self.yaw_i_adj.get_value())
      message += " Yaw D: %d" % int(self.yaw_d_adj.get_value())
      return message

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(ArduinoguiWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutArduinoguiDialog
        self.PreferencesDialog = PreferencesArduinoguiDialog

        # Code for other initialization actions should be added here.
        self.sendbutton = self.builder.get_object("sendbutton")
        self.textbuffer = self.builder.get_object("textbuffer")
        self.arduino_entry = self.builder.get_object("arduino_entry")
        self.roll_p_adj = self.builder.get_object("roll_p_adj")
        self.roll_i_adj = self.builder.get_object("roll_i_adj")
        self.roll_d_adj = self.builder.get_object("roll_d_adj")
        self.pitch_p_adj = self.builder.get_object("pitch_p_adj")
        self.pitch_i_adj = self.builder.get_object("pitch_i_adj")
        self.pitch_d_adj = self.builder.get_object("pitch_d_adj")
        self.yaw_p_adj = self.builder.get_object("yaw_p_adj")
        self.yaw_i_adj = self.builder.get_object("yaw_i_adj")
        self.yaw_d_adj = self.builder.get_object("yaw_d_adj")

    def on_sendbutton_clicked(self, widget):
        res = 1
        message = self.gatherData()
        response = ""
        print "Sending message: ", message
        try:
          self.ser.write(message)
        except AttributeError:
          print "No serial connection"
          return
        self.ser.write("\n")
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
        self.ser = serial.Serial(new_file, 9600, timeout = 1)
        print "Connected to serial port"
      except serial.serialutil.SerialException:
        print "Unable to create serial connection"
      



