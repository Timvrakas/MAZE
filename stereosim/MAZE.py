# -*- coding: utf-8 -*-
import logging
import numpy as np

from flir_ptu.ptu import PTU
from stereosim.stereo_camera import StereoCamera, CameraID
from stereosim.session import start_session
from stereosim.imu import IMU
from stereosim.label import create_label
from stereosim.console import Console

logger = logging.getLogger(__name__)


class MAZE(object):

    def __init__(self, cam, ptu, imu, session):
        self.cam = cam
        self.ptu = ptu
        self.imu = imu
        self.session = session

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

    def quit(self):
        self.cam.quit()
        self.imu.disconnect()
        self.ptu.stream.close()
        logger.info("Exiting")


def main():
    cam = StereoCamera()
    ptu = PTU("10.5.1.2", 4000)
    imu = IMU()

    with start_session() as session:
        cam.detect_cameras()
        ptu.connect()
        imu.connect()

        maze = MAZE(cam, ptu, imu, session)

        console = Console(maze)

        while True:
            command_input = input('> ')
            console.test_case(command_input)


if __name__ == "__main__":
    main()
