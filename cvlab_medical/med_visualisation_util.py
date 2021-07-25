# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame
# from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
# from vtkplotter import Volume, Plotter
#
#
# class VtkVisualisationWindow(QMainWindow):
#     def __init__(self, data):
#         super().__init__()
#
#         vol = Volume(data, c=['white', 'b', 'g', 'r'])
#         vol.addScalarBar3D()
#         #
#         vp = Plotter(verbose=0)
#
#         # # vp.load("IMG_0002.nii.gz")
#         vp.show(vol, __doc__, axes=1)
#
#
# class VtkVisualisationWidget(QWidget):
#     def __init__(self, data):
#         super().__init__()
#
#         self.vtkWidget = QVTKRenderWindowInteractor()
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.vtkWidget)
#         self.setLayout(layout)
import json
from datetime import datetime, timedelta

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from distutils.util import strtobool

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkplotter import Volume, Plotter

from cvlab.view import image_preview, config
from cvlab.view.widgets import ActionImage, OutputPreview
from .med_image_io import *
from cvlab.view.image_preview import *


class PreviewWindowVtk(QFrame):
    minsize = (32, 32)
    maxsize = None
    last_save_dir = ""
    raise_window = False

    key_signal = pyqtSignal(int, int, int)
    move_signal = pyqtSignal()

    def __init__(self, manager, name, image=None, message=None, position=None, size=None, high_quality=False):
        # super(PreviewWindowVtk, self).__init__(manager, name, image, message, position, size, high_quality)
        super(PreviewWindowVtk, self).__init__()
        self.setObjectName("Visualisation window {}".format(name))
        self.setWindowTitle(name)

        self.vtkWidget = None

        self.manager = manager

        desktop = QApplication.instance().desktop()
        if self.maxsize:
            self.maxsize = QSize(*self.maxsize)
        else:
            self.maxsize = desktop.screenGeometry(desktop.screenNumber(self)).size() * 0.95

        self.setMinimumSize(*self.minsize)
        self.setMaximumSize(self.maxsize)

        self.image = None
        self.original = None
        self.message = message
        self.scale = 1.
        self.rotation = 0
        self.quality = Qt.SmoothTransformation if high_quality else Qt.FastTransformation
        self.fixed_size = size

        self.scrollarea = PreviewScrollArea()
        self.scrollarea.setFrameStyle(0)
        self.scrollarea.setFocusPolicy(Qt.NoFocus)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self.scrollarea, 0, 0)

        self.preview = QLabel()
        self.preview.setMouseTracking(False)
        self.preview.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scrollarea.setWidget(self.preview)

        self.message_label = QLabel(" ")
        self.layout().addWidget(self.message_label, 0, 0, Qt.AlignTop)
        self.message_label.setStyleSheet("QLabel {color:black;background:rgba(255,255,255,32)}")
        self.message_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.message_label.setText("")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setColor(Qt.white)
        shadow.setOffset(0, 0)
        self.message_label.setGraphicsEffect(shadow)

        self.blink_widget = QWidget()
        self.blink_widget.hide()
        self.blink_widget.setStyleSheet("border:3px solid red")
        self.blink_timer = QTimer()
        self.blink_timer.setInterval(1000)
        self.blink_timer.timeout.connect(self.blink_)
        layout.addWidget(self.blink_widget, 0, 0)

        self.setImageVtk(image, show=False)

        if image is not None and not size:
            size = self.autoSize()

        if size:
            self.resize(*size)

        if position == 'cursor':
            position = (QCursor.pos().x() - self.size().width() // 2, QCursor.pos().y() - self.size().height() // 2)

        if position:
            self.move(*position)

        self.showNormal()

    def setImage(self, image, show=True, scale=None, blink=False):
        if image is None: return
        self.original = image
        if isinstance(image, QImage):
            image = QPixmap.fromImage(image)
        elif isinstance(image, QPixmap):
            pass
        else:
            image = array_to_pixmap(image)
        self.image = image
        if not scale:
            scale = self.scale
            if image.width() * scale > self.maxsize.width():
                scale = self.maxsize.width() / image.width()
            if image.height() * scale > self.maxsize.height():
                scale = self.maxsize.height() / image.height()
        self.setZoom(scale)
        if self.message is not None:
            self.message_label.setText(self.message)
        if blink:
            self.blink(True)
        if show:
            self.show()
            if self.raise_window:
                self.raise_()

    def setImageVtk(self, image, show=True, scale=None, blink=False):
        print("CV LAB VTK 2")
        if image is None:
            return

        # layout = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.resize(512, 512)
        # layout.addWidget(vtkWidget)
        # self.setLayout(layout)
        self.layout().addWidget(self.vtkWidget, 0, 0)

        vol = Volume(image, c=['white', 'b', 'g', 'r'])
        vol.addScalarBar3D()
        vp = Plotter(verbose=0, qtWidget=self.vtkWidget)

        # self.original = image
        # if isinstance(image, QImage):
        #     image = QPixmap.fromImage(image)
        # elif isinstance(image, QPixmap):
        #     pass
        # else:
        #     image = array_to_pixmap(image)
        # self.image = image

        # if not scale:
        #     scale = self.scale
        #     if 512*scale > self.maxsize.width():
        #         scale = self.maxsize.width() / image.width()
        #     if 512*scale > self.maxsize.height():
        #         scale = self.maxsize.height() / image.height()
        # self.setZoom(scale)
        if blink:
            self.blink(True)
        if show:
            self.show()
            vp.show(vol, __doc__, axes=1)
            if self.raise_window:
                self.raise_()

    def closeEvent(self, event):
        self.scale = 1.0
        self.fixed_size = None

        if self.vtkWidget is not None:
            self.vtkWidget.Finalize()

    def setImageAndParams(self, image, show=True, scale=None, position=None, size=None, hq=None, message=None,
                          blink=False):
        if size:
            self.fixed_size = size
        if position:
            self.move(*position)
        if hq is not None:
            if hq:
                self.quality = Qt.SmoothTransformation
            else:
                self.quality = Qt.FastTransformation
        if message is not None:
            self.message = message
        self.setImageVtk(image, show=show, scale=scale, blink=blink)

    def setZoom(self, scale):
        self.setParams(scale=scale)

    def setRotation(self, rotation):
        self.setParams(rotation=rotation)

    def setParams(self, scale=None, rotation=None):
        assert isinstance(self.image, QPixmap)

        if scale is None: scale = self.scale
        if rotation is None: rotation = self.rotation

        if scale != 1.0 or rotation:
            transform = QTransform().rotate(rotation).scale(scale, scale)
            pixmap = self.image.transformed(transform, self.quality)
        else:
            pixmap = self.image

        w = pixmap.width()
        h = pixmap.height()

        self.scale = scale
        self.rotation = rotation
        self.preview.setPixmap(pixmap)
        self.preview.setFixedSize(pixmap.size())

        if not self.fixed_size:
            self.resize(w, h)

    def autoSize(self):
        # size = self.image.size()
        # w = size.width()
        # h = size.height()
        return 500, 500

    def wheelEvent(self, event):
        assert isinstance(event, QWheelEvent)
        event.accept()

        if event.angleDelta().y() > 0:
            s = 1.1
        else:
            s = 1 / 1.1
        self.setZoom(s * self.scale)

        scrollX = self.scrollarea.horizontalScrollBar().value()
        posX = event.x()
        newX = s * (scrollX + posX) - posX
        self.scrollarea.horizontalScrollBar().setValue(int(newX))

        scrollY = self.scrollarea.verticalScrollBar().value()
        posY = event.y()
        newY = s * (scrollY + posY) - posY
        self.scrollarea.verticalScrollBar().setValue(int(newY))

        self.blink(False)

    def mousePressEvent(self, event):
        assert isinstance(event, QMouseEvent)
        self.key_signal.emit(KEY_MOUSE, event.x(), event.y())
        self.blink(False)
        event.accept()

    def keyPressEvent(self, event):
        assert isinstance(event, QKeyEvent)
        self.key_signal.emit(int(event.key()), 0, 0)
        self.blink(False)
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()

    def moveEvent(self, event):
        self.move_signal.emit()

    def contextMenuEvent(self, event):
        assert isinstance(event, QContextMenuEvent)

        self.blink(False)

        menu = QMenu()

        copy = menu.addAction("Copy to clipboard")

        reset = menu.addAction("Reset view")

        hq = menu.addAction("High quality")
        hq.setCheckable(True)
        if self.quality == Qt.SmoothTransformation:
            hq.setChecked(True)

        fixed = menu.addAction("Fixed size")
        fixed.setCheckable(True)
        if self.fixed_size:
            fixed.setChecked(True)

        rotate_right = menu.addAction("Rotate +")
        rotate_left = menu.addAction("Rotate -")

        save = menu.addAction("Save...")

        quit = menu.addAction("Close")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == quit:
            self.close()
        elif action == reset:
            self.setParams(1, 0)
        elif action == hq:
            if self.quality == Qt.SmoothTransformation:
                self.quality = Qt.FastTransformation
            else:
                self.quality = Qt.SmoothTransformation
            self.setZoom(self.scale)
        elif action == rotate_right:
            rotation = (self.rotation + 90) % 360
            self.setRotation(rotation)
        elif action == rotate_left:
            rotation = (self.rotation + 270) % 360
            self.setRotation(rotation)
        elif action == save:
            filename, filter = QFileDialog.getSaveFileName(self, "Save image...",
                                                           filter="*.png;;*.jpg;;*.bmp;;*.tiff;;*.gif",
                                                           directory=self.last_save_dir)
            if filename:
                try:
                    if not str(filename).endswith(filter[1:]):
                        filename = filename + filter[1:]
                    PreviewWindow.last_save_dir = path.dirname(str(filename))
                    success = self.image.save(filename, quality=100)
                    if not success: raise Exception("unknown error")
                except Exception as e:
                    QMessageBox.critical(self, "Saving error", "Cannot save.\nError: {}".format(e.message))
                    print("Saving error:", e)
        elif action == fixed:
            if self.fixed_size:
                self.fixed_size = None
            else:
                self.fixed_size = self.size()
        elif action == copy:
            print("copy")
            clipboard = QApplication.instance().clipboard()
            clipboard.setPixmap(self.image)

    def blink(self, enable):
        if enable:
            self.blink_timer.start()
        else:
            self.blink_timer.stop()
            self.blink_widget.hide()

    @pyqtSlot()
    def blink_(self):
        if self.blink_widget.isHidden():
            self.blink_widget.show()
        else:
            self.blink_widget.hide()


class ActionImageVtk(ActionImage):
    def __init__(self, image_preview):

        self.visualisation_dialog = None
        self.visualisation_option_added = False

        super(ActionImageVtk, self).__init__(image_preview)

        # self.visualisation_option()

    def visualisation_option(self, arr):
        if not self.visualisation_option_added and self.is_image_3d(arr):
            self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
            action = QAction('VTK visualisation', self)
            action.triggered.connect(self.open_visualisation_dialog_vtk)
            self.addAction(action)

            self.visualisation_option_added = True

    def set_image(self, arr):
        self.visualisation_option(arr)
        arr = self.set_3d_image_params(arr)

        # remember not to modify arr !!!
        if self.data_type != ActionImage.DATA_TYPE_IMAGE:
            self.prepare_actions()
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

    def is_image_3d(self, arr):
        if arr is not None and len(arr.shape) == 3 and arr.shape[2] != 3:
            return True
        return False

    @pyqtSlot()
    def open_visualisation_dialog_vtk(self):
        print("AND IT WORKS")
        if not self.get_connected() and self.element.diagram is not None:
            self.element.diagram.element_deleted.connect(self.on_element_destroy)
            self.set_connected(True)
        if self.visualisation_dialog is None:
            # image = self.set_3d_image_params(self.image_preview.get_preview_objects()[self.id])
            image = self.image_preview.get_preview_objects()[self.id]
            self.visualisation_dialog = image_preview.manager.manager.window_vtk(self.name + "_visualisation", image=image,
                                                                                 position='cursor')
            self.visualisation_dialog.setImageVtk(image)
            settings = config.ConfigWrapper.get_settings()
            if bool(strtobool(settings.get_with_default(config.VIEW_SECTION, config.PREVIEW_ON_TOP_OPTION))):
                flags = self.visualisation_dialog.windowFlags()
                flags |= QtCore.Qt.WindowStaysOnTopHint
                self.visualisation_dialog.setWindowFlags(flags)
                self.visualisation_dialog.showNormal()
            self.visualisation_dialog.installEventFilter(self)
            self.previews_container.visualisation_dialog_count += 1

    def close_visualisation_dialog_vtk(self):
        if self.visualisation_dialog is not None:
            self.visualisation_dialog.close()
            self.visualisation_dialog = None
            self.previews_container.visualisation_dialog_count -= 1
            if self.previews_container.visualisation_dialog_count < 0:
                self.previews_container.visualisation_dialog_count = 0

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Close and self.image_dialog is not None:
            self.close_image_dialog()
            return True
        if event.type() == QtCore.QEvent.Close and self.visualisation_dialog is not None:
            self.close_visualisation_dialog_vtk()
            return True
        return False

    @pyqtSlot(Element)
    def on_element_destroy(self, element):
        if element is self.element and self.image_dialog is not None:
            self.close_image_dialog()
        if element is self.element and self.visualisation_dialog is not None:
            self.close_visualisation_dialog_vtk()

    def deleteLater(self):
        QObject.deleteLater(self)
        if self.image_dialog is not None:
            self.close_image_dialog()
        if self.visualisation_dialog is not None:
            self.close_visualisation_dialog_vtk()


class OutputPreviewVtk(QHBoxLayout):
    default_image = None
    preview_callbacks = [
        (np.ndarray, ActionImageVtk.set_image),
        (str, ActionImageVtk.set_text),
        (bool, ActionImageVtk.set_bool)
    ]

    def __init__(self, output, previews_container):
        super(OutputPreviewVtk, self).__init__()
        if not self.default_image:
            self.default_image = QPixmap(CVLAB_DIR + "/images/default.png")
        self.output = output
        self.previews_container = previews_container
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setContentsMargins(0, 0, 0, 0)
        self.base_spacing = 4
        self.previews = []
        self.previews.append(ActionImageVtk(self))
        self.img = self.default_image
        self.previews[0].setPixmap(self.img)

        self.all_layouts = []
        self.image_3d_controls_layouts_bool = []
        self.actual_param_3d_image = []
        self.actual_controls_3d_image = []

        self.prepare_3d_image_controls(0)

    def add_3d_image_controls(self, image_id):
        if not self.image_3d_controls_layouts_bool[image_id]:
            self.all_layouts[image_id].addLayout(self.actual_controls_3d_image[image_id][0])
            self.all_layouts[image_id].addLayout(self.actual_controls_3d_image[image_id][1])
            self.image_3d_controls_layouts_bool[image_id] = True

    def prepare_3d_image_controls(self, image_id):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.previews[image_id])

        self.actual_param_3d_image.append(
            [FloatParameter("slice", min_=0, max_=1, step=0.01),
             ComboboxParameter("axis", [("Z", 0), ("Y", 1), ("X", 2)])])
        self.actual_controls_3d_image.append(
            [GuiFloatParameter(self.actual_param_3d_image[image_id][0], self.previews[image_id].element),
             GuiComboboxParameter(self.actual_param_3d_image[image_id][1], self.previews[image_id].element)])
        for param in self.actual_param_3d_image[image_id]:
            param.value_changed.connect(self.previews[image_id].previews_container.update)

        self.image_3d_controls_layouts_bool.append(False)
        self.all_layouts.append(layout)
        self.addLayout(layout)

    def update(self, forced=False):
        objects = self.get_preview_objects()
        if not objects:
            objects = [None]
        self.adjust_number_of_previews(objects)
        for i, obj in enumerate(objects):
            if forced or self.previews_container.isVisible() or self.previews[i].image_dialog is not None:
                for _type, callback in self.preview_callbacks:
                    if isinstance(obj, _type):
                        callback(self.previews[i], obj)

    def get_preview_objects(self):
        return self.output.get().desequence_all()

    def adjust_number_of_previews(self, preview_images):
        while len(preview_images) > len(self.previews):
            new_label = ActionImageVtk(self)
            self.addWidget(new_label)
            self.previews.append(new_label)

            index = len(self.previews) - 1
            self.prepare_3d_image_controls(index)

        while len(preview_images) < len(self.previews):
            label_out = self.previews[-1]
            self.previews.pop(-1)
            self.actual_param_3d_image.pop(-1)
            self.actual_controls_3d_image.pop(-1)
            self.image_3d_controls_layouts_bool.pop(-1)
            self.all_layouts[-1].deleteLater()
            self.all_layouts.pop(-1)
            # todo: again - a memory leak?
            label_out.deleteLater()

    def set_outdated(self):
        # todo: implement this
        pass


