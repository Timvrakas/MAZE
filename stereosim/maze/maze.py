# -*- coding: utf-8 -*-
import logging
from flir_ptu import ptu
from stereosim.maze import stereo_camera, imu, session, label
from multiprocessing import Lock
from multiprocessing.managers import BaseManager

logger = logging.getLogger(__name__)


class MAZE(object):

    def __init__(self):
        self.cam = stereo_camera.StereoCamera()
        self.ptu = ptu.PTU("10.5.1.2", 4000)
        self.imu = imu.IMU()
        self.session = session.Session("/srv/stereosim")
        self.last_images = [None, None]
        self.connected = False

    def get_last_images(self):
        return self.last_images

    def connect(self):
        if self.connected:
            self.disconnect()

        logger.info("Connecting")

        cam_status = self.cam.detect_cameras()

        self.ptu.connect()
        ptu_status = self.ptu.stream.is_connected

        imu_status = self.imu.connect()

        self.session.setup()
        self.connected = True
        return cam_status, ptu_status, imu_status

    def point(self, angle):
        self.ptu.slew_to_angle(angle)

    def get_stats(self):
        self.cam.get_stats()

    def preview(self):
        self.last_images = self.cam.capture_previews()

    def capture(self):

        file_path = self.session.get_folder_path()
        file_name = self.session.get_file_name()

        imu_data = self.imu.getData()
        ptu_angle = self.ptu.get_angle()

        saved_images = self.cam.capture_images(file_path, file_name)

        for image_path, camera_name in zip(saved_images, ('Left','Right')):
            label.create_label(image_path, camera_name, ptu_angle, imu_data)

        self.session.image_count(inc=True)

        logger.info("Captured Image Pair: {}".format(saved_images))
        self.last_images = saved_images
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
        if(self.connected):
            self.cam.disconnect()
            self.imu.disconnect()
            self.ptu.stream.close()
            self.session.teardown()
            logger.info("Disconnected")
            self.connected = False
        else:
            logger.info("Already Disconnected")


def main():
    maze = MAZE()
    BaseManager.register('get_maze', callable=lambda: maze)
    manager = BaseManager(address=('', 50000), authkey=b'abc')
    server = manager.get_server()
    server.serve_forever()
