# -*- coding: utf-8 -*-
import logging
import numpy as np

from flir_ptu.ptu import PTU
from stereosim.stereo_camera import StereoCamera, CameraID
from stereosim.imu import IMU
from stereosim.label import create_label
from stereosim.console import Console
from stereosim.session import Session

logger = logging.getLogger(__name__)


class MAZE(object):

    def __init__(self):
        self.cam = StereoCamera()
        self.ptu = PTU("10.5.1.2", 4000)
        self.imu = IMU()
        self.session = Session("/srv/stereosim")

    def connect(self):
        logger.info("Connecting")
        self.cam.detect_cameras()
        self.ptu.connect()
        self.imu.connect()
        self.session.setup()

    def point(self, angle):
        self.ptu.slew_to_angle(angle)

    def settings(self):
        self.cam.get_stats()

    def capture(self):
        file_path = self.session.get_folder_path()
        file_name = self.session.get_file_name()

        imu_data = self.imu.getData()
        ptu_angle = self.ptu.get_angle()

        saved_images = self.cam.capture_image(file_path, file_name)

        for (image_path, camera_name) in saved_images:
            create_label(image_path, camera_name, ptu_angle, imu_data)

        self.session.image_count(inc=True)

        logger.info("Captured Image Pair: {}".format(saved_images))
        return saved_images

    def mosaic(self, positions):
        """ Capture a mosiac based on the positions provided."""
        file_name_count = 1

        # Move to the origin (0,0)
        self.ptu.slew_to_angle((0, 0))

        for pos in positions:
            # point camera
            self.point(pos)
            filename = str(file_name_count).zfill(5)
            logger.info('Current Position:- Az: {}, El: {}, '
                        'Current File:- {}'.format(pos[0], pos[1], filename))
            # capture image
            self.capture()
            file_name_count += 1

    def bulk(self, count):
        # take  a bunch of pictures
        for x in range(1, count+1):
            self.capture()
            logger.info('Bulk Capture Progress: {}/{}'.format(x, count))

    def new_session(self):
        return self.session.new_session()

    def disconnect(self):
        self.cam.quit()
        self.imu.disconnect()
        self.ptu.stream.close()
        self.session.teardown()
        logger.info("Disconnected")
