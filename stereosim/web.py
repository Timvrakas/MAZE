import logging
from stereosim.maze import MAZE
from stereosim.session import start_session
import remi.gui as gui
from remi import start, App

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class WebUI(App):
    def __init__(self, *args):
        self.maze = MAZE()
        self.connected = False
        super(WebUI, self).__init__(*args)

    def main(self):
        container = gui.VBox(width=600, height=400)
        self.bt = gui.Button('Connect')
        self.lbl = gui.Label('Not Connected')


        # setting the listener for the onclick event of the button
        self.bt.set_on_click_listener(self.connect_button)

        # appending a widget to another, the first argument is a string key
        container.append(self.bt)
        container.append(self.lbl)

        # returning the root widget
        return container

    # listener function
    def connect_button(self, widget):
        if self.connected:
            self.maze.disconnect()
            self.lbl.set_enabled(False)
            self.bt.set_text('Connect')
        else:
            self.maze.connect()
            self.bt.set_text('Disconnect')


def main():
        start(WebUI)


if __name__ == "__main__":
    main()
