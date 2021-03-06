# -*- coding: utf-8 -*-
from stereosim.compute_coordinates import compute_coordinates
from stereosim.camera_orientation import CAHVmodel
import numpy as np
from planetaryimage import PDS3Image
from PIL import Image
import exifread
import argparse
import os.path
import six
import yaml
import pvl
import io


class PDSGenerator(PDS3Image):
    def __init__(self, filepath):
        pds_date = self._convert_date(filepath)
        print('pds_date:', pds_date)
        jpg_im = Image.open(filepath)
        np_ar = np.asarray(jpg_im)
        dim = np_ar.shape
        new_ar = np.zeros((dim[2], dim[0], dim[1]))
        new_ar[0, :, :] = np_ar[:, :, 0]
        new_ar[1, :, :] = np_ar[:, :, 1]
        new_ar[2, :, :] = np_ar[:, :, 2]
        new_ar = new_ar.astype('>i2')
        # call __init__ of planetaryimage's class
        super().__init__(new_ar)
        self.filename = os.path.splitext(filepath)[0]
        if self._label_file_exists():
            self.label = self._update_labelPDSG(pds_date)
        self.save(self.filename + '.IMG')

    def _label_file_exists(self):
        """
        Checks whether label file for given JPG Images exists or not.

        Returns:
        True: if label file is present in the same path
        False: if label file does not exist in the same path
        """
        self.label_file = self.filename + '.lbl'
        if os.path.isfile(self.label_file):
            return True
        else:
            return False

    def _update_labelPDSG(self, pds_date):
        """
        Updates label by adding groups and comments into it.
        1. PTU_ARTICULATION_STATE
        2. CAHVOR_CAMERA_MODEL_LEFT
        3. And so on

        Returns:
        label: PVLModule
            Returns updated image label.
        """
        with open(self.label_file, 'r') as fp:
            try:
                self.yaml_data = yaml.load(fp)
            except yaml.YAMLError as exc:
                print(exc)
        self.label = self._add_group('PTU_ARTICULATION_STATE')
        if self.yaml_data['Camera'] == 'LEFT':
            self.label = self._add_group('CAHVOR_CAMERA_MODEL_LEFT')
            self.label = self._add_group('COLLINEAR_CAMERA_MODEL_LEFT')
            #self.label = self._add_group('LCAM_EL_TRANSLATION')
            #self.label = self._add_group('LCAM_AZ_TRANSLATION')
        if self.yaml_data['Camera'] == 'RIGHT':
            self.label = self._add_group('CAHVOR_CAMERA_MODEL_RIGHT')
            self.label = self._add_group('COLLINEAR_CAMERA_MODEL_RIGHT')
            #self.label = self._add_group('RCAM_EL_TRANSLATION')
            #self.label = self._add_group('RCAM_AZ_TRANSLATION')
        #self.label = self._add_group('RSM_COORDINATE_SYSTEM')
        #self.label = self._add_group('PTU_AXES_HEIGHTS')
        self.label = self._add_group('ROVER_FRAME')
        self.label = self._add_group('SITE_FRAME')
        self.label['IMAGE']['IMAGE_CREATION_TIME'] = pds_date
        return self.label

    def _add_group(self, group_name):
        """
        Adds PVLGroup into label.

        Parameters
        ----------
        group_name: String
            Name of the group to be added.

        Returns:
        --------
        label: PVLModule
            Returns label after adding PVLGroup in it.
        """
        if group_name == 'PTU_ARTICULATION_STATE':
            self.label['BEGIN_GROUP'] = 'PTU_ARTICULATION_STATE'
            self.label['ARTICULATION_DEVICE_ID'] = "PTU"
            self.label['ARTICULATION_DEVICE_NAME'] = "FLIR Pan-Tilt Unit"
            self.label['ARTICULATION_DEVICE_ANGLE'] = [
                round(self.yaml_data['AZIMUTH']), round(self.yaml_data['ELEVATION'])]
            self.label['ARTICULATION_DEVICE_ANGLE_NAME'] = [
                "AZIMUTH-MEASURED", "ELEVATION-MEASURED"]
            #self.label['PP'] = int(self.yaml_data['PP'])
            #self.label['TP'] = int(self.yaml_data['TP'])
            #self.label['AZIMUTH'] = self.yaml_data['AZIMUTH']
            #self.label['ELEVATION'] = self.yaml_data['ELEVATION']
            self.label['ARTICULATION_DEVICE_MODE'] = 'DEPLOYED'
            self.label['END_GROUP'] = 'PTU_ARTICULATION_STATE'

        elif group_name == 'CAHVOR_CAMERA_MODEL_LEFT':
            self.label['BEGIN_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'
            self.label['MODEL_TYPE'] = 'CAHVOR'
            self.label['MODEL_COMPONENT_ID'] = ["C", "A", "H", "V", "O", "R"]
            self.label['MODEL_COMPONENT_NAME'] = ["CENTER", "AXIS",
                                                  "HORIZONTAL", "VERTICAL",
                                                  "OPTICAL_AXIS", "DISTORTION_COEFFICIENTS"]
            self.label['MODEL_COMPONENT_UNIT'] = [
                "METER", "N/A", "PIXEL", "PIXEL", "N/A", "N/A"]
            cahv = CAHVmodel.compute(self.yaml_data['Camera'])

            C = [0, 0, 0]
            A = [0.999762, 0.021815, 0.000000]
            H = [1429.297020, 3942.905305, 0.000000]
            V = [1043.675052, 22.773071, 3910.787050]
            O = [0.999762, 0.021815, 0.000000]
            R = [0, 0.164600, -0.084529]
            Hc = 1522.659078
            Vc = 1041.005182
            Vs = 3886.530592
            V1 = 0.166722249
            TV = [0, 0.11, -0.144]
            Q = [0, -0.9999, 0, -0.0109]

            self.label['MODEL_COMPONENT_1'] = C
            self.label['MODEL_COMPONENT_2'] = A
            self.label['MODEL_COMPONENT_3'] = H
            self.label['MODEL_COMPONENT_4'] = V
            self.label['MODEL_COMPONENT_5'] = O
            self.label['MODEL_COMPONENT_6'] = R
            self.label['MODEL_TRANSFORM_VECTOR'] = TV
            self.label['MODEL_TRANSFORM_VECTOR_UNIT'] = 'METER'
            self.label['MODEL_TRANSFORM_QUATERNION'] = Q
            self.label['END_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'

        elif group_name == 'CAHVOR_CAMERA_MODEL_RIGHT':
            self.label['BEGIN_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'
            self.label['MODEL_TYPE'] = 'CAHVOR'
            self.label['MODEL_COMPONENT_ID'] = ["C", "A", "H", "V", "O", "R"]
            self.label['MODEL_COMPONENT_NAME'] = ["CENTER", "AXIS",
                                                  "HORIZONTAL", "VERTICAL",
                                                  "OPTICAL_AXIS", "DISTORTION_COEFFICIENTS"]
            self.label['MODEL_COMPONENT_UNIT'] = [
                "METER", "N/A", "PIXEL", "PIXEL", "N/A", "N/A"]

            cahv = CAHVmodel.compute(self.yaml_data['Camera'])

            C = [0, 0.252, 0]
            A = [0.999762, -0.021815, 0.000000]
            H = [1614.223560, 3839.925763, 0.000000]
            V = [1042.262663, -22.742252, 3874.226066]
            O = [0.999762, -0.021815, 0.000000]
            R = [0, 0.169487, -0.100739]
            Hc = 1516.339359
            Vc = 1038.826689
            Vs = 3912.148959
            V1 = 0.166722334
            TV = [0, 0.11, 0.108]
            Q = [0, 0.9999, 0, -0.0109]

            self.label['MODEL_COMPONENT_1'] = C
            self.label['MODEL_COMPONENT_2'] = A
            self.label['MODEL_COMPONENT_3'] = H
            self.label['MODEL_COMPONENT_4'] = V
            self.label['MODEL_COMPONENT_5'] = O
            self.label['MODEL_COMPONENT_6'] = R
            self.label['MODEL_TRANSFORM_VECTOR'] = TV
            self.label['MODEL_TRANSFORM_VECTOR_UNIT'] = 'METER'
            self.label['MODEL_TRANSFORM_QUATERNION'] = Q
            self.label['END_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'

        elif group_name == 'COLLINEAR_CAMERA_MODEL_LEFT':
            self.label['BEGIN_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'
            self.label['MODEL_TYPE'] = 'COLLINEAR'
            self.label['MODEL_COMPONENT_ID'] = [
                "C", "F", "f", "PxS", "P", "ANG", "ROT_MAT", "k"]
            self.label['MODEL_COMPONENT_NAME'] = ["CENTER", "FOCAL_LENGTH", "fx/fy", "PIXEL_SIZE",
                                                  "PRINCIPAL", "ROT_ANG[OMEGA,PHI,KAPPA]", "ROTATION_MATRIX", "DISTORTION_COEFFICIENTS"]

            self.label['MODEL_COMPONENT_UNIT'] = ["METER", "MILLIETER",
                                                  "PIXEL", "MILLIMETER", "MILLIMETER", "DEGREE", "RADIANS", "N/A"]
            C = [0, 0, 0]
            F = 28.939824
            f = [3910.787050, 3910.787050]
            PxS = [0.0074, 0.0074]
            P = [-0.155615, -0.147434]
            ANG = [0, -1.25, 0]
            ROT_MAT = [[0.999762, 0, 0.021815], [
                0, -1.0, 0], [0.021815, 0, -0.999762]]
            k = [0.000201221865, -0.000000179738162, 0.000000000291226599]

            self.label['MODEL_COMPONENT_1'] = C
            self.label['MODEL_COMPONENT_2'] = F
            self.label['MODEL_COMPONENT_3'] = f
            self.label['MODEL_COMPONENT_4'] = PxS
            self.label['MODEL_COMPONENT_5'] = P
            self.label['MODEL_COMPONENT_6'] = ANG
            self.label['MODEL_COMPONENT_7'] = ROT_MAT
            self.label['MODEL_COMPONENT_8'] = k
            self.label['END_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'

        elif group_name == 'COLLINEAR_CAMERA_MODEL_RIGHT':
            self.label['BEGIN_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'
            self.label['MODEL_TYPE'] = 'COLLINEAR'
            self.label['MODEL_COMPONENT_ID'] = [
                "C", "F", "f", "PxS", "P", "ANG", "ROT_MAT", "k"]
            self.label['MODEL_COMPONENT_NAME'] = ["CENTER", "FOCAL_LENGTH", "fx/fy", "PIXEL_SIZE",
                                                  "PRINCIPAL", "ROT_ANG[OMEGA,PHI,KAPPA]", "ROTATION_MATRIX", "DISTORTION_COEFFICIENTS"]

            self.label['MODEL_COMPONENT_UNIT'] = ["METER", "MILLIMETER",
                                                  "PIXEL", "MILLIMETER", "MILLIMETER", "DEGREE", "RADIANS", "N/A"]
            C = [0, 0.252, 0]
            F = 28.669273
            f = [3874.226066, 3874.226066]
            PxS = [0.0074, 0.0074]
            P = [-0.043868, -0.136980]
            ANG = [0, 1.25, 0]
            ROT_MAT = [[0.999762, 0, -0.021815],
                       [0, -1, 0], [-0.021815, 0, -0.999762]]
            k = [0.000199562771, -0.0000000467599006, -0.000000000439101069]

            self.label['MODEL_COMPONENT_1'] = C
            self.label['MODEL_COMPONENT_2'] = F
            self.label['MODEL_COMPONENT_3'] = f
            self.label['MODEL_COMPONENT_4'] = PxS
            self.label['MODEL_COMPONENT_5'] = P
            self.label['MODEL_COMPONENT_6'] = ANG
            self.label['MODEL_COMPONENT_7'] = ROT_MAT
            self.label['MODEL_COMPONENT_8'] = k
            self.label['END_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'

        elif group_name == 'RCAM_EL_TRANSLATION':
            self.label['BEGIN_GROUP'] = 'RCAM_EL_TRANSLATION'
            self.label['COORDINATE_SYSTEM_NAME'] = 'RC_HEAD_FRAME'
            self.label['ORIGIN_OFFSET_VECTOR'] = [0.0, 0.108, -0.11]
            self.label['ORIGIN_OFFSET_VECTOR_INDEX'] = ['X', 'Y', 'Z']
            self.label['ORIGIN_OFFSET_VECTOR_UNIT'] = "METERS"
            self.label['ORIGIN_ROTATION_QUATERION'] = [1, 0, 0, 0]
            self.label['ORIGIN_ANGULAR_OFFSET'] = [1.25]
            self.label['ORIGIN_ANGULAR_OFFSET_UNIT'] = 'DEGREES'
            self.label['POSITIVE_ELEVATION_DIRECTION'] = "UP"
            self.label['REFERENCE_COORD_SYSTEM_NAME'] = 'PTU_ELEVATION_AXIS'
            self.label['END_GROUP'] = 'RCAM_EL_TRANSLATION'

        elif group_name == 'LCAM_EL_TRANSLATION':
            self.label['BEGIN_GROUP'] = 'LCAM_EL_TRANSLATION'
            self.label['COORDINATE_SYSTEM_NAME'] = 'LC_HEAD_FRAME'
            self.label['ORIGIN_OFFSET_VECTOR'] = [0.0, -0.144, -0.11]
            self.label['ORIGIN_OFFSET_VECTOR_INDEX'] = ['X', 'Y', 'Z']
            self.label['ORIGIN_OFFEST_VECTOR_UNIT'] = "METERS"
            self.label['ORIGIN_ROTATION_QUATERION'] = [1, 0, 0, 0]
            self.label['ORIGIN_ANGULAR_OFFSET'] = [-1.25]
            self.label['ORIGIN_ANGULAR_OFFSET_UNIT'] = 'DEGREES'
            self.label['POSITIVE_ELEVATION_DIRECTION'] = "UP"
            self.label['REFERENCE_COORD_SYSTEM_NAME'] = 'PTU_ELEVATION_AXIS'
            self.label['END_GROUP'] = 'LCAM_EL_TRANSLATION'

        elif group_name == 'RCAM_AZ_TRANSLATION':
            self.label['BEGIN_GROUP'] = 'RCAM_AZ_TRANSLATION'
            self.label['COORDINATE_SYSTEM_NAME'] = 'RC_HEAD_FRAME'
            self.label['ORIGIN_OFFSET_VECTOR'] = [0.0, 0.108, -0.2398]
            self.label['ORIGIN_OFFSET_VECTOR_INDEX'] = ['X', 'Y', 'Z']
            self.label['ORIGIN_OFFSET_VECTOR_UNIT'] = "METERS"
            self.label['POSITIVE_ELEVATION_DIRECTION'] = "UP"
            self.label['ORIGIN_ROTATION_QUATERION'] = [1, 0, 0, 0]
            self.label['ORIGIN_ANGULAR_OFFSET'] = [1.25]
            self.label['ORIGIN_ANGULAR_OFFSET_UNIT'] = 'DEGREES'
            self.label['REFERENCE_COORD_SYSTEM_NAME'] = 'PTU_AZIMUTH_AXIS'
            self.label['END_GROUP'] = 'RCAM_AZ_TRANSLATION'

        elif group_name == 'LCAM_AZ_TRANSLATION':
            self.label['BEGIN_GROUP'] = 'LCAM_AZ_TRANSLATION'
            self.label['COORDINATE_SYSTEM_NAME'] = 'LC_HEAD_FRAME'
            self.label['ORIGIN_OFFSET_VECTOR'] = [0.0, 0.108, -0.2398]
            self.label['ORIGIN_OFFSET_VECTOR_INDEX'] = ['X', 'Y', 'Z']
            self.label['ORIGIN_OFFSET_VECTOR_UNIT'] = "METERS"
            self.label['ORIGIN_ROTATION_QUATERION'] = [1, 0, 0, 0]
            self.label['ORIGIN_ANGULAR_OFFSET'] = [-1.25]
            self.label['ORIGIN_ANGULAR_OFFSET_UNIT'] = 'DEGREES'
            self.label['POSITIVE_ELEVATION_DIRECTION'] = "UP"
            self.label['REFERENCE_COORD_SYSTEM_NAME'] = 'PTU_AZIMUTH_AXIS'
            self.label['END_GROUP'] = 'LCAM_AZ_TRANSLATION'

        elif group_name == 'PTU_AXES_HEIGHTS':
            self.label['BEGIN_GROUP'] = 'PTU_AXES_HEIGHTS'
            self.label['COORD_SYS_UNIT'] = 'METERS'
            self.label['AZ_AXIS_HEIGHT'] = '1.305'
            self.label['EL_AXIS_HEIGHT'] = '1.4348'
            self.label['OPTICAL_CENTER_HEIGHT'] = '1.5448'
            self.label['REFERENCE_COORDINATE_SYSTEM'] = 'GROUND_BENEATH_TRIPOD'
            self.label['END_GROUP'] = 'PTU_AXES_HEIGHTS'

        # This one is pointing of CAMERAS wrt rover frame (TRIPOD).
        elif group_name == 'ROVER_FRAME':
            self.label['BEGIN_GROUP'] = 'ROVER_DERIVED_GEOMETRY_PARMS'
            self.label['INSTRUMENT_AZIMUTH'] = '{} <deg>'.format(
                round(self.yaml_data['AZIMUTH']))
            self.label['INSTRUMENT_ELEVATION'] = '{} <deg>'.format(
                round(self.yaml_data['ELEVATION']))
            self.label['POSITIVE_AZIMUTH_DIRECTION'] = 'CLOCKWISE'
            self.label['ORIGIN_ANGULAR_OFFSET_UNIT'] = 'DEGREES'
            self.label['REFERENCE_COORD_SYSTEM_INDEX'] = [
                1, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            self.label['REFERENCE_COORD_SYSTEM_NAME'] = "ROVER_NAV_FRAME"
            self.label['END_GROUP'] = 'ROVER_DERIVED_GEOMETRY_PARMS'

        # This one is pointing of cameras wrt to site frame
        elif group_name == 'SITE_FRAME':
            self.label['BEGIN_GROUP'] = 'SITE_DERIVED_GEOMETRY_PARMS'
            self.label['INSTRUMENT_AZIMUTH'] = 'null <deg>'
            self.label['INSTRUMENT_ELEVATION'] = 'null <deg>'
            self.label['POSITIVE_AZIMUTH_DIRECTION'] = "CLOCKWISE"
            self.label['REFERENCE_COORD_SYSTEM_INDEX'] = '1'
            self.label['REFERENCE_COORD_SYSTEM_NAME'] = "SITE_FRAME"
            self.label['END_GROUP'] = "SITE_DERIVED_GEOMETRY_PARMS"

        stream = io.BytesIO()
        with open(self.filename + '.IMG', 'w+b') as stream:
            # use our own PDS3 encoder class so we can add comment lines
            pvl.dump(self.label, stream, cls=PDS3LabelEncoder)
            stream.seek(0)
            label_list = list(pvl.load(stream))
        l = len(label_list)
        label_list[l-2], label_list[l-1] = label_list[l-1], label_list[l-2]
        label = pvl.PVLModule(label_list)
        return label

    def _create_label(self, array):
        """
        Override PDS3Image._create_label() method to reflect desired label attributes.

        Parameters
        ----------


        Returns
        -------
        PVLModule label for the given NumPy array.
        """
        if len(array.shape) == 3:
            bands = array.shape[0]
            lines = array.shape[1]
            line_samples = array.shape[2]
        else:
            bands = 1
            lines = array.shape[0]
            line_samples = array.shape[1]
        record_bytes = line_samples * array.itemsize
        print("array.itemsize:", array.itemsize)
        label_module = pvl.PVLModule([
            ('ODL_VERSION_ID', 'ODL3'),
            ('RECORD_TYPE', 'FIXED_LENGTH'),
            ('RECORD_BYTES', record_bytes),
            ('LABEL_RECORDS', 1),
            ('DATA_SET_ID', 'UNK'),
            ('PRODUCT_ID', 'UNK'),
            ('INSTRUMENT_HOST_NAME', 'MARS 2020'),
            ('INSTRUMENT_NAME', 'STEREOSIM'),
            ('TARGET_NAME', 'MARS'),
            ('START_TIME', 'UNK'),
            ('STOP_TIME', 'UNK'),
            ('SPACECRAFT_CLOCK_START_COUNT', 'UNK'),
            ('SPACECRAFT_CLOCK_STOP_COUNT', 'UNK'),
            ('PRODUCT_CREATION_TIME', 'UNK'),
            ('^IMAGE', 1),
            ('IMAGE',
                pvl.PVLModule([('BANDS', bands),
                               ('BAND_STORAGE_TYPE', 'BAND_SEQUENTIAL'),
                               ('FIRST_LINE', 1),
                               ('FIRST_LINE_SAMPLE', 1),
                               ('LINES', lines),
                               ('LINE_SAMPLES', line_samples),
                               ('SAMPLE_BITS', array.itemsize * 8),
                               ('SAMPLE_TYPE', 'MSB_INTEGER')])
             )])
        return self._update_label(label_module, array)

    def _update_label(self, label, array):
        """Update PDS3 label for NumPy Array.
        It is called by '_create_label' to update label values
        such as,
        - ^IMAGE, RECORD_BYTES
        - STANDARD_DEVIATION
        - MAXIMUM, MINIMUM
        - MEDIAN, MEAN

        ** Currently lines are commented out because these values are not desired by users.
        Returns
        -------
        Update label module for the NumPy array.
        Usage: self.label = self._update_label(label, array)
        """
        maximum = float(np.max(array))
        mean = float(np.mean(array))
        median = float(np.median(array))
        minimum = float(np.min(array))
        stdev = float(np.std(array, ddof=1))

        encoder = pvl.encoder.PDSLabelEncoder
        serial_label = pvl.dumps(label, cls=encoder)
        label_sz = len(serial_label)
        image_pointer = int(label_sz / label['RECORD_BYTES']) + 1

        label['^IMAGE'] = image_pointer + 1
        label['LABEL_RECORDS'] = image_pointer

        return label

    def _convert_date(self, filepath):
        """
        Access the image acquisition time from intial image
        and convert to PDS format for storage in PDS header.
        Also collect focal length from exif header.

        As of this writing:
        EXIF data format: 2017:02:21 12:36:11
        PDS date format:  2017-02-21T12:36:11.sssZ
        See: https://pds.jpl.nasa.gov/documents/sr/stdref3.7/Chapter07.pdf

        Parameters
        ----------
        filepath: string
            Path to the file that is being convert to PDS

        Returns
        -------
        pds_date: string
            Image acquisition time in PDS format
        fl : string
            focal length of lens read by camera.
        """
        with open(filepath, 'rb') as f:
            meta = exifread.process_file(f, details=False)
        date = '{}'.format(meta['EXIF DateTimeOriginal'])
        print('date exif format:', date)

        # Identify parts of the date for PDS application
        yr = date[0:4]
        mo = date[5:7]
        d = date[8:10]
        hr = date[11:13]
        m = date[14:16]
        s = date[17:19]
        pds_date = yr + '-' + mo + '-' + d + 'T' + hr + ':' + m + ':' + s + '.sssZ'
        print('date pds format:', pds_date)
        return pds_date

    def _save(self, file_to_write, overwrite):
        """
        Redefine _save() used in PDS3Image() so it does not overwrite the comment
        lines we add in with PDS3LabelEncoder()
        """
# if overwrite:
##            file_to_write = self.filename
# elif os.path.isfile(file_to_write):
# msg = 'File ' + file_to_write + ' already exists !\n' + \
##                  'Call save() with "overwrite = True" to overwrite the file.'
##            raise IOError(msg)

# with open(file_to_write, 'a+b') as stream:
        encoder = PDS3LabelEncoder
        serial_label = pvl.dumps(self.label, cls=encoder)
        label_sz = len(serial_label)
        image_pointer = int(label_sz / self.label['RECORD_BYTES']) + 1
        self.label['^IMAGE'] = image_pointer + 1

        if self._sample_bytes != self.label['IMAGE']['SAMPLE_BITS'] * 8:
            self.label['IMAGE']['SAMPLE_BITS'] = self.data.itemsize * 8

        sample_type_to_save = self.DTYPES[self._sample_type[0] +
                                          self.dtype.kind]
        self.label['IMAGE']['SAMPLE_TYPE'] = sample_type_to_save

        if len(self.data.shape) == 3:
            self.label['IMAGE']['BANDS'] = self.data.shape[0]
            self.label['IMAGE']['LINES'] = self.data.shape[1]
            self.label['IMAGE']['LINE_SAMPLES'] = self.data.shape[2]
        else:
            self.label['IMAGE']['BANDS'] = 1
            self.label['IMAGE']['LINES'] = self.data.shape[0]
            self.label['IMAGE']['LINE_SAMPLES'] = self.data.shape[1]

        diff = 0
        if len(pvl.dumps(self.label, cls=encoder)) != label_sz:
            diff = abs(label_sz - len(pvl.dumps(self.label, cls=encoder)))
        pvl.dump(self.label, file_to_write, cls=encoder)
        offset = image_pointer * self.label['RECORD_BYTES'] - label_sz
        stream = open(file_to_write, 'a')
        for i in range(0, offset+diff):
            stream.write(" ")

        if (self._bands > 1 and self._format != 'BAND_SEQUENTIAL'):
            raise NotImplementedError
        else:
            self.data.tofile(stream, format='%' + self.dtype.kind)
        stream.close()


class PDS3LabelEncoder(pvl.PVLEncoder):
    """
    Redefine some of PVLEncoder's methods as well as PDSLabelEncoder methods so we can add comment lines between sections
    """
    begin_comment = b'/* '
    end_comment = b' */'
    new_line = b'\r\n'
    begin_group = b'GROUP'
    begin_object = b'OBJECT'

    comments = {
        'DATA_SET_ID': b'IDENTIFICATION DATA ELEMENTS',
        'FILTER_NAME': b'DESCRIPTIVE DATA ELEMENTS'
    }

    # Allow comments to be encoded as well
    def encode_block(self, block, level, stream):
        for key, value in six.iteritems(block):
            if key in self.comments:
                self.encode_comment(key, self.comments[key], level, stream)
            self.encode_statement(key, value, level, stream)

    def encode_comment(self, key, comment, level, stream):
        stream.write(self.newline)
        stream.write(self.begin_comment)
        stream.write(comment)
        stream.write(self.end_comment)
        stream.write(self.newline)
        stream.write(self.newline)

    # These four methods are brought in from pvl.PDSLabelEncoder to help format the label
    # in the way PDS/IDL desires.
    def _detect_assignment_col(self, block, indent=0):
        if not block:
            return 0
        block_items = six.iteritems(block)
        return max(self._key_length(k, v, indent) for k, v in block_items)

    def _key_length(self, key, value, indent):
        length = indent + len(key)

        if isinstance(value, dict):
            indent += len(self.indentation)
            return max(length, self._detect_assignment_col(value, indent))

        return length

    def encode(self, module, stream):
        self.assignment_col = self._detect_assignment_col(module)
        super(PDS3LabelEncoder, self).encode(module, stream)
        stream.write(self.newline)

    def encode_raw_assignment(self, key, value, level, stream):
        indented_key = (level * self.indentation) + key
        stream.write(indented_key.ljust(self.assignment_col))
        stream.write(self.assignment)
        stream.write(value)
        stream.write(self.newline)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    args = parser.parse_args()
    PDSGenerator(args.filepath)
