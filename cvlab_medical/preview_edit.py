from PyQt5 import QtCore, QtGui
import numpy as np
import copy

from PyQt5.QtWidgets import QMenu

from cvlab.view import image_preview
from cvlab.view.widgets import ActionImage, QAction, cv


def set_image_preview(self, arr):
    # remember not to modify arr !!!
    self.ConstPreview = qt_image_to_array(self.pixmap().toImage())
    if self.DataFlag == 0:
        add_actions(self)
    self.DataFlag = 1
    self.data_type = ActionImage.DATA_TYPE_IMAGE
    if isinstance(arr, np.ndarray):
        arr = self.preprocess_array(arr)
    if arr is None:
        pass
        # self.setPixmap(self.image_preview.default_image)  # todo: na pewno to chcemy? moze to nam opozniac interfejs!
    elif isinstance(arr, np.ndarray):
        qpix = image_preview.array_to_pixmap(arr)
        qpix_scaled = self.scale_pixmap(qpix)
        self.setPixmap(qpix_scaled)
        if self.image_dialog is not None:
            image_preview.imshow(self.name, qpix, show=False)

#sprawdzic czy nie wplywa przetwarzabue
def qt_image_to_array(img):
    assert isinstance(img, QtGui.QImage), "img must be a QtGui.QImage object"

    img_size = img.size()
    buffer = img.constBits()
    buffer.setsize(img_size.height() * img_size.width() * 8)


    arr = np.ndarray(shape  = (img_size.height(), img_size.width(), img.depth()//8),
                     buffer = buffer,
                     dtype  = np.uint8)
    return copy.deepcopy(arr)


def preview_options(self, a):

    arr = copy.deepcopy(self.ConstPreview)
    #do sprawdzenia czy modyfikowane sa np.array czy pixmap
    if a == 0:
        img = image_preview.array_to_pixmap(arr)
        self.setPixmap(img)
    elif a == 10:
        img = image_preview.array_to_pixmap(arr.clip(0, 255).astype(np.uint8))
        self.setPixmap(img)
    elif a == 20:
        img = image_preview.array_to_pixmap(arr.astype(np.float32).clip(0.0, 1.0))
        self.setPixmap(img)
    elif a == 21:
        arr=arr.astype(np.float32)
        min_, max_, _, _ = cv.minMaxLoc(arr.flatten())
        if min_ == max_:
            arr = np.zeros(arr.shape) + 0.5
        else:
            arr = (arr-min_)/(max_-min_)+min_
        img = image_preview.array_to_pixmap(arr.astype(np.float32))
        self.setPixmap(img)
    elif a == 22:
        arr=arr.astype(np.float32)
        min_, max_, _, _ = cv.minMaxLoc(arr.flatten())
        if min_ == max_:
            arr = np.zeros(arr.shape) + 0.5
        else:
            if len(arr.shape) > 2:
                mean = cv.mean(cv.mean(arr)[:3])[0]
            else:
                mean = cv.mean(arr)[0]
            scale = 0.5/max(max_-mean, mean-min_)
            arr = (arr-mean)*scale+0.5
        img = image_preview.array_to_pixmap(arr.astype(np.float32))
        self.setPixmap(img)
    elif a == 23:
        img = image_preview.array_to_pixmap(arr/255.)
        self.setPixmap(img)
    elif a == 30:
        arr = arr.astype(np.float32)
        min_, max_, _, _ = cv.minMaxLoc(arr.flatten())
        if min_ == max_:
            arr = np.zeros(arr.shape) + 0.5
        else:
            scale = 0.5/max(max_,-min_)
            arr = arr*scale+0.5
        img = image_preview.array_to_pixmap(arr.astype(np.float32))
        self.setPixmap(img)


def add_actions(self):
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

    actionMenu = QAction('Modify preview',self)

    x=QMenu("preview modifiers",self)
    action = QAction('Default preview', self)
    action.triggered.connect(lambda: self.preview_options(0))
    x.addAction(action)

    action = QAction('Truncate to 0-255', self)
    action.triggered.connect(lambda: self.preview_options(10))
    x.addAction(action)

    action = QAction('Truncate to 0-1', self)
    action.triggered.connect(lambda: self.preview_options(20))
    x.addAction(action)

    action = QAction('Scale contrast to 0-1', self)
    action.triggered.connect(lambda: self.preview_options(21))
    x.addAction(action)

    action = QAction('Mean -> 0.5 max/min -> 1/0', self)
    action.triggered.connect(lambda: self.preview_options(22))
    x.addAction(action)

    action = QAction('Divide by 255.0', self)
    action.triggered.connect(lambda: self.preview_options(23))
    x.addAction(action)

    action = QAction('0 -> 0.5, max/min -> 1/0', self)
    action.triggered.connect(lambda: self.preview_options(30))
    x.addAction(action)

    actionMenu.setMenu(x)
    self.addAction(actionMenu)
