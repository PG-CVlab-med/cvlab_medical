import vedo
import vedo.applications

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from distutils.util import strtobool

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from cvlab.view import image_preview, config
from cvlab.view.widgets import ActionImage, OutputPreview
from .vedo_app_utils import IsosurfaceBrowserCustom
from .med_image_io import *
from cvlab.view.image_preview import *


def is_image_3d(arr):
    if arr is not None and len(arr.shape) == 3 and arr.shape[2] != 3:
        return True
    return False


# class PreviewWindowVtk(QFrame):
#     minsize = (32, 32)
#     maxsize = None
#     last_save_dir = ""
#     raise_window = False
#
#     key_signal = pyqtSignal(int, int, int)
#     move_signal = pyqtSignal()
#
#     def __init__(self, manager, name, image=None, message=None, position=None, size=None, high_quality=False):
#         # super(PreviewWindowVtk, self).__init__(manager, name, image, message, position, size, high_quality)
#         super(PreviewWindowVtk, self).__init__()
#         self.setObjectName("Visualisation window {}".format(name))
#         self.setWindowTitle(name)
#
#         self.vtkWidget = None
#
#         self.vol = None
#         self.vp = None
#
#         self.manager = manager
#
#         desktop = QApplication.instance().desktop()
#         if self.maxsize:
#             self.maxsize = QSize(*self.maxsize)
#         else:
#             self.maxsize = desktop.screenGeometry(desktop.screenNumber(self)).size() * 0.95
#
#         self.setMinimumSize(*self.minsize)
#         self.setMaximumSize(self.maxsize)
#
#         self.image = None
#         self.original = None
#         self.message = message
#         self.scale = 1.
#         self.rotation = 0
#         self.quality = Qt.SmoothTransformation if high_quality else Qt.FastTransformation
#         self.fixed_size = size
#
#         self.scrollarea = PreviewScrollArea()
#         self.scrollarea.setFrameStyle(0)
#         self.scrollarea.setFocusPolicy(Qt.NoFocus)
#
#         layout = QGridLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         self.setLayout(layout)
#         layout.addWidget(self.scrollarea, 0, 0)
#
#         self.preview = QLabel()
#         self.preview.setMouseTracking(False)
#         self.preview.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#         self.scrollarea.setWidget(self.preview)
#
#         self.message_label = QLabel(" ")
#         self.layout().addWidget(self.message_label, 0, 0, Qt.AlignTop)
#         self.message_label.setStyleSheet("QLabel {color:black;background:rgba(255,255,255,32)}")
#         self.message_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#         self.message_label.setText("")
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(4)
#         shadow.setColor(Qt.white)
#         shadow.setOffset(0, 0)
#         self.message_label.setGraphicsEffect(shadow)
#
#         self.blink_widget = QWidget()
#         self.blink_widget.hide()
#         self.blink_widget.setStyleSheet("border:3px solid red")
#         self.blink_timer = QTimer()
#         self.blink_timer.setInterval(1000)
#         self.blink_timer.timeout.connect(self.blink_)
#         layout.addWidget(self.blink_widget, 0, 0)
#
#         self.setVisualisation(image, show=False)
#
#         if image is not None and not size:
#             size = self.autoSize()
#
#         if size:
#             self.resize(*size)
#
#         if position == 'cursor':
#             position = (QCursor.pos().x() - self.size().width() // 2, QCursor.pos().y() - self.size().height() // 2)
#
#         if position:
#             self.move(*position)
#
#         self.showNormal()
#
#     def closeVtkWidget(self):
#         self.vp.close()
#
#         self.vol = None
#         self.vp = None
#
#         if self.vtkWidget is not None:
#             self.vtkWidget.Finalize()
#             del self.vtkWidget
#         self.vtkWidget = None
#
#     def setImage(self, image, show=True, scale=None, blink=False):
#         if image is None:
#             return
#         self.original = image
#         if isinstance(image, QImage):
#             image = QPixmap.fromImage(image)
#         elif isinstance(image, QPixmap):
#             pass
#         else:
#             image = array_to_pixmap(image)
#         self.image = image
#         if not scale:
#             scale = self.scale
#             if image.width() * scale > self.maxsize.width():
#                 scale = self.maxsize.width() / image.width()
#             if image.height() * scale > self.maxsize.height():
#                 scale = self.maxsize.height() / image.height()
#         self.setZoom(scale)
#         if self.message is not None:
#             self.message_label.setText(self.message)
#         if blink:
#             self.blink(True)
#         if show:
#             self.show()
#             if self.raise_window:
#                 self.raise_()
#
#
#     def setVisualisation(self, image, show=True, scale=None, blink=False, show_vis_function=None):
#         if image is None:
#             return
#
#         self.vtkWidget = QVTKRenderWindowInteractor(self)
#         self.vtkWidget.resize(512, 512)
#
#         self.vol = vedo.Volume(image, c=['white', 'b', 'g', 'r'])
#         self.vol.addScalarBar3D()
#         self.vp = vedo.Plotter(qtWidget=self.vtkWidget)
#
#         # vol = vedo.Volume(image, c=['white', 'b', 'g', 'r'])
#         # #vol.addScalarBar3D()
#         # vp = vedo.Plotter(qtWidget=self.vtkWidget)
#
#         # vol = vedo.Volume(image, c=['black', 'b', 'g', 'r'])
#         # vp = vedo.applications.SlicerPlotter(vol,
#         #                     bg='white', bg2='lightblue',
#         #                     cmaps=("gist_ncar_r", "jet", "Spectral_r", "hot_r", "bone_r"),
#         #                     useSlider3D=False
#         #                     )
#         #
#         # vp.show()
#
#         vol = vedo.Volume(image, c=['black', 'b', 'g', 'r'])
#         # plt = vedo.applications.IsosurfaceBrowser(vol, c='gold')
#         # plt.show(axes=7, bg2='lb')
#
#
#         plt = vedo.applications.RayCastPlotter(vol)  # Plotter instance
#         plt.show(viewup="z", bg='black', bg2='blackboard', axes=7)
#
#
#         self.layout().addWidget(self.vtkWidget, 0, 0)
#
#         # if blink:
#         #     self.blink(True)
#         # if show:
#         #     self.show()
#         #     if self.raise_window:
#         #         self.raise_()
#
#     def closeEvent(self, event):
#         self.scale = 1.0
#         self.fixed_size = None
#
#         self.closeVtkWidget()
#
#     def setImageAndParams(self, image, show=True, scale=None, position=None, size=None, hq=None, message=None,
#                           blink=False):
#         if size:
#             self.fixed_size = size
#         if position:
#             self.move(*position)
#         if hq is not None:
#             if hq:
#                 self.quality = Qt.SmoothTransformation
#             else:
#                 self.quality = Qt.FastTransformation
#         if message is not None:
#             self.message = message
#
#         #self.visualisation_dialog.set_visualisation_params(None, image)
#         self.setVisualisation(image, show=show, scale=scale, blink=blink)
#
#     def setZoom(self, scale):
#         self.setParams(scale=scale)
#
#     def setRotation(self, rotation):
#         self.setParams(rotation=rotation)
#
#     def setParams(self, scale=None, rotation=None):
#         assert isinstance(self.image, QPixmap)
#
#         if scale is None: scale = self.scale
#         if rotation is None: rotation = self.rotation
#
#         if scale != 1.0 or rotation:
#             transform = QTransform().rotate(rotation).scale(scale, scale)
#             pixmap = self.image.transformed(transform, self.quality)
#         else:
#             pixmap = self.image
#
#         w = pixmap.width()
#         h = pixmap.height()
#
#         self.scale = scale
#         self.rotation = rotation
#         self.preview.setPixmap(pixmap)
#         self.preview.setFixedSize(pixmap.size())
#
#         if not self.fixed_size:
#             self.resize(w, h)
#
#     def autoSize(self):
#         # size = self.image.size()
#         # w = size.width()
#         # h = size.height()
#         return 500, 500
#
#     def wheelEvent(self, event):
#         assert isinstance(event, QWheelEvent)
#         event.accept()
#
#         if event.angleDelta().y() > 0:
#             s = 1.1
#         else:
#             s = 1 / 1.1
#         self.setZoom(s * self.scale)
#
#         scrollX = self.scrollarea.horizontalScrollBar().value()
#         posX = event.x()
#         newX = s * (scrollX + posX) - posX
#         self.scrollarea.horizontalScrollBar().setValue(int(newX))
#
#         scrollY = self.scrollarea.verticalScrollBar().value()
#         posY = event.y()
#         newY = s * (scrollY + posY) - posY
#         self.scrollarea.verticalScrollBar().setValue(int(newY))
#
#         self.blink(False)
#
#     def mousePressEvent(self, event):
#         assert isinstance(event, QMouseEvent)
#         self.key_signal.emit(KEY_MOUSE, event.x(), event.y())
#         self.blink(False)
#         event.accept()
#
#     def keyPressEvent(self, event):
#         assert isinstance(event, QKeyEvent)
#         self.key_signal.emit(int(event.key()), 0, 0)
#         self.blink(False)
#         if event.key() == Qt.Key_Escape:
#             self.close()
#             event.accept()
#
#     def moveEvent(self, event):
#         self.move_signal.emit()
#
#     def contextMenuEvent(self, event):
#         assert isinstance(event, QContextMenuEvent)
#
#         self.blink(False)
#
#         menu = QMenu()
#
#         copy = menu.addAction("Copy to clipboard")
#
#         reset = menu.addAction("Reset view")
#
#         hq = menu.addAction("High quality")
#         hq.setCheckable(True)
#         if self.quality == Qt.SmoothTransformation:
#             hq.setChecked(True)
#
#         fixed = menu.addAction("Fixed size")
#         fixed.setCheckable(True)
#         if self.fixed_size:
#             fixed.setChecked(True)
#
#         rotate_right = menu.addAction("Rotate +")
#         rotate_left = menu.addAction("Rotate -")
#
#         save = menu.addAction("Save...")
#
#         quit = menu.addAction("Close")
#
#         action = menu.exec_(self.mapToGlobal(event.pos()))
#
#         if action == quit:
#             self.close()
#         elif action == reset:
#             self.setParams(1, 0)
#         elif action == hq:
#             if self.quality == Qt.SmoothTransformation:
#                 self.quality = Qt.FastTransformation
#             else:
#                 self.quality = Qt.SmoothTransformation
#             self.setZoom(self.scale)
#         elif action == rotate_right:
#             rotation = (self.rotation + 90) % 360
#             self.setRotation(rotation)
#         elif action == rotate_left:
#             rotation = (self.rotation + 270) % 360
#             self.setRotation(rotation)
#         elif action == save:
#             filename, filter = QFileDialog.getSaveFileName(self, "Save image...",
#                                                            filter="*.png;;*.jpg;;*.bmp;;*.tiff;;*.gif",
#                                                            directory=self.last_save_dir)
#             if filename:
#                 try:
#                     if not str(filename).endswith(filter[1:]):
#                         filename = filename + filter[1:]
#                     PreviewWindow.last_save_dir = path.dirname(str(filename))
#                     success = self.image.save(filename, quality=100)
#                     if not success: raise Exception("unknown error")
#                 except Exception as e:
#                     QMessageBox.critical(self, "Saving error", "Cannot save.\nError: {}".format(e.message))
#                     print("Saving error:", e)
#         elif action == fixed:
#             if self.fixed_size:
#                 self.fixed_size = None
#             else:
#                 self.fixed_size = self.size()
#         elif action == copy:
#             print("copy")
#             clipboard = QApplication.instance().clipboard()
#             clipboard.setPixmap(self.image)
#
#     def blink(self, enable):
#         if enable:
#             self.blink_timer.start()
#         else:
#             self.blink_timer.stop()
#             self.blink_widget.hide()
#
#     @pyqtSlot()
#     def blink_(self):
#         if self.blink_widget.isHidden():
#             self.blink_widget.show()
#         else:
#             self.blink_widget.hide()
#
#     def close(self):
#         self.closeVtkWidget()
#
#         super().close()


