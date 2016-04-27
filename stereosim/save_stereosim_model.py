# -*- coding: utf-8 -*-
from camera_calibrate import StereoCalibration
import numpy as np
import argparse
import yaml
import os


class StereosimModel(object):
    def __init__(self, filepath):
        """
        Saving photogrammetric model of stereo camera.

        Parameters
        ----------
        filepath: filepath containing stereocamera images.
            Filepath must contain 2 folders 'LEFT' and 'RIGHT
            e.g. for '/sample/path/LEFT' and 'sample/path/RIGHT',
            filepath should be '/sample/path/'

        Saves:
            Saves dict containing stereocamera model.
        """
        print('Creating Stereo Camera Model...')
        self._cal = StereoCalibration(filepath)
        print('Calibration Performed...')
        self.left_cam_model = self._make_model('LEFT')
        self.right_cam_model = self._make_model('RIGHT')
        self.f = 100.0
        # http://www.digicamdb.com/specs/canon_eos-60d/
        self.pixelsize = 0.00429
        self.image_size = [2048, 3072]
        self.az_to_fix = 90.00
        self.el_to_fix = 0.0
        print('Saving YAML file...')
        self._save_yaml_file()

    def _make_model(self, camera_eye):
        """
        Makes model for LEFT and RIGHT cameras.

        Parameters
        ----------
        camera_eye: str
            Takes camera eye as an input. ('LEFT' -or- 'RIGHT')

        Returns:
        model: dict
            Dict containing LEFT and RIGHT camera Parameters such as
            intrinsic, extrinsic and perscpective camera center.
        """
        cal = self._cal.camera_model
        if camera_eye == 'LEFT':
            model = dict([('intrinsic', cal['M1'].tolist()),
                          ('extrinsic', cal['rot_left'].tolist()),
                          ('center', [0.762, 1.4097, -3.3667])])
        if camera_eye == 'RIGHT':
            rotation = cal['rot_right']
            relative_rotation = np.array(cal['R'])
            rotation = np.dot(relative_rotation, rotation)
            model = dict([('intrinsic', cal['M1'].tolist()),
                          ('extrinsic', rotation.tolist()),
                          ('center', [0.762, -1.4097, -3.3667])])
        return model

    def _save_yaml_file(self):
        """
        Saves dictionary containing stereocamera model as yaml file.
        """
        contents = {
            'LEFT': self.left_cam_model,
            'RIGHT': self.right_cam_model,
            'f': self.f,
            'pixelsize': self.pixelsize,
            'image_size': self.image_size,
            'az_to_fix': self.az_to_fix,
            'el_to_fix': self.el_to_fix
        }
        yaml_path = os.path.join(os.path.dirname(__file__))
        yaml_filename = os.path.join(yaml_path, 'stereosim_model_v1.yml')
        with open(yaml_filename, 'w') as model_file:
            yaml.dump(contents, model_file, default_flow_style=False)
        print('YAML file saved.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    args = parser.parse_args()
    StereosimModel(args.filepath)
