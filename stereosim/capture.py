# -*- coding: utf-8 -*-
import sys
import os
import logging
import numpy as np

import yaml
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


    def point(self,az=None, el=None):
        if az==None and el==None:
            az = int(input('Enter Azimuth: '))
            el = int(input('Enter Elevation: '))
        elif az==None and el!=None:
            el = el
            az = int(input('Elevation : {} \n Enter Azimuth: '.format(el)))
        elif az!=None and el==None:
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
        file_path = self.session.get_folder_path()
        file_name = self.session.get_file_name()
        camera_file_paths = self.cam.capture_image(file_path, file_name)
        print('Image Captured.')
        self.session.image_count(inc=True)

        return camera_file_paths


    def pos_arr(self, pos):
        '''Make an (x,2) position array from a comma seperated list
        where each row provides az and el data. There must be an even number of values.
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
        '''
        lst = list(map(int, pos.split(',')))
        length = len(lst)
        if length % 2 != 0:
        	print('{} data points provided, an even number of az and el data points is required please try again.'.format(length))
        arr = np.asarray(lst)
        arr = arr.reshape((len(lst)/2, 2))

        return arr


    def mosaic(self, positions):
        """ Capture a mosiac based on the positions provided

        Parameters
        ----------

        cam : StereoCamera
        	Instance of 'StereoCamera'
        ptu : PTU
        	Instance of 'PTU'
        positions : array
        	Azimuth/elevation locations to image.
        **NOTE: Each consecutive az or el value is added to the previous.
        Ex: if 1st az is 10, and 2nd az is 12, after reading in 2nd az the position will be 22.

        Returns
        -------
            TBD :
            """
        file_name_count = 1

            # Move to the initial position
        self.ptu.pan_angle(positions[0][0])
        self.ptu.tilt_angle(positions[0][1])

        curr_az = positions[0][0]
        curr_el = positions[0][1]
        for pos in positions:
            curr_az += pos[0]
            curr_el += pos[1]

            self.point(az=curr_az, el=curr_el)
            filename = str(file_name_count).zfill(5)
            logger.info('Current Position:- Az: {}, El: {}, Current File:- {}'.format(curr_az, curr_el, filename))

            camera_files = self.capture()
            logger.info(camera_files)

            pp = self.ptu.pan()
            tp = self.ptu.tilt()

            for f in camera_files:
                yaml_path = os.path.splitext(f)[0]
                print('yaml_path:',yaml_path)
                contents = {
                        'AZIMUTH': curr_az,
                        'ELEVATION': curr_el,
                        'PP': pp,
                        'TP': tp
                }
                #with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
                #	print('lblfile:',lblfile)
                #	yaml.dump(contents, lblfile, default_flow_style=False)

                file_name_count += 1


    def view(self):
        # TODO: Add Preview Here
        print('view')


    def session(self):
        no = self.session.new_session()
        print("New session with no: {} started".format(no))


    def command_help(self):
        print('-----------------------------------------------------------------')
        print('                         Commands List                           ')
        print('-----------------------------------------------------------------')
        print(' n - To start new session')
        print(' p - To set PTU direction')
        print(' c - To capture an image')
        print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
        print(' v - To view sample image *NOT IMPLEMENTED*')
        print(' q - To quit the code')
        print('-----------------------------------------------------------------')


    def quit(self):
        self.cam.quit()
        print('quit')
        sys.exit()


    def test_case(self, command_input):
        options = {'n': self.session,
                   'p': self.point,
                   's': self.settings,
                   'c': self.capture,
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

    session_type = input('Begin regular_session or mosaic_session? ')
    while session_type not in ['regular_session', 'mosaic_session']:
        print('Input not applicable, please choose either "regular_session" or "mosaic_session"')
        session_type = input('regular_session or mosaic_session? ')

    with start_session() as session:
        cap_ses = CaptureSession(cam, ptu, session)
        if session_type=='regular_session':
                while True:
                    command_input = input('> ')
                    cap_ses.test_case(command_input)
        elif session_type=='mosaic_session':
            while True:
                    positions = input('Input comma separated list of az/el positions for mosaic, enter "Default" for default positions: ')
                    # Add a default option that uses predetermined steps.
                    if positions == 'Default':
                        positions = '0,0,15,0,15,0,0,-15,-15,0,-15,0'
                        print('positions : (0, 0), (15, 0), (15, 0), (0, -15), (-15, 0), (-15, 0)')
                    positions = cap_ses.pos_arr(positions)
                    cap_ses.mosaic(positions)
        

if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    main()
