#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest
import time
from stereosim import imu


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
