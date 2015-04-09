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
import os
import SimpleHTTPServer
import SocketServer
import socket
import threading

from arduinogui_lib import Window
from arduinogui.AboutArduinoguiDialog import AboutArduinoguiDialog
from arduinogui.PreferencesArduinoguiDialog import PreferencesArduinoguiDialog

#GObject.threads_init()

# See arduinogui_lib.Window.py for more details about how this class works
class ArduinoguiWindow(Window):
    __gtype_name__ = "ArduinoguiWindow"

    def hostingThread(self):
      PORT = 8080
      IP = self.getOwnAddr()
      Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
      while True:
        try:
          httpd = SocketServer.TCPServer((IP, PORT), Handler)
          break
        except:
          PORT += 1
      self.server_inst = httpd
      print "Serving at IP: %s port: %d" % (IP, PORT)
      self.ip_label.set_text("%s:%d" % (IP, PORT))
      self.server_status_label.set_text("Online")
      httpd.serve_forever()

    def getOwnAddr(self):
      #Connect to google server
      try:
        #IPv4 server:
        ownAddr = socket.create_connection(('8.8.8.8', 53), 5)
    
        #Uncomment this for creating IPv6 server:
        #ownAddr = socket.create_connection(('2001:4860:4860::8888', 53), 5)
    
        #Retrieve own IP
        my_IP = ownAddr.getsockname()[0]
        ownAddr.close()
        print "Retrieved own IP: ", my_IP
      except socket.timeout:
           print "No connection, creating localserver"
           my_IP = 'localhost'
      return my_IP
           
    def gatherData(self, spinbox_list):
      float_array = []
      for spinbox in spinbox_list:
        float_array.append(spinbox.get_adjustment().get_value())
      buf = struct.pack("%sf" % (len(float_array)), *float_array)
      return buf

    def printBinaryDebug(self, data):
      print "Start of debug print"
      debug_data = struct.unpack("%sB" % (len(data)), data)
      debug_data = "%d debug bytes: %s: " % (len(data), str(debug_data))
      #self.textbuffer.set_text(debug_data)
      print debug_data
      print data
      print "End of debug print"

    def unpackBinaryPid(self, data):
      float_str = "\n"
      i = 0
      packet_size = len(data)/4
      print "Received packet is %d bytes long. Unpacking %d floats" % (len(data), packet_size)
      try:
        floats = struct.unpack("%sf" % (packet_size), data)
      except struct.error:
        print "Unpack failed"
        return
      for flo in floats:
        float_str += (str(round(flo, 2)) + "  ")
        i += 1
        if not (i % 6):
          float_str += "\n"
      return float_str

    def unpackBinarySensor(self, data):
      float_str = "\n"
      i = 0
      print "Received packet is %d bytes long" % (len(data))
      try:
        floats = struct.unpack("fffhhh", data)
      except struct.error:
        print "Unpack failed"
        return
      for flo in floats:
        if i < 3:
          float_str += (str(round(flo, 1)) + "  ")
        else:
          float_str += (str(flo) + "  ")
        i += 1
        if not (i % 6):
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

    def serialRead(self, binary = False, packetSize = 1024):
        response = ""
        byte_count = 0
        while True:
          res = self.ser.read(1)
          if res:
            response += res
            byte_count += 1
          else:
            break
          if byte_count == packetSize:
            break
        self.bytes_label.set_text(str(byte_count))
        self.printBinaryDebug(response)
        if not binary:
          self.textbuffer.set_text(response)
          self.read_report += (response + " ")
        else:
          self.textbuffer.set_text("Data is in binary form")
          self.read_report += ("Binary data: " + response + " ")
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
        self.ser = serial.Serial(new_file, int(self.baud_entry.get_text()), timeout = 3)
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
        self.host_button = self.builder.get_object("host_button")

        self.textbuffer = self.builder.get_object("textbuffer")

        self.arduino_entry = self.builder.get_object("arduino_entry")
        self.baud_entry = self.builder.get_object("baud_entry")
        self.filename_entry = self.builder.get_object("filename_entry")

        self.serial_label = self.builder.get_object("serial_label");
        self.bytes_label = self.builder.get_object("bytes_label");
        self.time_label = self.builder.get_object("time_label");
        self.ip_label = self.builder.get_object("ip_label");
        self.server_status_label = self.builder.get_object("server_status_label");


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

        self.read_report = ""

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
        self.serialRead(packetSize = 12)

    #Tests that serial connection is ok. MCU should respond with 7 bytes: "conn ok"
    def on_test_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("t") == -1):
          return
        #Receive response:
        self.serialRead(packetSize = 7)

    #Enable debugging prints. Unable to retrieve PID values and Sensor values in this mode
    def on_enable_prints_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("e") == -1):
          return
        #Receive response:
        self.serialRead()

    #Orders MCU to reset
    def on_reset_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("r") == -1):
          return
        #Receive response:
        self.serialRead(packetSize = 8)

    #Read serial buffer until timeout
    def on_read_button_clicked(self, widget):
        res = 1
        response = ""
        #Read buffer
        try:
          self.serialRead()
        except AttributeError:
          print "No serial connetion"
          self.serial_label.set_text("No serial connection")

    #Request 72 byte "PID values" packet from copter
    def on_request_pid_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("a") == -1):
          return
        #Receive response:
        response = self.serialRead(binary = True, packetSize = 72)
        floats = self.unpackBinaryPid(response)
        if floats:
          floats = "Unpacked and formatted binary data: " + str(floats)
          self.textbuffer.set_text(floats)

    #Request 18 byte "Sensor values" packet from copter
    def on_request_sensor_button_clicked(self, widget):
        res = 1
        response = ""
        #Send test request:
        if(self.serialWrite("s") == -1):
          return
        #Receive response:
        response = self.serialRead(binary = True, packetSize = 18)
        floats = self.unpackBinarySensor(response)
        floats = "Unpacked and formatted binary data: " + str(floats)
        self.textbuffer.set_text(floats)

    def on_baud_entry_activate(self, widget):
      self.connectSerial()
        
    def on_arduino_entry_activate(self, widget):
      self.connectSerial()

    def on_report_button_clicked(self, widget):
      if not self.read_report:
        print "No new data to report"
        return
      print "Saving"
      fd = open("index.html", "a+")
      fd.write(str(datetime.datetime.now().strftime("%H:%M:%S")))
      fd.write("\n")
      fd.write(self.read_report)
      fd.write("\n")
      self.read_report = ""

    def on_clear_button_clicked(self, widget):
      try:
        os.unlink("index.html")
        print "File cleared"
      except OSError:
        print "Nothing to clear"

    def on_host_button_clicked(self, widget):
      self.server_thread = threading.Thread(target = self.hostingThread)
      self.server_thread.start()

    def on_stop_host_button_clicked(self, widget):
      threads = threading.activeCount()
      if threads == 1:
        print "Couldn't find other threads"
        return
      self.server_inst.shutdown()
      print "Waiting for thread to exit"
      self.server_thread.join()
      if threading.activeCount() == 1:
        print "Shutdown ok"
        self.server_status_label.set_text("Offline")
        self.ip_label.set_text("---")
