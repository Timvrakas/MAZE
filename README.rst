===============================================
Stereosim - Mastcam-Z Stereo Simulator System
===============================================
This system is intended to simulate a stereo pair of adjustable focal length cameras to aid in the development of stereo analysis algorithms and inform the development of operational activities. The system is comprised of the following components:

* a FLIR pan tilt head
* a pair of DSLR cameras with manual zoom
* a computer to interface with the above items (i.e. a Raspberry Pi)
* supporting wiring and accessories

Features
--------
* Captures JPG Image with label containing PTU azimuth and elevation angles
* Captures 6 images required to create a mosaic
* Generates PDS image file from JPG Image

System Setup
------------

Stereosim uses the Linux `gphoto` package to interface with the cameras.  Users
will probably have to install the development versions of the following packages:

  sudo apt-get install gphoto2 libgphoto2-dev python3-dev


Depending on exactly which python version is in use, you might need a different
python `-dev` package.

Quickstart
----------
The example below will walk you through setting up a Python virtual environment
and installing the necessary software as well as a few handy extras. The example
assumes you have Python3, virtualenv, and pip installed on your system.

SSH to raspberry pi, create and activate a virtual environment::

  ssh pi@129.219.136.161
  virtualenv -p python3 venv
  source venv/bin/activate

Run setup.py, upgrade pip, then pip install the package and IPython notebook and
matplotlib to help display the image::

  python setup.py develop
  pip install -U pip
  pip install -r requirements.txt

This examples will show you the procedure to capture an Image::

  $ capture
    > ?
    -----------------------------------------------------------------
                             Commands List
    -----------------------------------------------------------------
     n - To start new session
     p - To set PTU direction
     c - To capture an image
     s - To set camera parameteres (focal length, ISO, Aperture etc.)
     v - To view sample image
     q - To quit the code
    -----------------------------------------------------------------
    >

These commands help performing the tasks listed above.

This example will show you the procedure to generate PDS file::

  $ generate_pds /path/to/captured/JPG/file

This example will show you the procedure of stereocamera calibration and saving
the calibration model::

  $ python save_stereosim_model.py /path/to/captured/checkerboard/images/

Network Configuration
---------------------
There are several hardcoded IP addresses used to connect to components for feild operation.
The Raspberry Pi is used as a wireless access point, hosting a wireless network on the subnet 10.5.0.1/24.
Additionaliy, the Pi uses ethernet to operate the PTU, over a statialy assigned wired network on 10.5.1.1/24.
The Pi is 10.5.1.1, and the PTU is 10.5.1.2. On top of this, the Pi runs a DHCP client over ethernet (to recvive internet while testing), 
and a DHCP Server over the WiFi connection, providing WiFi clients with internet access.

References
----------
**(1) What is PDS (Planetary Data Systems) ?** (https://pds.nasa.gov/about/about.shtml)

- Reference to the PDS Standards (https://pds.nasa.gov/tools/standards-reference.shtml)
- Sample PDS data Product (http://pds-imaging.jpl.nasa.gov/data/msl/MSLMST_0011/DATA/EDR/SURFACE/0935/)
- Label has an extension of '.LBL' and data has an extension of '.DAT' here on PDS Imaging node by JPL.

**(2) Introduction to CAHVOR Camera Models (https://github.com/bvnayak/CAHVOR_camera_model)**

- The link attached here is Github repository, which includes link for understanding Photogrammetric Model, CAHVOR Model and the Reference paper which converts CAHVOR camera model to the Photogrammetric Model and vice-versa.
- Reference Paper Link (http://onlinelibrary.wiley.com/doi/10.1029/2003JE002199/abstract)

**(3) What is FLIR PTU (Pan Tilt Unit) ?**

- http://www.flir.com/mcs/view/?id=53670

**(4) What is camera calibration ?**

- Link to understand Pinhole Camera Model (https://en.wikipedia.org/wiki/Pinhole_camera_model)
- Link for Camera Calibration (http://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html)
- Python version of above link (http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html?highlight=coefficients)
