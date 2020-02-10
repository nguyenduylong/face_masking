import cv2
import numpy as np
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal

class PushBut(QtWidgets.QPushButton):
    def __init__(self, background_url, parent=None):
        super(PushBut, self).__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet("margin: 1px; padding: 1px; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(127,127,255,255);")
        self.background_url = background_url
        self.setIcon(QtGui.QIcon(background_url))
        self.setFixedSize(72, 72)
        self.setIconSize(QtCore.QSize(70, 70))

    def enterEvent(self, event):
        if self.isEnabled() is True:
            self.setStyleSheet("margin: 1px; padding: 1px; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(0,230,255,255);")
            self.setIcon(QtGui.QIcon(self.background_url))
            self.setFixedSize(72, 72)
            self.setIconSize(QtCore.QSize(70, 70))

        if self.isEnabled() is False:
            self.setStyleSheet("margin: 1px; padding: 1px; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(127,127,255,255);")
            self.setIcon(QtGui.QIcon(self.background_url))
            self.setFixedSize(72, 72)
            self.setIconSize(QtCore.QSize(70, 70))

    def leaveEvent(self, event):
        self.setStyleSheet("margin: 1px; padding: 1px; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(127,127,255,255);")
        self.setIcon(QtGui.QIcon(self.background_url))
        self.setFixedSize(72, 72)
        self.setIconSize(QtCore.QSize(70, 70))