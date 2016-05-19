# -*- coding: utf-8 -*-
from sys import path
import configparser
import contextlib


class Session:
    CONFIG_FILE = '~/config/stereosim.ini'

    def setup(self):
        self.config = configparser.ConfigParser()
        if not path.isfile(self.CONFIG_FILE):
            self.config['DEFAULT'] = {
                'SessionNumber': 1,
                'ImageCount': 1
            }
            with open(self.CONFIG_FILE, 'w') as f:
                self.config.write(f)

        else:
            self.config.read(self.CONFIG_FILE)

    def session_number(self, new=False):
        session_number = self.config['DEFAULT']['SessionNumber']
        if new:
            session_number += 1

        return session_number

    def image_count(self, inc=False):
        count = self.config['DEFAULT']['ImageCount']
        if inc:
            count += 1
        else:
            return count

    def teardown(self):
        with open(self.CONFIG_FILE, 'w') as f:
            self.config.write(f)


@contextlib.contextmanager
def start_session():
    session = Session()
    try:
        session.setup()
        yield session
    finally:
        session.teardown()
