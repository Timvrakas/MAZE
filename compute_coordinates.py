import math
import numpy as np


def compute_coordinates(c, az, el):
    """
    Computes coordinates of point 'c' after rotating it with
    specific AZ and EL.

    Parameters
    ----------
    c: array / vector (x,y,z)
        point for which one wants to compute coordinates after rotation.
    az: float
        Azimuth angle in degree.
    el: float
        Elevation angle in degree.

    Returns:
    c_new: array / vector
        Returns computed coordinate c_new by rotating c with specific AZ
        and EL.
    """
    el = math.radians(el)
    az = math.radians(az)

    c_new = np.zeros(3)

    # Calculation for specific AZ angle (Rotation around Z)
    c_new[0] = c[0] * math.cos(az) - c[1] * math.sin(az)
    c_new[1] = c[0] * math.sin(az) + c[1] * math.cos(az)
    c_new[2] = c[2]

    # Calculation for specific EL angle (Rotation around Y)
    c_new[0] = c_new[0] * math.cos(el) + c_new[2] * math.sin(el)
    c_new[1] = c_new[1]
    c_new[2] = c_new[2] * math.cos(el) - c_new[0] * math.sin(el)

    return c_new
