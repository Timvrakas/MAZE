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
        self.img.label = self._add_group('CAHVOR_CAMERA_MODEL')
        self.img.label = self._add_group('PHOTOGRAMMETRY_CAMERA_MODEL')
        self.img.label['IMAGE']['IMAGE_CREATION_TIME'] = pds_date
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
        elif group_name == 'CAHVOR_CAMERA_MODEL':
            self.img.label['BEGIN_GROUP'] = 'CAHVOR_CAMERA_MODEL'
            self.img.label['MODEL_TYPE'] = 'CAHVOR'
            self.img.label['MODEL_COMPONENT_ID'] = [
                "C", "A", "H", "V", "O", "R"]
            self.img.label['MODEL_COMPONENT_NAME'] = ["CENTER", "AXIS",
                                                      "HORIZONTAL",
                                                      "VERTICAL", "OPTICAL_AXIS", "DISTORTION_COEFFICIENTS"]
            cahv = CAHVmodel.compute(self.yaml_data['Camera'])
            print("Printing CAHV")
            print(cahv)
            print("TESTING CAHVOR")
            C = compute_coordinates(cahv.C, self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            A = compute_coordinates(cahv.A, self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            H = compute_coordinates(cahv.H, self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            V = compute_coordinates(cahv.V, self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            O = compute_coordinates(cahv.O, self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            R = cahv.R
            # print("Printing A vector")
            # print(cahv.A)
            # print("Printing O vector")
            # print(cahv.O)
            print("Printing R vector")
            print(cahv.R)

            # This is how I would print 'O' vector directly i.e. without changing the camera_orientation.py
            #my_test_object = CAHVmodel(self.yaml_data['Camera'])
            #my_test = my_test_object._cahv
            #print("Printing O vector")
            # print(my_test['O'])

            self.img.label['MODEL_COMPONENT_1'] = C.tolist()
            self.img.label['MODEL_COMPONENT_2'] = A.tolist()
            self.img.label['MODEL_COMPONENT_3'] = H.tolist()
            self.img.label['MODEL_COMPONENT_4'] = V.tolist()
            self.img.label['MODEL_COMPONENT_5'] = O.tolist()
            if(R == None):
                self.img.label['MODEL_COMPONENT_6'] = R
            else:
                self.img.label['MODEL_COMPONENT_6'] = R.tolist()
            self.img.label['END_GROUP'] = 'CAHVOR_CAMERA_MODEL'
        elif group_name == 'PHOTOGRAMMETRY_CAMERA_MODEL':
            self.img.label['BEGIN_GROUP'] = 'PHOTOGRAMMETRY_CAMERA_MODEL'
            self.img.label['MODEL_TYPE'] = 'PHOTOGRAMMETRY'
            self.img.label['MODEL_COMPONENT_ID'] = [
                "C", "F", "PxS", "ImS", "P", "ANG"]
            self.img.label['MODEL_COMPONENT_NAME'] = ["CENTER", "FOCAL_LENGTH",
                                                      "PIXEL_SIZE",
                                                      "IMAGE_SIZE",
                                                      "PRINICIPAL",
                                                      "ROTATION_ANGLES"]
            print("TESTING COLLINEARITY")
            test_object = CAHVmodel(self.yaml_data['Camera'])
            test = test_object._cahv_input
            #print("Printing CENTER")
            # print(test['center'])
            C = test['center']
            F = test['f']
            PxS = test['pixelsize']
            ImS = test['image_size']
            P = test['principal']
            ANG = None
            print("Printing Principal")
            print(ImS)
            # ang = test[]
            self.img.label['MODEL_COMPONENT_1'] = C
            self.img.label['MODEL_COMPONENT_2'] = F
            self.img.label['MODEL_COMPONENT_3'] = PxS
            self.img.label['MODEL_COMPONENT_4'] = ImS
            self.img.label['MODEL_COMPONENT_5'] = P.tolist()
            self.img.label['MODEL_COMPONENT_6'] = ANG
            self.img.label['END_GROUP'] = 'PHOTOGRAMMETRY_CAMERA_MODEL'
        stream = io.BytesIO()
        pvl.dump(self.img.label, stream)
        stream.seek(0)
        label_list = list(pvl.load(stream))
        l = len(label_list)
        label_list[l-2], label_list[l-1] = label_list[l-1], label_list[l-2]
        label = pvl.PVLModule(label_list)
        # print(label)
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