class PreviewWindowVtk(PreviewWindow):
    def __init__(self, manager, name, image=None, message=None, position=None, size=None, high_quality=False):
        super(PreviewWindowVtk, self).__init__(manager, name, image=None, message=None, position=None, size=None, high_quality=False)

        self.vtkWidget = None
        self.vol = None
        self.vp = None

        self.setVisualisation(image, show=False)

    def closeVtkWidget(self):
        self.vol = None
        if self.vp is not None:
            self.vp.close()
            self.vp = None
        if self.vtkWidget is not None:
            self.layout().removeWidget(self.vtkWidget)
            self.vtkWidget.Finalize()
            del self.vtkWidget
            self.vtkWidget = None

    def setVisualisation(self, image, show=True, scale=None, blink=False, element=None):
        if image is None:
            return

        if self.vtkWidget is None:
            self.vtkWidget = QVTKRenderWindowInteractor(self)
            self.vtkWidget.resize(512, 512)
            self.layout().addWidget(self.vtkWidget, 0, 0)

        if element is not None:
            self.vol = element.get_volume(image)
            self.vp = element.get_plotter(self.vol, self.vtkWidget)

        if blink:
            self.blink(True)
        if show:
            self.show()
            if element is not None:
                element.show_plotter(self.vp, self.vol)
            if self.raise_window:
                self.raise_()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.closeVtkWidget()

    # def setImageAndParams(self, image, show=True, scale=None, position=None, size=None, hq=None, message=None, blink=False):
    #     super().setImageAndParams(image, show, scale, position, size, hq, message, blink)
    #     #self.setVisualisation(image, show=show, scale=scale, blink=blink)

    def autoSize(self):
        return 512, 512

    def close(self):
        super().close()
        self.closeVtkWidget()


