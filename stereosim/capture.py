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


def point(cam, ptu, session, az=None, el=None):
    if az==None and el==None:
        az = int(input('Enter Azimuth: '))
        el = int(input('Enter Elevation: '))
    elif az==None and el!=None:
        el = el
        az = int(input('Elevation : {} \n Enter Azimuth: '.format(el)))
    elif az!=None and el==None:
        az = az
        el = int(input('Azimuth : {} \n Enter Elevation: '.format(az)))

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

def pos_arr(pos):
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
    while (num % 2) != 0:
        print('{} data points provided, an even number of az and el data points is required please try again.'.format(length))
    arr = np.asarray(lst)
    arr = arr.reshape((len(lst)/2, 2))

    return arr


def mosaic(cam, ptu, session, positions):
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
        
        camera_files = capture(cam, ptu, session)
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

    session_type = input('Begin regular_session or mosaic_session? ')
    while session_type not in ['regular_session', 'mosaic_session']:
        print('Input not applicable, please choose either "regular_session" or "mosaic_session"')
        session_type = input('regular_session or mosaic_session? ')

    with start_session() as session:
        if session_type==regular_session:
                while True:
                    command_input = input('> ')
                    test_case(command_input, s, ptu, session)
        elif session_type==mosaic_session:
            while True:
                    positions = input('Input comma separated list of az/el positions for mosaic, enter "feeling lucky" for default positions: ')
                    # Add a default option that uses predetermined steps.
                    if positions == 'default':
                        positions = 0,0,15,0,15,0,0,-15,-15,0,-15,0
                        print('positions : (0, 0), (15, 0), (15, 0), (0, -15), (-15, 0), (-15, 0)')
                    positions = pos_arr(positions)
                    mosaic(cam, ptu, session, positions)
        

if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    main()
