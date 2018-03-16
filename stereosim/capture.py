# -*- coding: utf-8 -*-
import sys
import logging
import numpy as np
import time

from flir_ptu.ptu import PTU
from stereosim.stereosim import StereoCamera, CameraID
from stereosim.session import start_session


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class CaptureSession(object):

    def __init__(self, cam, ptu, session):
        self.cam = cam
        self.ptu = ptu
        self.session = session

    def point(self, az=None, el=None):
        if az is None and el is None:
            az = int(input('Enter Azimuth: '))
            el = int(input('Enter Elevation: '))
        elif az is None and el is not None:
            el = el
            az = int(input('Elevation : {} \n Enter Azimuth: '.format(el)))
        elif az is not None and el is None:
            az = az
            el = int(input('Azimuth : {} \n Enter Elevation: '.format(az)))

        self.ptu.pan_angle(az)
        self.ptu.tilt_angle(el)
        pp = self.ptu.pan()
        tp = self.ptu.tilt()
        print('PP: ', pp, '\n', 'TP: ', tp)

    def settings(self):
        print('Setting up camera Parameters')
        self.cam.get_stats()
        print("Press `s` key if you want to get the camera parameters")

    def capture(self):
        print('Capturing an image...')
        timstart = time.time()
        file_path = self.session.get_folder_path()
        file_name = self.session.get_file_name()
        print('file_path: ', file_path)
        print('imageformat: ', self.cam.get_config('imageformat', CameraID.RIGHT))
        timstart = time.time()
        #if(self.cam.get_config('imageformat', CameraID.RIGHT) == 'RAW2' and self.cam.get_config('imageformat', CameraID.LEFT) == 'RAW2'):
            #file_name = file_name.replace("jpg", "cr2")
            #print('filename: ', file_name)
        if(self.cam.get_config('imageformat', CameraID.RIGHT) == 'RAW' and self.cam.get_config('imageformat', CameraID.LEFT) == 'RAW'):
            file_name = file_name.replace("jpg","crw")
            print('we in the get config if statement. this is file_name: ', file_name)
        elif(self.cam.get_config('imageformat', CameraID.RIGHT) == 'RAW' or self.cam.get_config('imageformat', CameraID.LEFT) == 'RAW'):
            print('image format of one of the cameras is not the same as the other please readjust')
        print("we about to cal stereosim stuff. but here's the get_config time: " + str(time.time()-timstart))
        camera_file_paths = self.cam.capture_image(file_path, file_name)
        print('Image Captured.')
        print('Total capture time' + str(time.time() - timstart) + ' seconds')
        self.session.image_count(inc=True)

        return camera_file_paths

    def pos_arr(self, pos):
        """Make an (x,2) position array from a comma seperated list.
        Each row provides az and el data.
        There must be an even number of values.
        Used when mosaic_session is chosen.

        Parameters
        ----------

        pos : input string
        comma seperated list of az and el.
        ex: az,el,az,el,az,el.

        Returns
        -------

        pos_arr : array
        An (x,2) array where column 0 is az and column 1 is el.
        ex: [(az, el),
            (az, el),
            (az, el)]
        """
        lst = list(map(int, pos.split(',')))
        length = len(lst)
        if length % 2 != 0:
            print('{} data points provided, an even number of az and el data'
                  'points is required please try again.'.format(length))
        arr = np.asarray(lst)
        arr = arr.reshape((len(lst) / 2, 2))

        return arr

    def mosaic(self):
        """ Capture a mosiac based on the positions provided.

        Parameters
        ----------

        cam : StereoCamera
            Instance of 'StereoCamera'
        ptu : PTU
            Instance of 'PTU'
        positions : array
            Azimuth/elevation locations to image.
        **NOTE: Each consecutive az or el value is added to the previous.
        Ex: if 1st az is 10, and 2nd az is 12, after reading in 2nd az
        the position will be 22.

       """

        print('-' * 50)
        positions = input("\n Enter comma separated list of az/el positions for mosaic"
                          "\n enter 'd' for default positions"
                          "\n enter 'q' to quit program: ")
        print('-' * 50)
        if positions == 'd':
            positions = '0,0,15,0,15,0,0,-15,-15,0,-15,0'
            print('positions : (0, 0), (15, 0), (15, 0),'
                  '(0, -15), (-15, 0), (-15, 0)')
            print('-' * 50)
        if positions == 'q':
            self.quit()
        positions = self.pos_arr(positions)

        file_name_count = 1

        # Move to the origin (0,0)
        self.ptu.pan_angle(0)
        self.ptu.tilt_angle(0)
        curr_az = 0
        curr_el = 0

        for pos in positions:
            curr_az += pos[0]
            curr_el += pos[1]

            # point camera
            self.point(az=curr_az, el=curr_el)
            filename = str(file_name_count).zfill(5)
            logger.info('Current Position:- Az: {}, El: {}, '
                        'Current File:- {}'.format(curr_az, curr_el, filename))
            # capture image
            camera_files = self.capture()
            logger.info(camera_files)

            file_name_count += 1

    def view(self):
        # TODO: Add Preview Here
        print('view')

    def create_session(self):
        no = self.session.new_session()
        print("New session with no: {} started".format(no))

    def command_help(self):
        print('-----------------------------------------------------------------')
        print('                         Commands List                           ')
        print('-----------------------------------------------------------------')
        print(' n - To start new session')
        print(' p - To set PTU direction')
        print(' c - To capture an image')
        print(' m - To take a mosaic')
        print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
        print(' v - To view sample image *NOT IMPLEMENTED*')
        print(' q - To quit the code')
        print('-----------------------------------------------------------------')

    def quit(self):
        self.cam.quit()
        print('quit')
        sys.exit()

    def test_case(self, command_input):
        options = {'n': self.create_session,
                   'p': self.point,
                   's': self.settings,
                   'c': self.capture,
                   'm': self.mosaic,
                   'v': self.view,
                   'q': self.quit,
                   '?': self.command_help}
        try:
            options[command_input]()
        except KeyError:
            print('Enter Valid Option')
            self.command_help()


def main():
    cam = StereoCamera()
    ptu = PTU("129.219.136.149", 4000)

    cam.detect_cameras() 
    ptu.connect()

    with start_session() as session:
        cap_ses = CaptureSession(cam, ptu, session)
        while True:
            command_input = input('> ')
            cap_ses.test_case(command_input)

if __name__ == "__main__":
    main()
