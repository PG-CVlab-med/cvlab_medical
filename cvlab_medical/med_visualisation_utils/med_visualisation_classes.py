from distutils.util import strtobool

import vedo
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from cvlab.view import image_preview, config
from cvlab.view.image_preview import *
from cvlab.view.widgets import ActionImage, OutputPreview
from cvlab_medical.med_image_io import *
from cvlab_medical.med_visualisation_utils.med_internal_utils import is_image_3d


class PreviewWindowVtk(PreviewWindow):
    def __init__(self, manager, name, image=None, message=None, position=None, size=None, high_quality=False):
        super().__init__(manager, name, image=None, message=None, position=None, size=None, high_quality=False)

        self.vtkWidget = None
        self.vol = None
        self.vp = None

    def setVisualisation(self, image, show=True, blink=False, element=None):
        if image is None:
            return

        if self.vtkWidget is None:
            self.vtkWidget = QVTKRenderWindowInteractor(self)
            self.vtkWidget.resize(*self.autoSize())
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

    def isVedoPoltter(self):
        return isinstance(self.vp, vedo.plotter.Plotter)

    def resetCamera(self):
        if self.isVedoPoltter():
            self.vp.resetCamera()

    def wheelEvent(self, event):
        # this method should not be implemented for visualisation window
        # it adjust window in incorrect way
        pass

    def contextMenuEvent(self, event):
        assert isinstance(event, QContextMenuEvent)

        # implement context menu only for vedo
        if self.isVedoPoltter():
            self.blink(False)

            menu = QMenu()
            reset_camera = menu.addAction("Reset camera")
            screenshot = menu.addAction("Make screenshot")
            quit = menu.addAction("Close")

            action = menu.exec_(self.mapToGlobal(event.pos()))

            if action == quit:
                self.close()
            elif action == reset_camera:
                self.resetCamera()
            elif action == screenshot:
                filename, filter = QFileDialog.getSaveFileName(self, "Save screenshot",
                                                               filter="*.png;;*.jpg;;*.bmp;;*.tiff;;*.gif",
                                                               directory=self.last_save_dir)
                if filename:
                    try:
                        if not str(filename).endswith(filter[1:]):
                            filename = filename + filter[1:]
                        PreviewWindowVtk.last_save_dir = path.dirname(str(filename))
                        self.vp.screenshot(filename)
                    except Exception as e:
                        QMessageBox.critical(self, "Saving error", "Cannot save.\nError: {}".format(e.message))
                        print("Saving error:", e)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.closeVtkWidget()

    def closeVtkWidget(self):
        del self.vol
        self.vol = None

        if self.vp is not None:
            if self.isVedoPoltter():
                self.vp.close()
            del self.vp
            self.vp = None

        if self.vtkWidget is not None:
            self.layout().removeWidget(self.vtkWidget)
            self.vtkWidget.Finalize()
            del self.vtkWidget
            self.vtkWidget = None

    def close(self):
        self.closeVtkWidget()
        super().close()


class ActionImageVtk(ActionImage):
    def __init__(self, image_preview):
        self.visualisation_dialog = None
        self.visualisation_option_added = False
        super().__init__(image_preview)
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
        if not self._ActionImage__connected and self.element.diagram is not None:
            self.element.diagram.element_deleted.connect(self.on_element_destroy)
            self._ActionImage__connected = True
        if self.visualisation_dialog is None:
            image = self.image_preview.get_preview_objects()[self.id]
            if image is not None:
                self.visualisation_dialog = image_preview.manager.manager.window_vtk(self.name, image=image,
                                                                                     position='cursor')
                self.visualisation_dialog.setImage(self.set_3d_image_params(image))
                self.visualisation_dialog.setVisualisation(image, element=self.element)
                settings = config.ConfigWrapper.get_settings()
                if bool(strtobool(settings.get_with_default(config.VIEW_SECTION, config.PREVIEW_ON_TOP_OPTION))):
                    flags = self.visualisation_dialog.windowFlags()
                    flags |= QtCore.Qt.WindowStaysOnTopHint
                    flags |= QtCore.Qt.CustomizeWindowHint
                    flags |= QtCore.Qt.WindowMaximizeButtonHint
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
        super().__init__(output, previews_container)

        # clean up and initialization
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
        super().__init__(element, outputs)

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
        super().__init__()

    def create_preview(self, layout):
        self.preview = PreviewsContainerVtk(self, list(self.outputs.values()))
        layout.addWidget(self.preview)


class FunctionGuiElementVtk(GuiElementVtk):
    def __init__(self):
        super().__init__()

        vb_main = QVBoxLayout()
        hb_content = QHBoxLayout()
        hb_label = QHBoxLayout()
        vb_inputs = QVBoxLayout()
        vb_params = QVBoxLayout()
        vb_outputs = QVBoxLayout()
        vb_inputs.setAlignment(QtCore.Qt.AlignTop)
        vb_outputs.setAlignment(QtCore.Qt.AlignTop)

        hb_label.setContentsMargins(0, 0, 0, 0)
        hb_label.setSpacing(0)

        w_params = QWidget()
        w_params.setLayout(vb_params)
        vb_params.setContentsMargins(0, 0, 0, 0)
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
        hb_content.setContentsMargins(0, 0, 0, 0)
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
