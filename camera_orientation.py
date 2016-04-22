from camera_calibrate import StereoCalibration
from cahvor import compute_CAHVOR

import numpy as np
import cv2
import argparse


class CAHVmodel(object):

    @classmethod
    def compute(cls, filepath, camera_eye):
        """
        Generation of CAHV model from photogrammetric parameters.

        Parameters
        ----------
        filepath: filepath containing stereocamera images.
            Filepath must contain 2 folders 'LEFT' and 'RIGHT
            e.g. for '/sample/path/LEFT' and 'sample/path/RIGHT',
            filepath should be '/sample/path/'
        camera_eye: str
            Takes camera eye as an input. ('LEFT' -or- 'RIGHT')

        Returns:
        cahv: dict
            Returns dict containing computed CAHV parameters from
            photogrammetric model.
        """
        return cls(filepath, camera_eye)

    def __init__(self, filepath, camera_eye):
        # Checkerboard pattern is kept almost vertical to the ground.
        # 1 Image is enough to get CAHVOR info.
        self._cal = StereoCalibration(filepath)
        self._cam_model = self._cal.camera_model
        self._cahv_input = self._get_input(camera_eye)
        self.cahv = compute_CAHVOR(self._cahv_input)

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
        f = 100.00
        # http://www.digicamdb.com/specs/canon_eos-60d/
        pixelsize = 0.00429
        image_size = [2048, 3072]

        if camera_eye == 'LEFT':
            M = self._cam_model['M1']
            # Manually measured. May have en error.
            center = [0.762, 1.4097, -3.3667]
            rotation, _ = cv2.Rodrigues(self._cam_model['rvecs1'][0])
        if camera_eye == 'RIGHT':
            M = self._cam_model['M2']
            center = [0.762, -1.4097, -3.3667]
            rotation, _ = cv2.Rodrigues(self._cam_model['rvecs2'][0])
            relative_rotation = np.array(self._cam_model['R'])
            rotation = np.dot(relative_rotation, rotation)
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
                           ('az', 90.0),
                           ('el', 0.0)])
        return input_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='String Filepath')
    parser.add_argument('camera_eye', help='Camera Eye')
    args = parser.parse_args()
    cahv_parameters = CAHVmodel(args.filepath, args.camera_eye)
