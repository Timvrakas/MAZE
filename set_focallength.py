from camera import StereoCamera, CameraID
import sys
import select
import tty
import termios


class NonBlockingConsole(object):
    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False


def echo_focallength(cam, cam_id):
    print()
    print("FocalLength of {} Camera:- ".format(cam_id.name))
    with NonBlockingConsole() as nbc:
        while True:
            print('\t ', cam.get_focallength(cam_id))
            key = nbc.get_data()
            if key == 'y' or key == 'Y':
                break


if __name__ == '__main__':
    print('Setting the FocalLength of cameras')
    print("Press `y` key to move to the next camera")
    s = StereoCamera()
    s.detect_cameras()

    echo_focallength(s, CameraID.LEFT)
    echo_focallength(s, CameraID.RIGHT)

    print("Please wait extracting final focallength values")
    l = s.get_focallength(CameraID.LEFT)
    r = s.get_focallength(CameraID.RIGHT)

    print("Final FocalLength of Cameras")
    print("\t {}:- {}".format(CameraID.LEFT.name, l))
    print("\t {}:- {}".format(CameraID.RIGHT.name, r))

    s.quit()
