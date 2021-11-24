from cvlab_medical.med_visualisation_utils.med_visualisation_classes import ThreadedElement, FunctionGuiElementVtk


class VisualisationElementVtk(FunctionGuiElementVtk, ThreadedElement):
    def __init__(self):
        super().__init__()

    def get_plotter(self, vol, qt_widget):
        return None

    def get_volume(self, image):
        return None

    def show_plotter(self, vp, vol):
        return None

    def visualization(self):
        self.preview.previews[0].previews[0].open_visualisation_dialog_vtk()
