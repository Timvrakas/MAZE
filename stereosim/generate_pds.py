# -*- coding: utf-8 -*-
from compute_coordinates import compute_coordinates
from camera_orientation import CAHVmodel
import numpy as np
from planetaryimage import PDS3Image
from PIL import Image
import argparse
import os.path
import yaml
import pvl
import io


class PDSGenerator(object):
    def __init__(self, filepath):
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
            self.img.label = self._update_label()
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

    def _update_label(self):
        """
        Updates label by addiing 2 gruops into it.
        1. PTU_ARTICULATION_STATE
        2. GEOMETRIC_CAMERA_MODEL

        Returns:
        label: PVLModule
            Returns updated image label.
        """
        with open(self.label_file, 'r') as fp:
            try:
                self.yaml_data = yaml.load(fp)
            except yaml.YAMLError as exc:
                print(exc)
        self.img.label = self._add_group('PTU_ARTICULATION_STATE')
        self.img.label = self._add_group('GEOMETRIC_CAMERA_MODEL')
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
        if group_name == 'PTU_ARTICULATION_STATE':
            self.img.label['BEGIN_GROUP'] = 'PTU_ARTICULATION_STATE'
            self.img.label['ARTICULATION_DEVICE_ID'] = "PTU"
            self.img.label['ARTICULATION_DEVICE_NAME'] = "FLIR Pan-Tilt Unit"
            self.img.label['PP'] = int(self.yaml_data['PP'])
            self.img.label['TP'] = int(self.yaml_data['TP'])
            self.img.label['AZIMUTH'] = self.yaml_data['AZIMUTH']
            self.img.label['ELEVATION'] = self.yaml_data['ELEVATION']
            self.img.label['END_GROUP'] = 'PTU_ARTICULATION_STATE'
        elif group_name == 'GEOMETRIC_CAMERA_MODEL':
            self.img.label['BEGIN_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'
            self.img.label['MODEL_TYPE'] = 'CAHV'
            self.img.label['MODEL_COMPONENT_ID'] = ["C", "A", "H", "V"]
            self.img.label['MODEL_COMPONENT_NAME'] = ["CENTER", "AXIS",
                                                      "HORIZONTAL",
                                                      "VERTICAL"]
            cahv = CAHVmodel.compute('/home/bvnayak/temp/cam_04_21/', 'LEFT')
            C = compute_coordinates(cahv.cahv['C'], self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            A = compute_coordinates(cahv.cahv['A'], self.yaml_data['AZIMUTH'],
                                   self.yaml_data['ELEVATION'])
            H = compute_coordinates(cahv.cahv['H'], self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            V = compute_coordinates(cahv.cahv['V'], self.yaml_data['AZIMUTH'],
                                    self.yaml_data['ELEVATION'])
            self.img.label['MODEL_COMPONENT_1'] = C.tolist()
            self.img.label['MODEL_COMPONENT_2'] = A.tolist()
            self.img.label['MODEL_COMPONENT_3'] = H.tolist()
            self.img.label['MODEL_COMPONENT_4'] = V.tolist()
            self.img.label['END_GROUP'] = 'GEOMETRIC_CAMERA_MODEL'
        stream = io.BytesIO()
        pvl.dump(self.img.label, stream)
        stream.seek(0)
        label_list = list(pvl.load(stream))
        l = len(label_list)
        label_list[l-2], label_list[l-1] = label_list[l-1], label_list[l-2]
        label = pvl.PVLModule(label_list)
        # print(label)
        return label

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    args = parser.parse_args()
    PDSGenerator(args.filepath)