class ActionImageVtk(ActionImage):
    def __init__(self, image_preview):
        self.visualisation_dialog = None
        self.visualisation_option_added = False
        super(ActionImageVtk, self).__init__(image_preview)
        self.name = "{} {}, Visualisation {}".format(self.element.name, str(self.element.object_id),
                                                        image_preview.output.name)

    def visualisation_option(self, arr):
        if not self.visualisation_option_added and is_image_3d(arr):
            self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
            action = QAction('VTK visualisation', self)
            action.triggered.connect(self.open_visualisation_dialog_vtk)
            self.addAction(action)

            self.visualisation_option_added = True

    @pyqtSlot()
    def open_visualisation_dialog_vtk(self):
        if not self.get_connected() and self.element.diagram is not None:
            self.element.diagram.element_deleted.connect(self.on_element_destroy)
            self.set_connected(True)
        if self.visualisation_dialog is None:
            image = self.image_preview.get_preview_objects()[self.id]
            self.visualisation_dialog = image_preview.manager.manager.window_vtk(self.name + "_visualisation", image=image,
                                                                                 position='cursor')
            self.visualisation_dialog.setVisualisation(image, element=self.element)
            # settings = config.ConfigWrapper.get_settings()
            # if bool(strtobool(settings.get_with_default(config.VIEW_SECTION, config.PREVIEW_ON_TOP_OPTION))):
            #     flags = self.visualisation_dialog.windowFlags()
            #     flags |= QtCore.Qt.WindowStaysOnTopHint
            #     self.visualisation_dialog.setWindowFlags(flags)
            #     self.visualisation_dialog.showNormal()
            self.visualisation_dialog.installEventFilter(self)
            self.previews_container.visualisation_dialog_count += 1

    def close_visualisation_dialog_vtk(self):
        if self.visualisation_dialog is not None:
            self.visualisation_dialog.close()
            self.visualisation_dialog = None
            self.previews_container.visualisation_dialog_count -= 1
            if self.previews_container.visualisation_dialog_count < 0:
                self.previews_container.visualisation_dialog_count = 0

    def set_image(self, arr):
        self.visualisation_option(arr)

        super().set_image(arr)

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


