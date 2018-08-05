import sys
from stereosim import MAZE
from subprocess import call
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Console(object):

    def __init__(self, maze):
        self.maze = maze
        self.viewtoggle = False

    def command_help(self):
        print('-----------------------------------------------------------------')
        print('                         Commands List                           ')
        print('-----------------------------------------------------------------')
        print(' n - To start new session')
        print(' p - To set PTU direction')
        print(' c - To capture an image')
        print(' m - To take a mosaic')
        print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
        print(' v - To view latest image')
        print(' b - To take a bunch of pictures at one PTU direction')
        print(' t - To toggle image preview')
        print(' q - To quit the code')
        print('-----------------------------------------------------------------')

    def test_case(self, command_input):
        options = {'n': self.new_session,
                   'p': self.point,
                   's': self.settings,
                   'c': self.capture,
                   'm': self.mosaic,
                   # 'v': self.maze.view,
                   'b': self.bulk,
                   't': self.toggleview,
                   'q': self.quit,
                   '?': self.command_help}
        try:
            options[command_input]()
        except KeyError:
            print('Enter Valid Option')
            self.command_help()

    def capture(self):
        print('Capturing an image...')
        saved_images = self.maze.capture

        if(self.viewtoggle):
            for image in saved_images:
                self.preview(image[0])

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
        arr = arr.reshape((-1, 2))
        return arr

    def mosaic(self):  # TODO: should use a better formatting for input...
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

    def settings(self):
        print('Setting up camera Parameters')
        self.maze.settings()
        print("Press `s` key if you want to get the camera parameters")

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

        self.maze.point((az, el))

    def bulk(self):
        # take  a bunch of pictures
        amount = input("\n Input the number of images you want to take ")
        num = int(amount)
        self.maze.bulk(num)

    def toggleview(self):
        self.maze.viewtoggle = not self.maze.viewtoggle

    def new_session(self):
        no = self.maze.new_session()
        print("New session with no: {} started".format(no))

    def preview(self, file):
        #img = Image.open(path+"/LEFT/L_"+name)
        # img.show() #TODO: show by path...
        call(["eog", file, "&"])

    def quit(self):
        self.maze.quit()
        print('quit')
        sys.exit()
