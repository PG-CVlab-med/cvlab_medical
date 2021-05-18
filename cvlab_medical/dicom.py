import pydicom
from vtkmodules.util import numpy_support

from cvlab.diagram.elements.base import *
from cvlab.diagram.elements.image_io import *
import vtk
class DicomLoader3D(InputElement):
    name = 'DicomLoader3D'
    comment = 'Loads DICOM format images as 3D image\n' \
              'Finds all DICOM images from directory'


    def get_attributes(self):
        return [], [Output("output")], [DirectoryParameter("path", value=CVLAB_DIR+"/images")]

    def process_inputs(self, inputs, outputs, parameters):
        path = parameters["path"]
        image = []

        filesList = [(path + '/' + s) for s in os.listdir(path)]
        #lstFilesDCM.sort

        fileDim = pydicom.read_file(filesList[0])

        # Load dimensions based on one of the images
        dims = (int(fileDim.Rows), int(fileDim.Columns), len(filesList))
        image = np.zeros(dims, dtype=fileDim.pixel_array.dtype)

        counter =0
        for fileName in filesList:
            ds = pydicom.read_file(fileName)
            if ds.pixel_array.size == (dims[0] * dims[1]):#dla roznych sekwencji moga sie roznic
                image[:, :, filesList.index(fileName)] = ds.pixel_array
                counter+=1
        print("Number of image loaded:", counter)

        outputs["output"] = Data(image)


class DicomLoader3D_NONDIRECTORY(InputElement):
    name = 'DicomLoader3D_NONDIRECTORY'
    comment = 'Loads DICOM format images as 3D image\n'


    def get_attributes(self):
        return [], [Output("output")], [MultiPathParameter("paths",value=[CVLAB_DIR+"/images/lena.jpg"]*10)]

    def process_inputs(self, inputs, outputs, parameters):
        paths = parameters["paths"]
        image = []

        filesList = sorted(paths)
        #lstFilesDCM.sort

        fileDim = pydicom.read_file(filesList[0])

        # Load dimensions based on one of the images
        dims = (int(fileDim.Rows), int(fileDim.Columns), len(filesList))
        image = np.zeros(dims, dtype=fileDim.pixel_array.dtype)

        counter =0
        for fileName in filesList:
            ds = pydicom.read_file(fileName)
            if ds.pixel_array.size == (dims[0] * dims[1]):#dla roznych sekwencji moga sie roznic
                image[:, :, filesList.index(fileName)] = ds.pixel_array
                counter+=1
        print("Number of image loaded:", counter)

        outputs["output"] = Data(image)


class DicomLoader2D(InputElement):
    name = 'DicomLoader2D'
    comment = 'Loads single DICOM format image\n'



    def get_attributes(self):
        return [], [Output("output")], [PathParameter("path", value=CVLAB_DIR+"/images")]

    def process_inputs(self, inputs, outputs, parameters):
        path = parameters["path"]
        image = []

        fileDCM = pydicom.read_file(path)
        dims = (int(fileDCM.Rows), int(fileDCM.Columns))
        #image = np.zeros(dims, dtype=fileDCM.pixel_array.dtype)
        image = fileDCM.pixel_array
        image=np.array(image)
        outputs["output"] = Data(image)



register_elements_auto(__name__, locals(), "DICOM", 5)
#register_elements_auto(__name__, locals(), "Image IO", 2)