# -*- coding: utf-8 -*-
import sys
import logging
from flir_ptu.ptu import PTU
from stereosim.stereosim import StereoCamera, CameraID
from stereosim.session import start_session


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def point(cam, ptu, session):
    az = int(input('Enter Azimuth: '))
    el = int(input('Enter Elevation: '))
    ptu.pan_angle(az)
    ptu.tilt_angle(el)
    pp = ptu.pan()
    tp = ptu.tilt()
    print('PP: ', pp, '\n', 'TP: ', tp)


def settings(cam, ptu, session):
    print('Setting up camera Parameters')
    cam.get_stats()
    print("Press `s` key if you want to get the camera parameters")


def capture(cam, ptu, session):
    print('Capturing an image...')
    file_path = session.get_folder_path()
    file_name = session.get_file_name()
    cam.capture_image(file_path, file_name)
    print('Image Captured.')
    session.image_count(inc=True)


def view(cam, ptu, session):
    # TODO: Add Preview Here
    print('view')


def session(cam, ptu, session):
    no = session.new_session()
    print("New session with no: {} started".format(no))


def command_help(cam, ptu, session):
    print('-----------------------------------------------------------------')
    print('                         Commands List                           ')
    print('-----------------------------------------------------------------')
    print(' n - To start new session')
    print(' p - To set PTU direction')
    print(' c - To capture an image')
    print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
    print(' v - To view sample image')
    print(' q - To quit the code')
    print('-----------------------------------------------------------------')


def quit(cam, ptu, session):
    cam.quit()
    print('quit')
    sys.exit()


def test_case(command_input, cam, ptu, ses_obj):
    options = {'n': session,
               'p': point,
               's': settings,
               'c': capture,
               'v': view,
               'q': quit,
               '?': command_help}
    try:
        options[command_input](cam, ptu, ses_obj)
    except KeyError:
        print('Enter Valid Option')
        command_help(cam, ptu, session)


def main():
    s = StereoCamera()
    ptu = PTU("129.219.136.149", 4000)

    s.detect_cameras()
    ptu.connect()

    with start_session() as session:
        while True:
            command_input = input('> ')
            test_case(command_input, s, ptu, session)


if __name__ == "__main__":
    main()
