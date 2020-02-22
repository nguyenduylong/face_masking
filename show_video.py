import os
import cv2
from datetime import date
import numpy as np
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
import face_recognition
import imutils
from imutils import face_utils
import dlib
from collections import OrderedDict


cascade_path = './haarcascade/'
dlib_path = './dlib/shape_predictor_68_face_landmarks.dat'

mid_nose = 33
mid_mouth = 51

eye_right = 17
eye_left = 27

lip_right = 48
lip_left = 55

nose_1 = 29
nose_2 = 36


def shapetocord(dshape):
    # initialize the list of (x, y)-coordinates
    cords = np.zeros((68, 2),dtype='int')
    # loop over the 68 facial landmarks and convert them to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        cords[i] = (dshape.part(i).x,dshape.part(i).y)  #E.g now dshape.part[5].x will give us the point on x axis for the 6th 
        #landmark
    # return the list of (x, y) tuple-coordinates
    return cords

class ShowVideo(QtCore.QObject):
     
    #initiating the built in camera
    camera_port = 0
    camera = cv2.VideoCapture(camera_port)
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)
    
    def reset_mask_of_sticker(self):
        if self.sticker_type is '' :
            return
        self.imgSticker = cv2.imread(self.sticker_path, -1)
        self.imgSticker = cv2.cvtColor(self.imgSticker, cv2.COLOR_BGR2BGRA)
        # Create the mask for the sticker
        self.origin_mask = self.imgSticker[:,:,3]
        
        # Create the inverted mask for the sticker
        self.orig_mask_inv = cv2.bitwise_not(self.origin_mask)
        
        # Convert mustache image to BGR
        # and save the original image size (used later when re-sizing the image)
        self.imgSticker = self.imgSticker[:,:,0:3]
        self.imgSticker = cv2.cvtColor(self.imgSticker, cv2.COLOR_BGR2RGB)
        self.origStickerHeight, self.origStickerWidth = self.imgSticker.shape[:2]

    def __init__(self, parent = None, sticker_path = ''):
        super(ShowVideo, self).__init__(parent)
        self.dlib_face_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(dlib_path)
        self.sticker_path = sticker_path
        self.sticker_type = ''
        self.imgSticker = []
        self.origin_mask = []
        self.orig_mask_inv = []
        self.origStickerHeight = 0
        self.origStickerWidth = 0

        self.reset_mask_of_sticker()

    @QtCore.pyqtSlot()
    def startVideo(self):
 
        run_video = True
        while run_video:
            ret, image = self.camera.read()
 
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            if self.sticker_type is not '' :
                dlib_faces = self.dlib_face_detector(gray_swapped_image)
                # loop over the face detections
                for (i, rect) in enumerate(dlib_faces):
                    # convert the facial landmark (x, y)-coordinates to a NumPy
                    # array
                    shape = self.predictor(gray_swapped_image, rect)
                    coordinates = shapetocord(shape)
                    shape = face_utils.shape_to_np(shape)
                    (x, y, w, h) = face_utils.rect_to_bb(rect)
                    x1, x2, y1, y2, stickerHeight, stickerWidth = self.calculate_position_sticker_size(coordinates)
                    if stickerWidth != 0 and stickerHeight != 0:
                        sticker = cv2.resize(self.imgSticker, (stickerWidth,stickerHeight), interpolation = cv2.INTER_AREA)
                        mask = cv2.resize(self.origin_mask, (stickerWidth,stickerHeight), interpolation = cv2.INTER_AREA)
                        mask_inv = cv2.resize(self.orig_mask_inv, (stickerWidth,stickerHeight), interpolation = cv2.INTER_AREA)
                        # take ROI for mustache from background equal to size of mustache image
                        roi = color_swapped_image[y1:y2, x1:x2]
                        # roi_bg contains the original image only where the mustache is not
                        # in the region that is the size of the mustache.
                        roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
                
                        # roi_fg contains the image of the mustache only where the mustache is
                        roi_fg = cv2.bitwise_and(sticker,sticker,mask = mask)
                        if roi_bg.shape == roi_fg.shape:
                            # join the roi_bg and roi_fg
                            dst = cv2.add(roi_bg,roi_fg)
                            # place the joined image, saved to dst back over the original image
                            color_swapped_image[y1:y2, x1:x2] = dst
            height, width, _ = color_swapped_image.shape
            
            qt_image = QtGui.QImage(color_swapped_image.data,
                                    width,
                                    height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
 
            self.VideoSignal.emit(qt_image)

    def set_new_sticker(self, sticker_path='./stickers/mustache.png',sticker_type='mustache'):
        self.sticker_path = sticker_path
        self.sticker_type = sticker_type
        self.reset_mask_of_sticker()

    def calculate_position_mustache(self, coordinates):
        [midNoseX, midNoseY] = coordinates[mid_nose]
        [midMouthX, midMouthY] = coordinates[mid_mouth]  
        [midMouthX, midMouthY] = coordinates[mid_mouth]  
        [midMouthX, midMouthY] = coordinates[mid_mouth]  
        stickerHeight = abs(midMouthY - midNoseY) + 16
        stickerWidth = stickerHeight * self.origStickerWidth / self.origStickerHeight
        x1 = midNoseX - stickerWidth/2 
        x1 = midNoseX - stickerWidth/2 
        x1 = midNoseX - stickerWidth/2 
        x2 = midNoseX + stickerWidth/2
        y2 = midMouthY + 8
        y1 = midNoseY - 8
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        stickerHeight = int(y2 - y1)
        stickerWidth = int(x2 - x1)

        return x1, x2, y1, y2, stickerHeight, stickerWidth

    def calculate_position_goggle(self, coordinates):
        pts = coordinates[eye_right:eye_left]
        xeye,yeye,weye,heye = cv2.boundingRect(pts)
        yeye = int(yeye + heye/3)
        stickerWidth =  int(weye * 1.4)
        stickerHeight = int(stickerWidth * self.origStickerHeight/ self.origStickerWidth)
        x1 = int(xeye) - int((stickerWidth - weye)/2)
        x2 = x1 + stickerWidth
        y2 = yeye + stickerHeight
        y1 = yeye
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        stickerHeight = int(y2 - y1)
        stickerWidth = int(x2 - x1)

        return x1, x2, y1, y2, stickerHeight, stickerWidth

    def calculate_position_lip(self, coordinates):
        pts = coordinates[lip_right:lip_left]
        xlip,ylip,wlip,hlip = cv2.boundingRect(pts)
        stickerWidth =  wlip + 50
        stickerHeight = int(stickerWidth * self.origStickerHeight/ self.origStickerWidth)
        x1 = int(xlip) - 25
        x2 = x1 + stickerWidth
        y2 = ylip - 10 + stickerHeight
        y1 = ylip - 10
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        stickerHeight = int(y2 - y1)
        stickerWidth = int(x2 - x1)

        return x1, x2, y1, y2, stickerHeight, stickerWidth
    
    def calculate_position_nose(self, coordinates):
        pts = coordinates[nose_1:nose_2]
        xnose,ynose,wnose,hnose = cv2.boundingRect(pts)
        stickerWidth =  wnose + 30
        stickerHeight = int(stickerWidth * self.origStickerHeight/ self.origStickerWidth)
        x1 = int(xnose) - 15
        x2 = x1 + stickerWidth
        y2 = ynose + stickerHeight
        y1 = ynose
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        stickerHeight = int(y2 - y1)
        stickerWidth = int(x2 - x1)
        return x1, x2, y1, y2, stickerHeight, stickerWidth
    
    def calculate_position_sticker_size(self, coordinates):
        stickerHeight, stickerWidth = 0, 0
        x1, x2, y1, y2 = 0, 0, 0, 0
        switcher = {
            'mustache': self.calculate_position_mustache,
            'goggle': self.calculate_position_goggle,
            'lip': self.calculate_position_lip,
            'nose': self.calculate_position_nose,
        }
        if(self.origStickerWidth != 0 and self.origStickerHeight != 0):
            func = switcher.get(self.sticker_type, lambda: "Invalid month")
            x1, x2, y1, y2, stickerHeight, stickerWidth = func(coordinates)
        return x1, x2, y1, y2, stickerHeight, stickerWidth
