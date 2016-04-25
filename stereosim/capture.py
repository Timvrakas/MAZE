import sys
import os
import logging
from flir_ptu.ptu import PTU
from stereosim.stereosim import StereoCamera, CameraID
from stereosim.setup_camera_settings import echo_focallength

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
    main()


def settings():
    print('Setting up camera Parameters')
    s = StereoCamera()
    s.detect_cameras()
    stats = s.get_stats()
    print("Press `s` key if you want to get the camera parameters")
    s.quit()
    main()


def capture():
    print('Capturing an image...')
    s = StereoCamera()
    s.detect_cameras()
    s.capture_image('/tmp/cam_files')
    s.get_stats(CameraID.LEFT)
    s.quit()
    print('Image Captured.')
    main()


def view():
    # TODO: Add Preview Here
    print('view')
    main()


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
    main()


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
    command_input = input('> ')
    test_case(command_input)

if __name__ == "__main__":
    main()
