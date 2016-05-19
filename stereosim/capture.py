# -*- coding: utf-8 -*-
import sys
import logging
from flir_ptu.ptu import PTU
from stereosim.stereosim import StereoCamera, CameraID

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def point():
    ptu = PTU("129.219.136.149", 4000)
    ptu.connect()

    az = int(input('Enter Azimuth: '))
    el = int(input('Enter Elevation: '))
    ptu.pan_angle(az)
    ptu.tilt_angle(el)
    pp = ptu.pan()
    tp = ptu.tilt()
    print('PP: ', pp, '\n', 'TP: ', tp)


def settings():
    print('Setting up camera Parameters')
    s = StereoCamera()
    s.detect_cameras()
    stats = s.get_stats()
    print("Press `s` key if you want to get the camera parameters")
    s.quit()


def capture():
    print('Capturing an image...')
    s = StereoCamera()
    s.detect_cameras()
    s.capture_image('/tmp/cam_files')
    s.quit()
    print('Image Captured.')


def view():
    # TODO: Add Preview Here
    print('view')


def command_help():
    print('-----------------------------------------------------------------')
    print('                         Commands List                           ')
    print('-----------------------------------------------------------------')
    print(' p - To set PTU direction')
    print(' c - To capture an image')
    print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
    print(' v - To view sample image')
    print(' q - To quit the code')
    print('-----------------------------------------------------------------')


def quit():
    print('quit')
    sys.exit()


def test_case(command_input):
    options = {'p': point,
               's': settings,
               'c': capture,
               'v': view,
               'q': quit,
               '?': command_help}
    try:
        options[command_input]()
    except KeyError:
        print('Enter Valid Option')
        command_help()


def main():
    while True:
        command_input = input('> ')
        test_case(command_input)

if __name__ == "__main__":
    main()
