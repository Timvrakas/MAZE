#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'pyyaml',
    'gphoto2',
    'exifread',
    'flir_ptu',
    'pyserial',
    'ocrd-pyexiftool'
]

setup(
    name='stereosim',
    version='0.1.0',
    description="Mastcam-Z Stereo Simulator System",
    long_description=readme + '\n\n' + history,
    author="Austin Godber",
    author_email='godber@asu.edu',
    url='https://genovesa.sese.asu.edu/godber/stereosim',
    packages=[
        'stereosim',
    ],
    package_dir={'stereosim':
                 'stereosim'},
    include_package_data=True,
    install_requires=requirements,
    dependency_links=['git+https://github.com/nikhilkalige/flir.git#egg=flir_ptu'],
    license="BSD",
    zip_safe=False,
    keywords='stereosim',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        "console_scripts": [
            "generate_pds = stereosim.generate_pds:main",           
            "populate_pds = stereosim.populate_pds:main",
            "capture = stereosim.capture:main"
        ]
    }
)
