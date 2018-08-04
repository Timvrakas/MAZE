#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest
import time
from stereosim import imu
from flir_ptu.ptu import PTU


def test_imu_connect():
    imu_unit = imu.IMU()
    imu_unit.connect()
    imu_unit.disconnect()


def test_imu_data():
    imu_unit = imu.IMU()
    imu_unit.connect()
    time.sleep(3)
    print(imu_unit.getData())
    time.sleep(3)
    print(imu_unit.getData())
    time.sleep(3)
    print(imu_unit.getData())
    imu_unit.disconnect()

def test_ptu():
    ptu = PTU("10.5.1.2", 4000)
    ptu.connect()
    print(1)
    ptu.slew_to_angle((0,0))
    print(2)
    print(ptu.get_angle())
    time.sleep(3)
    print(3)
    ptu.slew_to_angle((10,10))
    print(4)
    print(ptu.get_angle())