def create_previews(self, layout):
    for output in self.outputs:
        if not output.preview_enabled:
            continue
        preview = OutputPreviewVtk(output, self)
        self.previews.append(preview)
        layout.addLayout(preview)


def window_vtk(self, winname, **kwargs):
    print("window vtk")
    winname = str(winname)
    with self.lock:
        if winname not in self.windows:
            position = kwargs.pop('position', 'auto')
            if position == 'auto':
                position = self.positions.get(winname, self.find_best_place())
            window = self.windows[winname] = PreviewWindowVtk(self, winname, position=position, **kwargs)
            window.key_signal.connect(self.key_slot)
            window.move_signal.connect(self.save_positions)
        return self.windows[winname]


setattr(PreviewsContainer, "visualisation_dialog_count", 0)
setattr(PreviewsContainer, "create_previews", create_previews)
setattr(WindowManager, "window_vtk", window_vtk)
#setattr(ActionImage, "visualisation_option_added", False)
#setattr(ActionImage, "visualisation_option", visualisation_option)
# setattr(ActionImage, "open_visualisation_dialog_vtk", ActionImageVtk.open_visualisation_dialog_vtk)

#setattr(OutputPreview, "adjust_number_of_previews", adjust_number_of_previews_with_visualisation)

#OutputPreview.preview_callbacks.append((np.ndarray, add_menu_vis))


