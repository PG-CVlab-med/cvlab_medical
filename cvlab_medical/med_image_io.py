from cvlab.diagram.elements.base import *
import nibabel as nib
import pydicom


class DicomLoader3D(InputElement):
    name = 'DicomLoader3D'
    comment = 'Loads DICOM format images as 3D image\n' \
              'Finds all DICOM images from directory'

    def get_attributes(self):
        return [], [Output("output")], [DirectoryParameter("path", value=CVLAB_DIR + "/images")]

    def process_inputs(self, inputs, outputs, parameters):
        path = parameters["path"]
        files_list = [(path + '/' + s) for s in os.listdir(path)]

        file_dim = pydicom.read_file(files_list[0])

        # Load dimensions based on one of the images
        dims = (int(file_dim.Rows), int(file_dim.Columns), len(files_list))
        d = np.zeros(dims, dtype=file_dim.pixel_array.dtype)

        counter = 0
        for file_name in files_list:
            ds = pydicom.read_file(file_name)
            if ds.pixel_array.size == (dims[0] * dims[1]):  # for some sequences dimensions can differ
                d[:, :, files_list.index(file_name)] = ds.pixel_array
                counter += 1
        print("Number of image loaded:", counter)

        outputs["output"] = Data(d)


class DicomLoader2D(InputElement):
    name = 'DicomLoader2D'
    comment = 'Loads single DICOM format image\n'

    def get_attributes(self):
        return [], [Output("output")], [PathParameter("path", value=CVLAB_DIR + "/images")]

    def process_inputs(self, inputs, outputs, parameters):
        path = parameters["path"]

        ds = pydicom.read_file(path)
        d = np.array(ds.pixel_array)
        if d is not None:
            self.may_interrupt()
            outputs["output"] = Data(d)


class NiftiLoader3D(InputElement):
    name = 'NiftiLoader3D'
    comment = 'Loads 3D nifti format image \n'

    def get_attributes(self):
        attributes = [], [Output("output")], [PathParameter("path")]
        return attributes

    def process_inputs(self, inputs, outputs, parameters):
        path = parameters["path"]

        ds = nib.load(path)
        d = np.array(ds.dataobj)
        if d is not None:
            self.may_interrupt()
            outputs["output"] = Data(d)


register_elements_auto(__name__, locals(), "Medical Image IO")
