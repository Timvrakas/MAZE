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


def point(cam, ptu, session, az=False, el=False):
    if az=False or el=False:
        az = int(input('Enter Azimuth: '))
        el = int(input('Enter Elevation: '))
        ptu.pan_angle(az)
        ptu.tilt_angle(el)
        pp = ptu.pan()
        tp = ptu.tilt()
        print('PP: ', pp, '\n', 'TP: ', tp)
    else:
        ptu.pan_angle(az)
        ptu.tilt_angle(el)
        pp = ptu.pan()
        tp = ptu.tilt()
        print('PP: ', pp, '\n', 'TP: ', tp)


def settings(cam, ptu, session):
    print('Setting up camera Parameters')
    cam.get_stats()
    print("Press `s` key if you want to get the camera parameters")


def capture(cam, ptu, session, filepath=False, filename=False):
    if filepath=False or filename=False:
        print('Capturing an image...')
        file_path = session.get_folder_path()
        file_name = session.get_file_name()
        cam.capture_image(file_path, file_name)
        print('Image Captured.')
        session.image_count(inc=True)
    else: 
        print('Capturing an image...')
        cam.capture_image(filepath, filename)
        print('Image Captured.')
        session.image_count(inc=True)

def mosaic(cam, ptu, filepath, positions):
    """ Capture a mosiac around the position defined by positions

    Parameters
    ----------

    cam : StereoCamera
        Instance of 'StereoCamera'
    ptu : PTU
        Instance of 'PTU'
    filepath : filepath
        path to where the image(s) will be stored
    positions : array
        azimuth/elevation locations to image
        ex: positions = [(az, el), (az, el), (az, el)]

    Returns
    -------

    TBD :
    """ 
    file_name_count = 1

    if not os.path.isdir(filepath):
        raise Exception("Invalid path: {}".format(filepath))

    # Move to the initial position
    ptu.pan_angle(positions[0][0])
    ptu.tilt_angle(positions[0][1])

    curr_az = positions[0][0]
    curr_el = positions[0][1]
    for pos in positions:
        curr_az += pos[0]
        curr_el += pos[1]

        point(cam, ptu, session, az=az, el=el)
        filename = str(file_name_count).zfill(5)
        logger.info('Current Position:- Az: {}, El: {}, Current File:- {}'.format(curr_az, curr_el, filename))
        
        camera_files = capture(cam, ptu, session, filepath=filepath, filename=filename)
        logger.info(camera_files)

        # removed because they are in point()
        # pp = ptu.pan()
        # tp = ptu.tilt()

        for f in camera_files:
            yaml_path = os.path.splitext(f)[0]
            contents = {
                'AZIMUTH': curr_az,
                'ELEVATION': curr_el,
                'PP': pp,
                'TP': tp
            }
            with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
                yaml.dump(contents, lblfile, default_flow_style=False)

        file_name_count += 1


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
    print(' v - To view sample image *NOT IMPLEMENTED*')
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
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    main()
