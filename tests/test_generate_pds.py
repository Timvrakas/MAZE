#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy
from numpy.testing import assert_almost_equal
from stereosim import generate_pds
from planetaryimage import PDS3Image


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/')
filename_right = os.path.join(DATA_DIR, 'IMG_0491.JPG')
filename_left = os.path.join(DATA_DIR, 'IMG_0603.JPG')


def test_generate_pds_with_cahvor_left():
    generate_pds.PDSGenerator(filename_left)
    image = PDS3Image.open(os.path.splitext(filename_left)[0] + '.IMG')
    assert image.bands == 3
    assert image.lines == 1024
    assert image.samples == 1536
    assert image.format == 'BAND_SEQUENTIAL'
    assert image.dtype == numpy.dtype('>i2')

    # Testing .label
    assert image.label['^IMAGE'] == 2
    assert image.label['IMAGE']['SAMPLE_TYPE'] == 'MSB_INTEGER'
    assert image.label['IMAGE']['MAXIMUM'] == 91.0
    assert image.label['IMAGE']['MEDIAN'] == 8.0
    assert image.label['IMAGE']['MINIMUM'] == 0.0
    assert image.label['IMAGE']['SAMPLE_BITS'] == 16
    C = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_1']
    A = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_2']
    H = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_3']
    V = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_4']

    assert image.data.dtype == numpy.dtype('>i2')
    assert_almost_equal(C, [0.762, 1.4097, -3.3667])
    assert_almost_equal(A, [-0.9965459569473566, -0.0789023704157911,
                            -0.025895397943394106])
    assert_almost_equal(H, [23222.553666216594, -3668.4647892385674,
                            -218.30723379448355])
    assert_almost_equal(V, [-71.89351162208236, -1837.818951993951,
                            23237.35009760759])
    os.remove(os.path.splitext(filename_left)[0] + '.IMG')


def test_generate_pds_with_cahvor_right():
    generate_pds.PDSGenerator(filename_right)
    image = PDS3Image.open(os.path.splitext(filename_right)[0] + '.IMG')
    assert image.bands == 3
    assert image.lines == 2048
    assert image.samples == 3072
    assert image.format == 'BAND_SEQUENTIAL'
    assert image.dtype == numpy.dtype('>i2')

    # Testing .label
    assert image.label['^IMAGE'] == 2
    assert image.label['IMAGE']['SAMPLE_TYPE'] == 'MSB_INTEGER'
    assert image.label['IMAGE']['MAXIMUM'] == 152.0
    assert image.label['IMAGE']['MEDIAN'] == 6.0
    assert image.label['IMAGE']['MINIMUM'] == 0.0
    assert image.label['IMAGE']['SAMPLE_BITS'] == 16
    C = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_1']
    A = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_2']
    H = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_3']
    V = image.label['GEOMETRIC_CAMERA_MODEL']['MODEL_COMPONENT_4']

    assert image.data.dtype == numpy.dtype('>i2')
    assert_almost_equal(C, [0.762, -1.4097, -3.3667])
    assert_almost_equal(A, [-0.9944904168251026, -0.0014849543217824183,
                            0.10481701080309513])
    assert_almost_equal(H, [23503.278833922475, -611.6639911280982,
                            118.4987568245268])
    assert_almost_equal(V, [-118.76981483988821, -47.17355566761959,
                            23309.672994764074])
    os.remove(os.path.splitext(filename_right)[0] + '.IMG')