class OutputPreviewVtk(OutputPreview):
    preview_callbacks_vtk = [
        (np.ndarray, ActionImageVtk.set_image),
        (str, ActionImageVtk.set_text),
        (bool, ActionImageVtk.set_bool)
    ]

    def __init__(self, output, previews_container):
        super(OutputPreviewVtk, self).__init__(output, previews_container)

        while len(self.previews) != 0:
            self.delete_old_init()

        self.previews = []
        self.previews.append(ActionImageVtk(self))
        self.previews[0].setPixmap(self.img)

        self.all_layouts = []
        self.image_3d_controls_layouts_bool = []
        self.actual_param_3d_image = []
        self.actual_controls_3d_image = []

        self.prepare_3d_image_controls(0)

    def adjust_number_of_previews(self, preview_images):
        while len(preview_images) > len(self.previews):
            new_label = ActionImageVtk(self)
            self.addWidget(new_label)
            self.previews.append(new_label)

            index = len(self.previews) - 1
            self.prepare_3d_image_controls(index)

        super().adjust_number_of_previews(preview_images)
        # or:
        # while len(preview_images) < len(self.previews):
        #     self.delete_old_init()

    def update(self, forced=False):
        objects = self.get_preview_objects()
        if not objects:
            objects = [None]
        self.adjust_number_of_previews(objects)
        for i, obj in enumerate(objects):
            if forced or self.previews_container.isVisible() or self.previews[i].image_dialog is not None:
                for _type, callback in self.preview_callbacks_vtk:
                    if isinstance(obj, _type):
                        callback(self.previews[i], obj)

    def delete_old_init(self):
        label_out = self.previews[-1]
        self.previews.pop(-1)
        self.actual_param_3d_image.pop(-1)
        self.actual_controls_3d_image.pop(-1)
        self.image_3d_controls_layouts_bool.pop(-1)
        self.all_layouts[-1].deleteLater()
        self.all_layouts.pop(-1)
        label_out.deleteLater()


