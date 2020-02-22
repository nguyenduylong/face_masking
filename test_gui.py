import os
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

stickers_folder = './stickers'
if __name__ == '__main__':

    def create_button_layout():
        #Button to start the videocapture:
        start_button = PushBut(background_url='./stickers/start_butt.png')
        start_button.clicked.connect(vid.startVideo)
        push_button1 = PushBut(background_url = './stickers/mustache.png')
        push_button1.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/mustache.png', sticker_type='mustache'))
        push_button8 = PushBut(background_url = './stickers/mustache_2.png')
        push_button8.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/mustache_2.png', sticker_type='mustache'))
        push_button6 = PushBut(background_url='./stickers/goggle.png')
        push_button6.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/goggle.png', sticker_type='goggle'))
        push_button2 = PushBut(background_url='./stickers/goggle_2.png')
        push_button2.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/goggle_2.png', sticker_type='goggle'))
        push_button7 = PushBut(background_url='./stickers/goggle_4.png')
        push_button7.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/goggle_4.png', sticker_type='goggle'))
        push_button3 = PushBut(background_url='./stickers/lip_1.png')
        push_button3.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/lip_1.png', sticker_type='lip'))
        push_button5 = PushBut(background_url='./stickers/mouth_1.png')
        push_button5.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/mouth_1.png', sticker_type='lip'))
        push_button9 = PushBut(background_url='./stickers/mouth_2.png')
        push_button9.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/mouth_2.png', sticker_type='lip'))
        push_button4 = PushBut(background_url='./stickers/nose_1.png')
        push_button4.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/nose_1.png', sticker_type='nose'))
        push_button10 = PushBut(background_url='./stickers/nose_2.png')
        push_button10.clicked.connect(lambda: vid.set_new_sticker(sticker_path='./stickers/nose_2.png', sticker_type='nose'))
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(start_button)
        button_layout.addWidget(push_button1)
        button_layout.addWidget(push_button8)
        button_layout.addWidget(push_button6)
        button_layout.addWidget(push_button2)
        button_layout.addWidget(push_button7)
        button_layout.addWidget(push_button3)
        button_layout.addWidget(push_button4)
        button_layout.addWidget(push_button10)
        button_layout.addWidget(push_button5)
        button_layout.addWidget(push_button9)

        return button_layout

 
    app = QtWidgets.QApplication(sys.argv)
    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo()
    vid.moveToThread(thread)
    image_viewer = ImageViewer()
 
    vid.VideoSignal.connect(image_viewer.setImage)
    
    vertical_layout = QtWidgets.QVBoxLayout()
    button_layout = create_button_layout()
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
    main_window.setFixedSize(layout_widget.sizeHint())
    sys.exit(app.exec_())