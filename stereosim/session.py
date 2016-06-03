# -*- coding: utf-8 -*-
import os
import configparser
import contextlib
import datetime


class Session:
    CONFIG_FILE = '.config/stereosim.ini'

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.config_file_path = os.path.join(os.path.expanduser('~'), self.CONFIG_FILE)

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)


    def setup(self):
        self.config = configparser.ConfigParser()
        if not os.path.isfile(self.config_file_path):
            self.config['DEFAULT'] = {
                'SessionNumber': 1,
                'ImageCount': 1,
                'CurrentSessionFolder': ''
            }
            with open(self.config_file_path, 'w') as f:
                self.config.write(f)

        else:
            self.config.read(self.config_file_path)

        # Check folder existence
        folder = self.get_folder_path()
        if not os.path.exists(folder):
            os.mkdir(folder)

    def session_number(self, new=False):
        session_number = int(self.config['DEFAULT']['SessionNumber'])
        if new:
            session_number += 1
            self.config['DEFAULT']['SessionNumber'] = str(session_number)

        return int(session_number)

    def image_count(self, inc=False):
        count = int(self.config['DEFAULT']['ImageCount'])
        if inc:
            count += 1
            self.config['DEFAULT']['ImageCount'] = str(count)
        else:
            return int(count)

    def get_file_name(self):
        return "{:03d}_{:04d}.IMG".format(self.session_number(), self.image_count())

    def get_folder_path(self, new=False):
        if new:
            date = datetime.date.today().strftime("%d%m%Y")
            folder_name = "session_{:03d}_{}".format(self.session_number(), date)
            self.config['DEFAULT']['CurrentSessionFolder'] = folder_name
        else:
            folder_name = self.config['DEFAULT']['CurrentSessionFolder']

        return os.path.join(self.folder_path, folder_name)

    def new_session(self):
        no = self.session_number(new=True)
        folder = self.get_folder_path(new=True)
        os.mkdir(folder)
        # reset count
        self.config['DEFAULT']['ImageCount'] = '1'
        return no

    def teardown(self):
        with open(self.config_file_path, 'w') as f:
            self.config.write(f)


@contextlib.contextmanager
def start_session(folder_path="/tmp/stereosim"):
    session = Session(folder_path)
    try:
        session.setup()
        yield session
    finally:
        session.teardown()