class PreviewsContainerVtk(PreviewsContainer):
    def __init__(self, element, outputs):
        super(PreviewsContainerVtk, self).__init__(element, outputs)

        self.visualisation_dialog_count = 0

    def create_previews(self, layout):
        for output in self.outputs:
            if not output.preview_enabled:
                continue
            preview = OutputPreviewVtk(output, self)
            self.previews.append(preview)
            layout.addLayout(preview)


class GuiElementVtk(GuiElement):
    def __init__(self):
        super(GuiElementVtk, self).__init__()

    def create_preview(self, layout):
        self.preview = PreviewsContainerVtk(self, list(self.outputs.values()))
        layout.addWidget(self.preview)


class FunctionGuiElementVtk(GuiElementVtk):
    def __init__(self):
        super(FunctionGuiElementVtk, self).__init__()

        print("FunctionGuiElementVtk")

        vb_main = QVBoxLayout()
        hb_content = QHBoxLayout()
        hb_label = QHBoxLayout()
        vb_inputs = QVBoxLayout()
        vb_params = QVBoxLayout()
        vb_outputs = QVBoxLayout()
        vb_inputs.setAlignment(QtCore.Qt.AlignTop)
        vb_outputs.setAlignment(QtCore.Qt.AlignTop)

        hb_label.setContentsMargins(0,0,0,0)
        hb_label.setSpacing(0)

        w_params = QWidget()
        w_params.setLayout(vb_params)
        vb_params.setContentsMargins(0,0,0,0)
        vb_params.setSpacing(1)

        vb_inputs.base_contents_margins = [4, 4, 4, 4]
        vb_inputs.base_spacing = 4
        vb_outputs.base_contents_margins = [4, 4, 4, 4]
        vb_outputs.base_spacing = 4

        self.create_label(hb_label)
        self.create_params(w_params)
        self.create_inputs(vb_inputs)
        self.create_outputs(vb_outputs)
        hb_content.setSpacing(0)
        hb_content.setContentsMargins(0,0,0,0)
        hb_content.addLayout(vb_inputs)
        hb_content.addWidget(w_params)
        hb_content.addStretch(1)
        hb_content.addLayout(vb_outputs)
        vb_main.addLayout(hb_label)
        vb_main.addLayout(hb_content)
        vb_main.addWidget(self.status_bar)
        vb_main.setSizeConstraint(QLayout.SetFixedSize)
        vb_main.base_contents_margins = [0, 4, 0, 4]
        vb_main.base_spacing = 4
        self.setLayout(vb_main)

        self.create_preview(vb_main)
        self.create_switch_params_action()
        self.create_switch_preview_action()
        self.create_switch_sliders_action()
        self.create_menu_separator()
        self.create_duplicate_action()
        self.create_break_action()
        self.create_del_action()
        self.create_code_action()
        #self.setFocusPolicy(QtCore.Qt.ClickFocus + QtCore.Qt.TabFocus)
        #self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 1)     # enable showing focus on a Mac


class VisualisationElementVtk(FunctionGuiElementVtk, ThreadedElement):
    def __init__(self):
        super(VisualisationElementVtk, self).__init__()

    def get_plotter(self, vol, qt_widget):
        return None

    def get_volume(self, image):
        return None

    def show_plotter(self, vp, vol):
        return None


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


setattr(WindowManager, "window_vtk", window_vtk)

