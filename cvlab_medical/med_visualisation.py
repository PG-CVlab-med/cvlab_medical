import vtk
import vedo
import vedo.applications
from cvlab_medical.med_visualisation_util import *
from cvlab_medical.vedo_app_utils import IsosurfaceBrowserCustom, SlicerPlotterCustom

# class Image3DVisualisation(NormalElement):
#     name = 'Image3DVisualisation'
#     comment = 'test\n'
#
#     def __init__(self):
#         super().__init__()
#
#     def get_attributes(self):
#         return [Input("input")], [], []
#
#     def process_inputs(self, inputs, outputs, parameters):
#         data = inputs["input"].value
#
#         imdata = vtk.vtkImageData()
#         depthArray = numpy_support.numpy_to_vtk(data.ravel(order='F'), deep=True, array_type=vtk.VTK_DOUBLE)
#
#         imdata.SetDimensions(data.shape)
#         imdata.SetSpacing([1, 1, 1])
#         imdata.SetOrigin([0, 0, 0])
#         imdata.GetPointData().SetScalars(depthArray)
#
#         colorFunc = vtk.vtkColorTransferFunction()
#         colorFunc.AddRGBPoint(1, 1, 0.0, 0.0)  # Red
#         colorFunc.AddRGBPoint(2, 0.0, 1, 0.0)  # Green
#
#         opacity = vtk.vtkPiecewiseFunction()
#
#         volumeProperty = vtk.vtkVolumeProperty()
#         volumeProperty.SetColor(colorFunc)
#         volumeProperty.SetScalarOpacity(opacity)
#         volumeProperty.SetInterpolationTypeToLinear()
#         volumeProperty.SetIndependentComponents(2)
#
#         volumeMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
#         volumeMapper.SetInputData(imdata)
#         volumeMapper.SetBlendModeToMaximumIntensity()
#
#         volume = vtk.vtkVolume()
#         volume.SetMapper(volumeMapper)
#         volume.SetProperty(volumeProperty)
#
#         ren = vtk.vtkRenderer()
#         ren.AddVolume(volume)
#         ren.SetBackground(0, 0, 0)
#
#         renWin = vtk.vtkRenderWindow()
#         renWin.AddRenderer(ren)
#         renWin.SetSize(900, 900)
#
#         interactor = vtk.vtkRenderWindowInteractor()
#         interactor.SetRenderWindow(renWin)
#
#         interactor.Initialize()
#         renWin.Render()
#         interactor.Start()


class PlotterVedo(VisualisationElementVtk):
    name = 'PlotterVedo'
    comment = 'Visualisation of 3D image using vedo plotter.\n'

    def __init__(self):
        super().__init__()

    def get_attributes(self):
        return [Input("input")], [Output("output")], []

    def process_inputs(self, inputs, outputs, parameters):
        data = inputs["input"].value
        outputs["output"] = Data(data)

    def get_plotter(self, vol, qt_widget):
        return vedo.Plotter(qtWidget=qt_widget)

    def get_volume(self, image):
        vol = vedo.Volume(image, c=['white', 'b', 'g', 'r'])
        vol.addScalarBar3D()

        return vol

    def show_plotter(self, vp, vol):
        vp.show(vol, __doc__, axes=3)


class SlicePlotterVedo(VisualisationElementVtk):
    name = 'SlicePlotterVedo'
    comment = 'Slice visualisation of 3D image using vedo slice plotter.\n'

    def __init__(self):
        super().__init__()

    def get_attributes(self):
        return [Input("input")], [Output("output")], []

    def process_inputs(self, inputs, outputs, parameters):
        data = inputs["input"].value
        outputs["output"] = Data(data)

    def get_plotter(self, vol, qt_widget):
        return SlicerPlotterCustom( vol,
                     bg='white', bg2='lightblue',
                     cmaps=("gist_ncar_r","jet","Spectral_r","hot_r","bone_r"),
                     useSlider3D=False,
                     qtWidget=qt_widget
                   )

    def get_volume(self, image):
        vol = vedo.Volume(image, c=['white', 'b', 'g', 'r'])
        return vol

    def show_plotter(self, vp, vol):
        vp.show()


class IsosurfaceBrowserVedo(VisualisationElementVtk):
    name = 'IsosurfaceBrowser'
    comment = 'tmp\n'

    def __init__(self):
        super().__init__()

    def get_attributes(self):
        return [Input("input")], [Output("output")], []

    def process_inputs(self, inputs, outputs, parameters):
        data = inputs["input"].value
        outputs["output"] = Data(data)

    def get_plotter(self, vol, qt_widget):
        return IsosurfaceBrowserCustom(vol, c='gold', qtWidget=qt_widget)

    def get_volume(self, image):
        vol = vedo.Volume(image, c=['white', 'b', 'g', 'r'])
        return vol

    def show_plotter(self, vp, vol):
        vp.show(axes=7, bg2='lb')


register_elements_auto(__name__, locals(), "Medical Image Visualisation")

