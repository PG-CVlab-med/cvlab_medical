from threading import Thread

import numpy
from vtkmodules.util import numpy_support

from cvlab.diagram.elements.base import *
from vtkplotter import datadir, Plotter, Point, Volume, show

from cvlab_medical.med_visualisation_util import *

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import Qt

from cvlab.view.widgets import PreviewsContainer, OutputPreview


# def well_done():
#
# OutputPreview.preview_callbacks.append((np.ndarray, well_done))

class Image3DVisualisation(NormalElement):
    name = 'Image3DVisualisation'
    comment = 'test\n'

    def __init__(self):
        super().__init__()

    def get_attributes(self):
        return [Input("input")], [], []

    def process_inputs(self, inputs, outputs, parameters):
        data = inputs["input"].value

        imdata = vtk.vtkImageData()
        depthArray = numpy_support.numpy_to_vtk(data.ravel(order='F'), deep=True, array_type=vtk.VTK_DOUBLE)

        imdata.SetDimensions(data.shape)
        imdata.SetSpacing([1, 1, 1])
        imdata.SetOrigin([0, 0, 0])
        imdata.GetPointData().SetScalars(depthArray)

        colorFunc = vtk.vtkColorTransferFunction()
        colorFunc.AddRGBPoint(1, 1, 0.0, 0.0)  # Red
        colorFunc.AddRGBPoint(2, 0.0, 1, 0.0)  # Green

        opacity = vtk.vtkPiecewiseFunction()

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorFunc)
        volumeProperty.SetScalarOpacity(opacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.SetIndependentComponents(2)

        volumeMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
        volumeMapper.SetInputData(imdata)
        volumeMapper.SetBlendModeToMaximumIntensity()

        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

        ren = vtk.vtkRenderer()
        ren.AddVolume(volume)
        ren.SetBackground(0, 0, 0)

        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        renWin.SetSize(900, 900)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renWin)

        interactor.Initialize()
        renWin.Render()
        interactor.Start()


class Image3DVisualisation2(NormalElement):
    name = 'Image3DVisualisation2'
    comment = 'test\n'

    def __init__(self):
        super().__init__()

        a = self.preview.previews[0]
        #a.visualisation_option

        def empty_function():
            pass

        output_preview_callbacks = OutputPreview.preview_callbacks

        for index, item in enumerate(output_preview_callbacks, start=0):
            callback_class, function = item

            if callback_class == numpy.ndarray:
                print(index)

    def get_attributes(self):
        return [Input("input")], [Output("output")], []

    def process_inputs(self, inputs, outputs, parameters):
        data = inputs["input"].value

        outputs["output"] = Data(data)

        vol = Volume(data, c=['white', 'b', 'g', 'r'])
        vol.addScalarBar3D()
        vp = Plotter(verbose=0)

        # vp.show(vol, __doc__, axes=1)


register_elements_auto(__name__, locals(), "Medical Image Visualisation")

