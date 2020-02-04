import cv2
import numpy as np
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal


face_cascPath = 'haarcascade_frontalface_default.xml'
nose_cascPath = 'haarcascade_mcs_nose.xml'

class ShowVideo(QtCore.QObject):
 
    #initiating the built in camera
    camera_port = 0
    camera = cv2.VideoCapture(camera_port)
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)
    
 
    def __init__(self, parent = None, sticker_path = './stickers/test.jpeg'):
        super(ShowVideo, self).__init__(parent)
        self.face_detector = cv2.CascadeClassifier(face_cascPath)
        self.noseCascade = cv2.CascadeClassifier(nose_cascPath)
        self.sticker_path = sticker_path
        print(self.sticker_path)
        # Load our overlay image: mustache.png
        self.imgMustache = cv2.imread(self.sticker_path, -1)
        self.imgMustache = cv2.cvtColor(self.imgMustache, cv2.COLOR_BGR2BGRA)
        print(self.imgMustache.shape)
        # Create the mask for the mustache
        self.orig_mask = self.imgMustache[:,:,3]
        
        # Create the inverted mask for the mustache
        self.orig_mask_inv = cv2.bitwise_not(self.orig_mask)
        
        # Convert mustache image to BGR
        # and save the original image size (used later when re-sizing the image)
        self.imgMustache = self.imgMustache[:,:,0:3]
        self.origMustacheHeight, self.origMustacheWidth = self.imgMustache.shape[:2]
    @QtCore.pyqtSlot()
    def startVideo(self):
 
        run_video = True
        while run_video:
            ret, image = self.camera.read()
 
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_detector.detectMultiScale(
                gray_swapped_image,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(50, 50),
                flags=cv2.CASCADE_SCALE_IMAGE
            )   

            for (x,y,w,h) in faces:
                roi_gray = gray_swapped_image[y:y+h, x:x+w]
                roi_color = color_swapped_image[y:y+h, x:x+w]
                # Detect a nose within the region bounded by each face (the ROI)
                nose = self.noseCascade.detectMultiScale(roi_gray)

                for (nx,ny,nw,nh) in nose:
                    mustacheWidth =  3 * nw
                    mustacheHeight = mustacheWidth * self.origMustacheHeight / self.origMustacheWidth
                    x1 = nx - (mustacheWidth/4)
                    x2 = nx + nw + (mustacheWidth/4)
                    y1 = ny + nh - (mustacheHeight/2)
                    y2 = ny + nh + (mustacheHeight/2)
                                # Check for clipping
                    if x1 < 0:
                        x1 = 0
                    if y1 < 0:
                        y1 = 0
                    if x2 > w:
                        x2 = w
                    if y2 > h:
                        y2 = h
 
                    # Re-calculate the width and height of the mustache image
                    x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
                    mustacheWidth = int(x2 - x1)
                    mustacheHeight = int(y2 - y1)
                    mustache = cv2.resize(self.imgMustache, (mustacheWidth,mustacheHeight), interpolation = cv2.INTER_AREA)
                    mask = cv2.resize(self.orig_mask, (mustacheWidth,mustacheHeight), interpolation = cv2.INTER_AREA)
                    mask_inv = cv2.resize(self.orig_mask_inv, (mustacheWidth,mustacheHeight), interpolation = cv2.INTER_AREA)
        
                    # take ROI for mustache from background equal to size of mustache image
                    roi = roi_color[y1:y2, x1:x2]
        
                    # roi_bg contains the original image only where the mustache is not
                    # in the region that is the size of the mustache.
                    roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
        
                    # roi_fg contains the image of the mustache only where the mustache is
                    roi_fg = cv2.bitwise_and(mustache,mustache,mask = mask)
        
                    # join the roi_bg and roi_fg
                    dst = cv2.add(roi_bg,roi_fg)
        
                    # place the joined image, saved to dst back over the original image
                    roi_color[y1:y2, x1:x2] = dst
                cv2.rectangle(color_swapped_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            height, width, _ = color_swapped_image.shape
            
            #width = camera.set(CAP_PROP_FRAME_WIDTH, 1600)
			#height = camera.set(CAP_PROP_FRAME_HEIGHT, 1080)
			#camera.set(CAP_PROP_FPS, 15)
            
            qt_image = QtGui.QImage(color_swapped_image.data,
                                    width,
                                    height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
 
            self.VideoSignal.emit(qt_image)

    def set_icon(self, sticker_path = '.stickers/mustache.png'):
        self.sticker_path = sticker_path;

 
 
class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
 
 
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0,0, self.image)
        self.image = QtGui.QImage()
 
    def initUI(self):
        self.setWindowTitle('Test')
 
    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")
 
        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()

class PushBut1(QtWidgets.QPushButton):
    def __init__(self, background_url, parent=None):
        super(PushBut1, self).__init__(parent)
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
 
 
if __name__ == '__main__':
 
    app = QtWidgets.QApplication(sys.argv)
    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo(sticker_path='./stickers/test2.png')
    vid.moveToThread(thread)
    image_viewer = ImageViewer()
 
    vid.VideoSignal.connect(image_viewer.setImage)
    #Button to start the videocapture:
 
    push_button1 = PushBut1(background_url = './stickers/mustache.png')
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