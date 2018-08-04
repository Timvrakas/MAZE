from __future__ import print_function
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from time import sleep
import math
import pickle
import os
import logging
import io
import time
import sys
import math
import yaml
import gphoto2 as gp
from enum import IntEnum
from flir_ptu.ptu import PTU
import exifread
import exiftool
#LOGGER = logging.getLogger(__name__)

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
        self.pool = ThreadPool(2)

    def detect_cameras(self):
        """ Detects the connected cameras and if the ownername matches
        with `LEFTNAME` or `RIGHTNAME`, it will be stored under the variable
        `cameras`
        """
        self.context
        _cameras = self.context.camera_autodetect()
        msg = [(False, "None"), (False, "None")]
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
            try:
                camera = gp.Camera()
                camera.set_port_info(ports[idx])
                camera.init(self.context)
                # Check if the ownername matches to given values
                ownername = self._get_config("ownername", camera)
                abilities = gp.check_result(gp.gp_camera_get_abilities(camera))
            except gp.GPhoto2Error as error:
                print(str(error))
            else:
                if ownername == self.LEFTNAME:
                    camera._camera_name = self.LEFTNAME
                    camera._camera_id = CameraID.LEFT
                    self.cameras[CameraID.LEFT] = camera
                    msg[CameraID.LEFT] = True, "Connected: " + \
                        str(abilities.model)
                elif ownername == self.RIGHTNAME:
                    camera._camera_name = self.RIGHTNAME
                    camera._camera_id = CameraID.RIGHT
                    self.cameras[CameraID.RIGHT] = camera
                    msg[CameraID.RIGHT] = True, "Connected: " + \
                        str(abilities.model)

        failure = (self.cameras[CameraID.LEFT] is None) or (
            self.cameras[CameraID.RIGHT] is None)
        return failure, msg

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
            #x = value_obj.get_value()
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

    '''
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

    '''

    def get_specs(self, name, test_file):
        with open(test_file, 'rb') as f:
            meta = exifread.process_file(f, details=False)

        focal_len = '{} mm'.format(meta['EXIF FocalLength'])
        shutterspeed = '{} seconds'.format(meta['EXIF ExposureTime'])
        if name == 'focallength':
            return focal_len
        else:
            return shutterspeed
    '''
        os.remove(test_file)
        self.set_config("imageformat", old_image_setting, camera_id)
        return focal_len
    '''

    # TODO: This has to be totaly reworked...
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
            filename = "specs.jpg"

            curr_dir = os.path.dirname(os.path.realpath(__file__))
            test_file = os.path.join(curr_dir, filename)
            if os.path.isfile(test_file):
                os.remove(test_file)

            old_image_setting = self._get_config(
                "imageformat", self.cameras[index])

            self.set_config("imageformat", "Small Normal JPEG", index)
            onboard_path = self.trigger_capture(self.cameras[index])

            test_file = os.path.join(curr_dir, filename)
            self.get_image_from_camera(
                self.cameras[index], onboard_path, test_file)

            for stat in stats:
                if stat == 'focallength' or stat == 'shutterspeed':
                    value = self.get_specs(stat, test_file)
                else:
                    value = self._get_config(stat, cam)
                logger.info("\t {}: {}".format(stat, value))
                stats_dict[stat] = value

            stats_array.append(stats_dict)
            os.remove(test_file)

            self.set_config("imageformat", old_image_setting, index)
        return stats_array

    def capture_image(self, storage_path, ptu_dict, IMU_data, filename_base=None):
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

        # PART ONE: capture the images to the camera internal memory card.
        timer = time.time()

        # Spin threads to capture images
        camera_onboard_paths = self.pool.map(
            self.trigger_capture, self.cameras)

        print("Capture Process took: {:f} seconds.".format(
            time.time() - timer))

        # PART TWO: transfer the images from the camera
        timer = time.time()

        if not os.path.isdir(storage_path):
            os.mkdir(storage_path)

        stored_file_paths = []

        for cam in self.cameras:  # Generate filenames
            camera_dir = os.path.join(storage_path, cam._camera_name)
            if not os.path.isdir(camera_dir):
                os.mkdir(camera_dir)
            if(self._get_config('imageformat', cam) == 'RAW'):
                file_ext = ".CRW"
            else:
                file_ext = ".JPG"
            filename = cam._camera_name[0] + '_' + filename_base + file_ext
            file_path = os.path.join(camera_dir, filename)
            stored_file_paths.append(file_path)

        get_image_args = list(
            zip(*(self.cameras, camera_onboard_paths, stored_file_paths)))

        self.pool.starmap(
            self.get_image_from_camera, get_image_args)

        print("Transfer Process took: {:f} seconds.".format(
            time.time() - timer))

        '''if filename != "specs.jpg":
            # TODO: This should really be called from capture_image, not from here.
            self.create_label(camera, camera_file, IMU_data, ptu_dict)'''

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
        logger.debug("Triggering image capture on {} camera".format(
            camera._camera_name))
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        logger.debug(
            "File path: {}/{}".format(file_path.folder, file_path.name))
        return file_path

    def get_image_from_camera(self, camera, camera_file_path, storage_file_path):
        """ Capture image on single camera

        Parameters
        ----------
        camera : camera_object
        camera_file_path : path of the image on the camera
        storage_file_path : file location to save
        """
        #timer = time.time()
        cfile = camera.file_get(camera_file_path.folder, camera_file_path.name,
                                gp.GP_FILE_TYPE_NORMAL, self.context)
        #print("get took: {:f} seconds.".format(time.time()-timer))
        #timer = time.time()
        cfile.save(storage_file_path)
        #print("save took: {:f} seconds.".format(time.time()-timer))

    def create_label(self, camera, file_path, IMU_data, ptu_dict):
        """ Create label for captured image.

        Parameters
        ----------
        camera : camera_object
        file_path : str
        """
        with exiftool.ExifTool() as et:
            flmeta = et.get_tag('FocalLength', file_path)
            #meta = et.get_metadata(file_path)

        #focal_length = '{}'.format(meta['EXIF FocalLength'])
        #focal_length = '{}'.format(meta['XMP:FocalLength'])
        focal_length = '{}'.format(flmeta)

        pp = ptu_dict['pp']
        tp = ptu_dict['tp']
        az = ptu_dict['az']
        el = ptu_dict['el']

        IMU_quaternion = IMU_data["quat"]

        yaml_path = os.path.splitext(file_path)[0]
        contents = {
            'AZIMUTH': az,
            'ELEVATION': el,
            'PP': float(pp),
            'TP': float(tp),
            'f': float(focal_length),
            # 'pr': ptu.pan_res(),
            # 'tr': ptu.tilt_res(),
            # 'temp': ptu.ptu_temp(),
            'Camera': camera._camera_name,
            'below values obtained by stereosim IMU:': 'see below',
            '': IMU_data,
            'IMU_quaternion': IMU_quaternion
        }
        with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
            yaml.dump(contents, lblfile, default_flow_style=False)

    def quit(self):
        for cam in self.cameras:
            cam.exit(self.context)


'''
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
    # s.capture_image('/tmp/cam_files')
    # f = s.get_focallength(CameraID.LEFT)
    # logger.debug("FocalLength: {}".format(f))
    s.get_stats()
    s.get_stats(CameraID.LEFT)
    s.quit()


if __name__ == "__main__":
    sys.exit(main())
'''  # this is old...
