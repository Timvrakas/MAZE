import sys
from subprocess import call
import logging
import numpy as np
import stereosim.maze as maze
import stereosim.web_preview as web_preview
from multiprocessing import Process
from multiprocessing.managers import BaseManager
import time

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Console(object):

    def __init__(self):
        BaseManager.register('get_maze')
        manager = BaseManager(address=('', 50000), authkey=b'abc')
        manager.connect()
        self.maze = manager.get_maze()
        self.maze.connect()

    def command_help(self):
        print('-----------------------------------------------------------------')
        print('                         Commands List                           ')
        print('-----------------------------------------------------------------')
        print(' n - To start new session')
        print(' p - To set PTU direction')
        print(' c - To capture an image')
        print(' m - To take a mosaic')
        print(' s - To set camera parameteres (focal length, ISO, Aperture etc.)')
        print(' b - To take a bunch of pictures at one PTU direction')
        print(' q - To quit the code')
        print('-----------------------------------------------------------------')

    def test_case(self, command_input):
        options = {'n': self.new_session,
                   'p': self.point,
                   's': self.settings,
                   'c': self.capture,
                   'm': self.mosaic,
                   'b': self.bulk,
                   'q': self.quit,
                   '?': self.command_help}
        try:
            options[command_input]()
        except KeyError:
            print('Enter Valid Option')
            self.command_help()

    def capture(self):
        print('Capturing an image...')
        saved_images = self.maze.capture()

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
            positions = '0,0,15,0,30,0,30,-15,15,-15,0,-15'
            print('positions : (0, 0), (15, 0), (30, 0),'
                  '(30, -15), (15, -15), (0, -15)')
            print('-' * 50)
        if positions == 'q':
            self.quit()
        positions = self.pos_arr(positions)
        self.maze.mosaic(positions)

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
        amount = input("\n Input the number of images you want to take: ")
        num = int(amount)
        self.maze.bulk(num)

    def new_session(self):
        no = self.maze.new_session()
        print("New session with no: {} started".format(no))

    def quit(self):
        self.maze.disconnect()
        sys.exit()

def main():
        #Start MAZE Process
        Mp = Process(target=maze.main)
        Mp.start()
        logger.info('Started MAZE in PID: {}'.format(Mp.pid))
        time.sleep(0.1) #Wait for manager to spin up

        #Start Web Process
        Wp = Process(target=web_preview.startServer)
        Wp.start()
        logger.info('Started Web Server in PID: {}'.format(Wp.pid))

        #Start Console (This Process)
        console = Console()
        while True:
            command_input = input('> ')
            console.test_case(command_input)

if __name__ == "__main__":
    main()
