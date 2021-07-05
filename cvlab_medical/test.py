from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage

from cvlab.view import image_preview

from cvlab.view.widgets import PreviewsContainer, OutputPreview

from cvlab.view.widgets import ActionImage, QAction, cv
import numpy as np
import copy

def set_image_test(self, arr):
    # remember not to modify arr !!!
    self.ConstPreview= qt_image_to_array(self.pixmap().toImage())
    if self.DataFlag == 0:
        prepare_actions2(self)
    self.DataFlag=1
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

def qt_image_to_array(img):
    assert isinstance(img, QtGui.QImage), "img must be a QtGui.QImage object"
   # assert img.format() == QtGui.QImage.Format.Format_RGB32, \
     #   "img format must be QImage.Format.Format_RGB32, got: {}".format(img.format())

    img_size = img.size()
    buffer = img.constBits()
    buffer.setsize(img_size.height() * img_size.width() * 8)

    # Sanity check
    # n_bits_buffer = len(buffer) * 8
    # n_bits_image  = img_size.width() * img_size.height() * img.depth()
    # assert n_bits_buffer == n_bits_image, \
    #     "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image)
    #
    # assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())

    # Note the different width height parameter order!
    arr = np.ndarray(shape  = (img_size.height(), img_size.width(), img.depth()//8),
                     buffer = buffer,
                     dtype  = np.uint8)
    return copy.deepcopy(arr)

def teste(self,a):
     # w= self.ConstPreview.toImage()
      #w= self.pixmap().toImage()

      arr=copy.deepcopy(self.ConstPreview)#qt_image_to_array(w)
      #arr=self.ConstPreview
      if a==10:
        img= image_preview.array_to_pixmap(arr.astype(np.float32).clip(0.0, 1.0))
        self.setPixmap(img)
      elif a==22:

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
          img = image_preview.array_to_pixmap(arr)
          self.setPixmap(img)


def prepare_actions2(self,enable=True):

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        action = QAction('Mean -> 0.5 max/min -> 1/0', self)
        action.triggered.connect(lambda: self.teste(22))
        self.addAction(action)
        d=QAction('Truncate to 0-1', self)
        d.triggered.connect(lambda: self.teste(10))
        self.addAction(d)

    # def process_inputs(self, inputs, outputs, parameters):
    #     i = inputs["input"].value
    #     t = parameters["type"]
    #     o = None
    #     if t == 0:
    #         o = i
    #     elif t == 10:
    #         o = i.clip(0, 255).astype(np.uint8)
    #     elif t == 20:
    #         o = i.astype(np.float32).clip(0.0, 1.0)
    #     elif t == 21:
    #         o = i.astype(np.float32)
    #         min_, max_, _, _ = cv.minMaxLoc(o.flatten())
    #         if min_ == max_:
    #             o = np.zeros(o.shape) + 0.5
    #         else:
    #             o = (o-min_)/(max_-min_)+min_
    #     elif t == 22:
    #         o = i.astype(np.float32)
    #         min_, max_, _, _ = cv.minMaxLoc(o.flatten())
    #         if min_ == max_:
    #             o = np.zeros(o.shape) + 0.5
    #         else:
    #             if len(o.shape) > 2:
    #                 mean = cv.mean(cv.mean(o)[:3])[0]
    #             else:
    #                 mean = cv.mean(o)[0]
    #             scale = 0.5/max(max_-mean, mean-min_)
    #             o = (o-mean)*scale+0.5
    #     elif t == 23:
    #         o = i / 255.
    #     elif t == 30:
    #         o = i.astype(np.float32)
    #         min_, max_, _, _ = cv.minMaxLoc(o.flatten())
    #         if min_ == max_:
    #             o = np.zeros(o.shape) + 0.5
    #         else:
    #             scale = 0.5/max(max_,-min_)
    #             o = o*scale+0.5
    #     outputs["output"] = Data(o)

# [ComboboxParameter("type", [
#     ("No change", 0),
#     ("Truncate to 0-255", 10),
#     ("Truncate to 0-1", 20),
#     ("Scale contrast to 0-1", 21),
#     ("Mean -> 0.5 max/min -> 1/0", 22),
#     ("Divide by 255.0", 23),
#     ("0 -> 0.5, max/min -> 1/0", 30),
# ])]
