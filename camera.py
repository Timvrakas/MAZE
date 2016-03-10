from __future__ import print_function

import os
import logging
import sys
import gphoto2 as gp
from enum import IntEnum


logger = logging.getLogger(__name__)


class CameraID(IntEnum):
    LEFT = 0
    RIGHT = 1


class StereoCamera():
    LEFTNAME = "LEFT"
    RIGHTNAME = "RIGHT"

    def __init__(self):
        self.context = gp.Context()

    def detect_cameras(self):
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
                self.cameras[CameraID.LEFT] = camera
            elif ownername == self.RIGHTNAME:
                camera._camera_name = self.RIGHTNAME
                self.cameras[CameraID.RIGHT] = camera

    def get_summary(self):
        for cam in self.cameras:
            text = cam.get_summary(self.context)
            logger.debug(str(text))

    def _get_config_obj(self, config, name):
        try:
            value_obj = config.get_child_by_name(name)
        except gp.GPhoto2Error:
            logger.error("Invalid config name: {}".format(name))
            return None

        return value_obj

    def get_config(self, name, camera_id):
        return self._get_config(name, self.cameras[camera_id])

    def _get_config(self, name, camera_obj):
        config = camera_obj.get_config(self.context)
        value_obj = self._get_config_obj(config, name)
        if value_obj:
            return value_obj.get_value()
        else:
            return None

    def get_choices(self, name, camera_id):
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

    def capture_image(self, storage_path, filename=None):
        if not os.path.isdir(storage_path):
            raise Exception("Invalid path: {}".format(storage_path))
        logger.debug(os.path.join(storage_path, 'LEFT'))
        if not os.path.isdir(os.path.join(storage_path, 'LEFT')):
            os.mkdir(os.path.join(storage_path, 'LEFT'))

        if not os.path.isdir(os.path.join(storage_path, 'RIGHT')):
            os.mkdir(os.path.join(storage_path, 'RIGHT'))

        camera_file_paths = []
        for cam in self.cameras:
            folder = os.path.join(storage_path, cam._camera_name)
            cpath = self.capture_image_individual(cam, folder, filename)
            camera_file_paths.append(cpath)

        return camera_file_paths

    def capture_image_individual(self, camera, storage_path, filename=None):
        logger.debug("Capturing image on {} camera".format(camera._camera_name))
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        logger.debug(
            "File path: {}/{}".format(file_path.folder, file_path.name))
        logger.debug("Transferring file")
        cfile = camera.file_get(
            file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL, self.context)

        camera_file = ''
        if filename:
            camera_file = os.path.join(storage_path, filename)
        else:
            camera_file = os.path.join(storage_path, file_path.name)
        cfile.save(camera_file)
        return camera_file

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
    s.get_summary()
    logger.debug(s.get_config("ownername", CameraID.LEFT))
    logger.debug(s.get_config("ownername", CameraID.RIGHT))
    logger.debug(s.get_choices("imageformat", CameraID.LEFT))
    # s.capture_image_individual(CameraID.LEFT)
    # s.capture_image('/tmp/cam_files')
    s.quit()


if __name__ == "__main__":
    sys.exit(main())
