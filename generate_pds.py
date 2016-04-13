# -*- coding: utf-8 -*-
import numpy as np
from planetaryimage import PDS3Image
from PIL import Image
import argparse
import os.path
import yaml
import pvl
import io


class GeneratePDS(object):
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
        self.img.label = self.update_label()
        self.img.save(self.filename + '.IMG')

    def update_label(self):
        label_file = self.filename + '.lbl'
        label = self.img.label
        if os.path.isfile(label_file):
            with open(label_file, 'r') as fp:
                try:
                    yaml_data = yaml.load(fp)
                except yaml.YAMLError as exc:
                    print(exc)
            label['BEGIN_GROUP'] = 'PTU_ARTICULATION_STATE'
            label['ARTICULATION_DEVICE_ID'] = "PTU"
            label['ARTICULATION_DEVICE_NAME'] = "FLIR Pan-Tilt Unit"
            label['PP'] = int(yaml_data['PP'])
            label['TP'] = int(yaml_data['TP'])
            label['AZIMUTH'] = yaml_data['AZIMUTH']
            label['ELEVATION'] = yaml_data['ELEVATION']
            label['END_GROUP'] = 'PTU_ARTICULATION_STATE'
            stream = io.BytesIO()
            pvl.dump(label, stream)
            stream.seek(0)
            label_list = list(pvl.load(stream))
            label_list[5], label_list[6] = label_list[6], label_list[5]
            label = pvl.PVLModule(label_list)
            # print(label)
        return label

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    args = parser.parse_args()
    GeneratePDS(args.filepath)
