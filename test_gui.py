import cv2
import numpy as np
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from show_video import ShowVideo
from image_viewer import ImageViewer
from push_button import PushBut
 
if __name__ == '__main__':
 
    app = QtWidgets.QApplication(sys.argv)
    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo(sticker_path='./stickers/test2.png')
    vid.moveToThread(thread)
    image_viewer = ImageViewer()
 
    vid.VideoSignal.connect(image_viewer.setImage)
    #Button to start the videocapture:
 
    push_button1 = PushBut(background_url = './stickers/mustache.png')
    push_button1.clicked.connect(vid.startVideo)
    vertical_layout = QtWidgets.QVBoxLayout()
    button_layout = QtWidgets.QHBoxLayout()
    button_layout.addWidget(push_button1)
    button_widget = QtWidgets.QWidget()
    button_widget.setLayout(button_layout)
    vertical_layout.addWidget(image_viewer)
    vertical_layout.addWidget(button_widget)
    layout_widget = QtWidgets.QWidget()
    layout_widget.setLayout(vertical_layout)
    layout_widget.setStyleSheet("QWidget {background-color: rgba(255,255,255,255);} QScrollBar:horizontal {width: 1px; height: 1px;"
                                "background-color: rgba(255,255,255,255);} QScrollBar:vertical {width: 1px; height: 1px;"
                                "background-color: rgba(255,255,255,255);}")
    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(layout_widget)
    main_window.show()
    sys.exit(app.exec_())