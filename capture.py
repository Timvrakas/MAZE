import sys, os
from flir_ptu.ptu import PTU
from camera import StereoCamera, CameraID


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
    # TODO: To add `setup_camera_settings.py` here
    print('Setting up camera Parameters')
    # Worst case Solution
    os.system(' python3 setup_camera_settings')
    main()


def capture():
    # TODO: To add `Camera.py` support here
    file_name_count = 1
    print('Capturing an image...')
    cam = StereoCamera()
    cam.detect_cameras()
    cam.get_summary()
    cam.set_config('imageformat', 'Large Normal JPEG', CameraID.LEFT)
    cam.set_config('imageformat', 'Large Normal JPEG', CameraID.RIGHT)
    filename = str(file_name_count).zfill(5)
    cam.capture_image('/tmp/cam_files/','IMG_{}.JPG'.format(filename))
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
