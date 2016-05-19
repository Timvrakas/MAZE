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


def point(cam, ptu):
    az = int(input('Enter Azimuth: '))
    el = int(input('Enter Elevation: '))
    ptu.pan_angle(az)
    ptu.tilt_angle(el)
    pp = ptu.pan()
    tp = ptu.tilt()
    print('PP: ', pp, '\n', 'TP: ', tp)


def settings(cam, ptu):
    print('Setting up camera Parameters')
    cam.get_stats()
    print("Press `s` key if you want to get the camera parameters")


def capture(cam, ptu):
    print('Capturing an image...')
    cam.capture_image('/tmp/cam_files')
    print('Image Captured.')


def view(cam, ptu):
    # TODO: Add Preview Here
    print('view')


def command_help(cam, ptu):
    print('-----------------------------------------------------------------')
    print('                         Commands List                           ')
    print('-----------------------------------------------------------------')
    print(' p - To set PTU direction')
    print(' c - To capture an image')
    print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
    print(' v - To view sample image')
    print(' q - To quit the code')
    print('-----------------------------------------------------------------')


def quit(cam, ptu):
    cam.quit()
    print('quit')
    sys.exit()


def test_case(command_input, cam, ptu):
    options = {'p': point,
               's': settings,
               'c': capture,
               'v': view,
               'q': quit,
               '?': command_help}
    try:
        options[command_input](cam, ptu)
    except KeyError:
        print('Enter Valid Option')
        command_help()


def main():
    s = StereoCamera()
    ptu = PTU("129.219.136.149", 4000)

    s.detect_cameras()
    ptu.connect()

    while True:
        command_input = input('> ')
        test_case(command_input, s, ptu)

if __name__ == "__main__":
    main()
