# -*- coding: utf-8 -*-
from stereosim.compute_coordinates import compute_coordinates
from stereosim.camera_orientation import CAHVmodel
import numpy as np
from planetaryimage import PDS3Image
from PIL import Image
import exifread
import argparse
import os.path
import yaml
import pvl
import io


class PDSGenerator(object):
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
        self.img = PDS3Image(new_ar)
        self.filename = os.path.splitext(filepath)[0]
        if self._label_file_exists():
            self.img.label = self._update_label(pds_date)
        self.img.save(self.filename + '.IMG')

    def _label_file_exists(self):
        """
        Checks whether label file for given JPG Images exists or not.

        Returns:
        1: if label file is present in the same path
        0: if label file does not exist in the same path
        """
        self.label_file = self.filename + '.lbl'
        if os.path.isfile(self.label_file):
            return 1
        else:
            return 0

    def _update_label(self, pds_date):
        """
        Updates label by addiing 2 gruops into it.
        1. PTU_ARTICULATION_STATE
        2. CAHVOR_CAMERA_MODEL

        Returns:
        label: PVLModule
            Returns updated image label.
        """
        with open(self.label_file, 'r') as fp:
            try:
                self.yaml_data = yaml.load(fp)
            except yaml.YAMLError as exc:
                print(exc)
        self.img.label = self._add_group('IDENTIFICATION_DATA_ELEMENTS')
        self.img.label = self._add_group('PTU_ARTICULATION_STATE')
        self.img.label = self._add_group('CAHVOR_CAMERA_MODEL_LEFT')
        self.img.label = self._add_group('CAHVOR_CAMERA_MODEL_RIGHT')
        # self.img.label = self._add_group('PHOTOGRAMMETRY_CAMERA_MODEL')
        self.img.label['IMAGE']['IMAGE_CREATION_TIME'] =  pds_date
        return self.img.label

    def _add_group(self, group_name):
        """
        Adds PVLGroup into label.

        Parameters
        ----------
        group_name: String
            Name of the group to be added.

        Returns:
        label: PVLModule
            Returns label after adding PVLGroup in it.
        """
        if group_name == 'IDENTIFICATION_DATA_ELEMENTS':
            self.img.label['BEGIN_GROUP'] = 'IDENTIFICATION_DATA_ELEMENTS'
            self.img.label['DATA_SET_ID'] = 'UNK'
            self.img.label['PRODUCT_ID'] = 'UNK'
            self.img.label['INSTRUMENT_HOST_NAME'] = 'MARS 2020'
            self.img.label['INSTRUMENT_NAME'] = 'STEREOSIM'
            self.img.label['TARGET_NAME'] = 'MARS'
            self.img.label['START_TIME'] = 'UNK'
            self.img.label['STOP_TIME'] = 'UNK'
            self.img.label['SPACECRAFT_CLOCK_START_COUNT'] = 'UNK'
            self.img.label['SPACECRAFT_CLOCK_STOP_COUNT'] = 'UNK'
            self.img.label['PRODUCT_CREATION_TIME'] = 'UNK'
            self.img.label['END_GROUP'] = 'IDENTIFICATION_DATA_ELEMENTS'

        elif group_name == 'PTU_ARTICULATION_STATE':
            self.img.label['BEGIN_GROUP'] = 'PTU_ARTICULATION_STATE'
            self.img.label['ARTICULATION_DEVICE_ID'] = "PTU"
            self.img.label['ARTICULATION_DEVICE_NAME'] = "FLIR Pan-Tilt Unit"
            self.img.label['PP'] = int(self.yaml_data['PP'])
            self.img.label['TP'] = int(self.yaml_data['TP'])
            self.img.label['AZIMUTH'] = self.yaml_data['AZIMUTH']
            self.img.label['ELEVATION'] = self.yaml_data['ELEVATION']
            self.img.label['END_GROUP'] = 'PTU_ARTICULATION_STATE'

        elif group_name == 'CAHVOR_CAMERA_MODEL_LEFT':
            self.img.label['BEGIN_GROUP'] = 'CAHVOR_CAMERA_MODEL_LEFT'
            self.img.label['MODEL_TYPE'] = 'CAHVOR'
            self.img.label['MODEL_COMPONENT_ID'] = ["C", "A", "H", "V", "O", "R", "Hc", "Vc", "Vs", "V1", "F", "ImS", "PxS", "P", "ANG"]
            self.img.label['MODEL_COMPONENT_NAME'] = ["CENTER", "AXIS",
                                                      "HORIZONTAL", "VERTICAL",
                                                      "OPTICAL_AXIS", "DISTORTION_COEFFICIENTS",
                                                      "HORIZONTAL_OPTICAL_CENTER", "VERTICAL_OPTICAL_CENTER",
                                                      "Vs", "V1",
                                                      "FOCAL_LENGTH", "IMAGE_SIZE",
                                                      "PIXEL_SIZE", "PRINICIPAL", "ROTATION_ANGLES"]
            cahv = CAHVmodel.compute(self.yaml_data['Camera'])

            C = [3.451904, 3.258335, 1.254338]
            A = [-0.698217, -0.681994, -0.217661]
            H = [-3768.955776, 1750.845082, -391.3237751]
            V = [-78.87639227, -162.8340073, -4019.463883]
            O = [-0.698217, -0.681994595, -0.21766119]
            R = [0, 0.169540938, -0.091659605]
            Hc = 1522.659078
            Vc = 1041.005182
            Vs = 3886.530592
            V1 = 0.166722249
            F = 28.76033845
            ImS = [3072, 2048]
            PxS = [0.0074, 0.0074]
            P = [-0.098722821, -0.125838347]
            ANG = [-72.29916094, 44.2841281, 166.5327547]

            self.img.label['MODEL_COMPONENT_1'] = C
            self.img.label['MODEL_COMPONENT_2'] = A
            self.img.label['MODEL_COMPONENT_3'] = H
            self.img.label['MODEL_COMPONENT_4'] = V
            self.img.label['MODEL_COMPONENT_5'] = O
            self.img.label['MODEL_COMPONENT_6'] = R
            self.img.label['MODEL_COMPONENT_7'] = Hc
            self.img.label['MODEL_COMPONENT_8'] = Vc
            self.img.label['MODEL_COMPONENT_9'] = V1
            self.img.label['MODEL_COMPONENT_10'] = F
            self.img.label['MODEL_COMPONENT_11'] = ImS
            self.img.label['MODEL_COMPONENT_12'] = Vc
            self.img.label['MODEL_COMPONENT_13'] = V1
            self.img.label['MODEL_COMPONENT_14'] = F
            self.img.label['MODEL_COMPONENT_15'] = ImS
            self.img.label['END_GROUP'] = 'CAHVOR_CAMERA_MODEL_LEFT'

        elif group_name == 'CAHVOR_CAMERA_MODEL_RIGHT':
            self.img.label['BEGIN_GROUP'] = 'CAHVOR_CAMERA_MODEL_RIGHT'
            self.img.label['MODEL_TYPE'] = 'CAHVOR'
            self.img.label['MODEL_COMPONENT_ID'] = ["C", "A", "H", "V", "O", "R", "Hc", "Vc", "Vs", "V1", "F", "ImS", "PxS", "P", "ANG"]
            self.img.label['MODEL_COMPONENT_NAME'] = ["CENTER", "AXIS",
                                                      "HORIZONTAL", "VERTICAL",
                                                      "OPTICAL_AXIS", "DISTORTION_COEFFICIENTS",
                                                      "HORIZONTAL_OPTICAL_CENTER", "VERTICAL_OPTICAL_CENTER",
                                                      "Vs", "V1",
                                                      "FOCAL_LENGTH", "IMAGE_SIZE",
                                                      "PIXEL_SIZE", "PRINICIPAL", "ROTATION_ANGLES"]
            cahv = CAHVmodel.compute(self.yaml_data['Camera'])

            C = [3.451904, 3.258335, 1.254338]
            A = [-0.698217, -0.681994595, -0.21766119]
            H = [-3782.37833, 1773.539076, -390.3432399]
            V = [-73.08384812, -157.7415041, -4043.988964]
            O = [-0.698217, -0.681994595, -0.21766119]
            R = [0, 0.167802847, -0.091829942]
            Hc = 1516.339359
            Vc = 1038.826689
            Vs = 3912.148959
            V1 = 0.166722334
            F = 28.9499023
            ImS = [3072, 2048]
            PxS = [0.0074, 0.0074]
            P = [-0.14548874, -0.1097175]
            ANG = [-72.2993175, 44.2841281, 166.5327547]

            self.img.label['MODEL_COMPONENT_1'] = C
            self.img.label['MODEL_COMPONENT_2'] = A
            self.img.label['MODEL_COMPONENT_3'] = H
            self.img.label['MODEL_COMPONENT_4'] = V
            self.img.label['MODEL_COMPONENT_5'] = O
            self.img.label['MODEL_COMPONENT_6'] = R
            self.img.label['MODEL_COMPONENT_7'] = Hc
            self.img.label['MODEL_COMPONENT_8'] = Vc
            self.img.label['MODEL_COMPONENT_9'] = V1
            self.img.label['MODEL_COMPONENT_10'] = F
            self.img.label['MODEL_COMPONENT_11'] = ImS
            self.img.label['MODEL_COMPONENT_12'] = Vc
            self.img.label['MODEL_COMPONENT_13'] = V1
            self.img.label['MODEL_COMPONENT_14'] = F
            self.img.label['MODEL_COMPONENT_15'] = ImS
            self.img.label['END_GROUP'] = 'CAHVOR_CAMERA_MODEL_RIGHT'    

        stream = io.BytesIO()
        pvl.dump(self.img.label, stream)
        stream.seek(0)
        label_list = list(pvl.load(stream))
        l = len(label_list)
        label_list[l-2], label_list[l-1] = label_list[l-1], label_list[l-2]
        label = pvl.PVLModule(label_list)
        return label
    def _convert_date(self, filepath):
        """
        Access the image acquisition time from intial image
        and convert to PDS format for storage in PDS header.

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    args = parser.parse_args()
    PDSGenerator(args.filepath)
