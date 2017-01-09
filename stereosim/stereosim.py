from __future__ import print_function
from multiprocessing.dummy import Pool as ThreadPool

import os
import logging
import sys
import math
import yaml
import gphoto2 as gp
from enum import IntEnum
from flir_ptu.ptu import PTU
import exifread


logger = logging.getLogger(__name__)


class CameraID(IntEnum):
    LEFT = 0
    RIGHT = 1


class StereoCamera():
    """
    Dual camera representation

    Attributes
    ----------
    LEFTNAME : str
        Ownername of the left camera
    RIGHTNAME : str
        Ownername of the right camera
    """
    LEFTNAME = "LEFT"
    RIGHTNAME = "RIGHT"

    def __init__(self):
        self.context = gp.Context()

    def detect_cameras(self):
        """ Detects the connected cameras and if the ownername matches
        with `LEFTNAME` or `RIGHTNAME`, it will be stored under the variable
        `cameras`
        """
        _cameras = self.context.camera_autodetect()
        if len(_cameras) == 0:
            raise Exception("Unable to find any camera")
        # Stores the left and right camera
        self.cameras = [None, None]
        ports = gp.PortInfoList()
        ports.load()

        for index, (name, addr) in enumerate(_cameras):
            logger.debug(
                "Count: {}, Name: {}, Addr: {}".format(index, name, addr))
            # Get the ports and search for the camera
            idx = ports.lookup_path(addr)
            camera = gp.Camera()
            camera.set_port_info(ports[idx])
            camera.init(self.context)
            # Check if the ownername matches to given values
            ownername = self._get_config("ownername", camera)
            if ownername == self.LEFTNAME:
                camera._camera_name = self.LEFTNAME
                camera._camera_id = self.cameras[CameraID.LEFT]
                self.cameras[CameraID.LEFT] = camera
            elif ownername == self.RIGHTNAME:
                camera._camera_name = self.RIGHTNAME
                camera._camera_id = self.cameras[CameraID.RIGHT]
                self.cameras[CameraID.RIGHT] = camera

    def get_summary(self):
        """ Prints the summary of the cameras as defined by gphoto2
        """
        for cam in self.cameras:
            text = cam.get_summary(self.context)
            logger.info(str(text))

    def _get_config_obj(self, config, name):
        try:
            value_obj = config.get_child_by_name(name)
        except gp.GPhoto2Error:
            logger.error("Invalid config name: {}".format(name))
            return None

        return value_obj

    def get_config(self, name, camera_id):
        """ Get camera config value

        Parameters
        ---------
        name : str
            The name of the camera config
        camera_id : enum

        Returns
        -------
        value or None
            Value of the config requested or None if the config
            does not exist
        """
        return self._get_config(name, self.cameras[camera_id])

    def _get_config(self, name, camera_obj):
        config = camera_obj.get_config(self.context)
        value_obj = self._get_config_obj(config, name)
        if value_obj:
            return value_obj.get_value()
        else:
            return None

    def get_choices(self, name, camera_id):
        """ Get valid choices for a config

        Parameters
        ---------
        name : str
            The name of the camera config
        camera_id : enum

        Returns
        -------
        Array
            Empty array if the config is invalid
        """
        config = self.cameras[camera_id].get_config(self.context)
        value_obj = self._get_config_obj(config, name)
        try:
            count = value_obj.count_choices()
        except gp.GPhoto2Error:
            count = 0

        valid_choices = []
        for i in range(count):
            valid_choices.append(value_obj.get_choice(i))
        return valid_choices

    def set_config(self, name, value, camera_id):
        config = self.cameras[camera_id].get_config(self.context)
        value_obj = self._get_config_obj(config, name)
        if value_obj:
            value_obj.set_value(value)
            self.cameras[camera_id].set_config(config, self.context)

    def get_focallength(self, camera_id):
        filename = "focallength.jpg"
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(curr_dir, filename)
        if os.path.isfile(test_file):
            os.remove(test_file)

        old_image_setting = self._get_config("imageformat", self.cameras[camera_id])
        self.set_config("imageformat", "Small Normal JPEG", camera_id)

        onboard_path = self.trigger_capture(self.cameras[camera_id])
        test_file = self.get_image_from_camera(self.cameras[camera_id], onboard_path,
                                               curr_dir, filename)

        with open(test_file, 'rb') as f:
            meta = exifread.process_file(f, details=False)

        focal_len = '{} mm'.format(meta['EXIF FocalLength'])

        os.remove(test_file)
        self.set_config("imageformat", old_image_setting, camera_id)
        return focal_len

    def get_stats(self, camera_id=None):
        stats = ['aperture', 'shutterspeed', 'iso', 'focallength']
        stats_array = []

        if camera_id is None:
            indexes = CameraID
        else:
            indexes = [camera_id]

        for index in indexes:
            cam = self.cameras[index]
            stats_dict = dict()
            logger.info("{} Camera Stats:".format(cam._camera_name))
            for stat in stats:
                if stat == 'focallength':
                    value = self.get_focallength(index)
                else:
                    value = self._get_config(stat, cam)
                logger.info("\t {}: {}".format(stat, value))
                stats_dict[stat] = value
            stats_array.append(stats_dict)
        return stats_array

    def capture_image(self, storage_path, filename=None):
        """ Capture images on both the cameras
        The files will stored as below
            storage_path
                LEFT
                    filename
                RIGHT
                    filename

        Parameters
        ---------
        storage_path : str
            Location where the files will be stored
        filename : str

        Returns
        -------
        Array : [Left camera filename, Right camera filename]
        """
        if not os.path.isdir(storage_path):
            raise Exception("Invalid path: {}".format(storage_path))
        logger.debug(os.path.join(storage_path, 'LEFT'))
        if not os.path.isdir(os.path.join(storage_path, 'LEFT')):
            os.mkdir(os.path.join(storage_path, 'LEFT'))

        if not os.path.isdir(os.path.join(storage_path, 'RIGHT')):
            os.mkdir(os.path.join(storage_path, 'RIGHT'))

        stored_file_paths = []
        camera_onboard_paths = []
        
        cameras_test = [self.cameras[0], self.cameras[1]]

        pool = ThreadPool(4)
       
        camera_onboard_paths = pool.map(self.trigger_capture, cameras_test)
        
        pool.close()
        pool.join()

        for cam, location in zip(self.cameras, camera_onboard_paths):
            folder = os.path.join(storage_path, cam._camera_name)
            if folder.startswith('RIGHT', 36, 41):
                filename = 'R_'  +  filename
                filename = filename[:2] + filename[4:]
            if folder.startswith('LEFT', 36, 40):
                filename = 'L_' + filename
            cpath = self.get_image_from_camera(cam, location, folder, filename)
            stored_file_paths.append(cpath)

        return stored_file_paths

    def trigger_capture(self, camera):
        """ Trigger image capture

        Parameters
        ----------
        camera : camera_object

        Returns
        -------
        str
            The path of the captured image on the camera
        """
        logger.debug("Triggering image capture on {} camera".format(camera._camera_name))
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        logger.debug(
            "File path: {}/{}".format(file_path.folder, file_path.name))
        return file_path

    def get_image_from_camera(self, camera, camera_file_path, storage_path, filename=None):
        """ Capture image on single camera

        Parameters
        ----------
        camera : camera_object
        camera_file_path : path of the image on the camera
        storage_path : str
        filename : str

        Returns
        -------
        str
            The path of the captured image
        """
        logger.debug("Transferring file")
        cfile = camera.file_get(camera_file_path.folder, camera_file_path.name,
                                gp.GP_FILE_TYPE_NORMAL, self.context)

        camera_file = ''
        if filename:
            camera_file = os.path.join(storage_path, filename)
        else:
            camera_file = os.path.join(storage_path, camera_file_path.name)
        logger.info("Storing file at {}".format(camera_file))
        cfile.save(camera_file)
        if filename != "focallength.jpg":
            self.create_label(camera, camera_file)
        return camera_file

    def create_label(self, camera, file_path):
        """ Create label for captured image.

        Parameters
        ----------
        camera : camera_object
        file_path : str
        """
        with open(file_path, 'rb') as f:
            meta = exifread.process_file(f, details=False)

        focal_length = '{}'.format(meta['EXIF FocalLength'])

        ptu = PTU("129.219.136.149", 4000)
        ptu.connect()
        if ptu.stream.is_connected:
            pp = ptu.pan()
            tp = ptu.tilt()
            az = ptu.pan_angle()
            el = ptu.tilt_angle()
            
            yaml_path = os.path.splitext(file_path)[0]
            contents = {
                'AZIMUTH': az,
                'ELEVATION': el,
                'PP': float(pp),
                'TP': float(tp),
                'f': float(focal_length),
                'Camera': camera._camera_name
            }
            with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
                yaml.dump(contents, lblfile, default_flow_style=False)

        else:
            pp = None
            tp = None
            az = None
            el = None

            yaml_path = os.path.splitext(file_path)[0]
            contents = {
                'AZIMUTH': az,
                'ELEVATION': el,
                'PP': pp,
                'TP': tp,
                'f': float(focal_length),
                'Camera': camera._camera_name
            }
            with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
                yaml.dump(contents, lblfile, default_flow_style=False)

    def quit(self):
        for cam in self.cameras:
            cam.exit(self.context)


def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.ERROR)
    gp.check_result(gp.use_python_logging())
    logger.setLevel(logging.DEBUG)

    s = StereoCamera()
    s.detect_cameras()
    # s.get_summary()
    # logger.debug(s.get_config("ownername", CameraID.LEFT))
    # logger.debug(s.get_choices("imageformat", CameraID.LEFT))
    s.capture_image('/tmp/cam_files')
    # f = s.get_focallength(CameraID.LEFT)
    # logger.debug("FocalLength: {}".format(f))
    s.get_stats()
    s.get_stats(CameraID.LEFT)
    s.quit()


if __name__ == "__main__":
    sys.exit(main())
