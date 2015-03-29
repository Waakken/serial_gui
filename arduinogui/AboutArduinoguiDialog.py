# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from locale import gettext as _

import logging
logger = logging.getLogger('arduinogui')

from arduinogui_lib.AboutDialog import AboutDialog

# See arduinogui_lib.AboutDialog.py for more details about how this class works.
class AboutArduinoguiDialog(AboutDialog):
    __gtype_name__ = "AboutArduinoguiDialog"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the about dialog"""
        super(AboutArduinoguiDialog, self).finish_initializing(builder)

        # Code for other initialization actions should be added here.

