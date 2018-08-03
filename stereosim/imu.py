import serial
import serial.tools.list_ports as list_ports
import json
from threading import Thread
from threading import Event


class IMU():

    def __init__(self):
        self.last_data = dict()
        self.ser_port = serial.Serial(baudrate=115200)
        self.thread = None
        self.kill = Event()
        self.is_connected = False

    def connect(self):  # connect to IMU Unit
        ports = list_ports.comports()
        imu_port_list = list(
            filter(lambda x: x.vid == 9025 and x.pid == 32823, ports))
        self.ser_port.port = imu_port_list[0][0]
        print('Found {:d} IMU units, using: {:s}'.format(
            len(imu_port_list), self.ser_port.port))  # TODO: Logging
        try:
            self.ser_port.open()
            # threaded serial listener
            self.thread = Thread(target=self.rx_thread)
            self.thread.start()
        except Exception:
            print("IMU Connection Failed!")  # TODO: Logging
            self.is_connected = False
        else:
            print("IMU Connected Sucessfully!")  # TODO: Logging
            self.is_connected = True
        return self.is_connected

    def rx_thread(self):  # threaded process that handles serial input
        buffer_string = ''
        self.ser_port.readline()  # clear incomplete line in buffer
        while not self.kill.is_set():
            buffer_string = buffer_string + \
                self.ser_port.read(self.ser_port.inWaiting()).decode()
            if '\n' in buffer_string:
                # Guaranteed to have at least 2 entries
                lines = buffer_string.split('\n')
                IMU_string = lines[-2].strip()
                try:
                    self.last_data = json.loads(IMU_string)
                except Exception:
                    print("IMU Parse Error")  # TODO: Logging
                buffer_string = lines[-1]  # keeps buffer small

    def getData(self):  # Fetch latest data
        return self.last_data

    def disconnect(self):
        self.kill.set()
        self.thread.join()
        self.ser_port.close()
        print("Serial Port Closed!")  # TODO: Logging
