from stereosim.cahvor import compute_CAHVOR

import numpy as np
import argparse
import yaml
import os


class CAHVmodel(object):

    @classmethod
    def compute(cls, camera_eye):
        """
        Generation of CAHV model from photogrammetric parameters.

        Parameters
        ----------
        camera_eye: str
            Takes camera eye as an input. ('LEFT' -or- 'RIGHT')

        Returns:
        cahv: dict
            Returns dict containing computed CAHV parameters from
            photogrammetric model.
        """
        return cls(camera_eye)

    def __init__(self, camera_eye):
        # Checkerboard pattern is kept almost vertical to the ground.
        # 1 Image is enough to get CAHVOR info.
        filepath = os.path.join(os.path.dirname(__file__))
        full_filepath = os.path.join(filepath, 'stereosim_model_v1.yml')
        with open(full_filepath, 'r') as fp:
            self._cam_model = yaml.load(fp)
        self._cahv_input = self._get_input(camera_eye)
        self._cahv = compute_CAHVOR(self._cahv_input)

    @property
    def C(self):
        """Returns Center Vector of CAHV model.
        """
        return self._cahv['C']

    @property
    def A(self):
        """Returns Axis Vector of CAHV model.
        """
        return self._cahv['A']

    @property
    def H(self):
        """Returns Horizontal Vector of CAHV model.
        """
        return self._cahv['H']

    @property
    def V(self):
        """Returns Vertical Vector of CAHV model.
        """
        return self._cahv['V']

    @property
    def O(self):
        """Returns Vertical Vector of CAHV model.
        """
        return self._cahv['O']    

    @property
    def R(self):
        """Returns Vertical Vector of CAHV model.
        """
        return self._cahv['R']    

    def _get_input(self, camera_eye):
        """
        Prepares Input dict required to compute CAHV.

        Parameters
        ----------
        camera_eye: str
            Takes camera eye as an input. ('LEFT' -or- 'RIGHT')

        Returns
        -------
        dict: dict
            Returns dictionary containing photogrammetric camera Parameters
            such as 'camera center', 'focallength', 'rotation matrix',
            'pixel size', 'principal point', 'image size' and 'az' and 'el'
            to be added to get back to origin position of PTU.
        """
        f = self._cam_model['f']
        # http://www.digicamdb.com/specs/canon_eos-d60/
        pixelsize = self._cam_model['pixelsize']
        image_size = self._cam_model['image_size']

        M = np.asarray(self._cam_model[camera_eye]['intrinsic'])
        center = self._cam_model[camera_eye]['center']
        rotation = np.asarray(self._cam_model[camera_eye]['extrinsic'])

        principal = np.zeros(2)
        principal[0], principal[1] = M[0][2], M[1][2]
        principal = principal * pixelsize
        # dict adds 2 more keywords named 'az' and 'el'
        # This is to recover back to main position.
        #
        # e.g. If we calibrate at AZ = -90, EL = 25
        # Our Input should be AZ = 90, EL = -25.
        input_dict = dict([('center', center),
                           ('image_size', image_size),
                           ('pixelsize', pixelsize),
                           ('principal', principal),
                           ('f', f),
                           ('rotation_mat', rotation),
                           ('az', self._cam_model['az_to_fix']),
                           ('el', self._cam_model['el_to_fix'])])
        return input_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    parser.add_argument('camera_eye', help='Camera Eye')
    args = parser.parse_args()
    cahv_parameters = CAHVmodel(args.filepath, args.camera_eye)
