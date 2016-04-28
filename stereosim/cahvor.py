import numpy as np
from stereosim.compute_coordinates import compute_coordinates


def compute_CAHVOR(pinhole_model):
    """
    Computation of CAHVOR from photogrammetric parameters.

    Parameters
    ----------
    dict: dict
        Takes dictionary containing photogrammetric camera Parameters
        such as 'camera center', 'focallength', 'rotation matrix',
        'pixel size', 'principal point', 'image size' and 'az' and 'el'
        to get back to origin position of PTU.

    Returns:
    cahvor: dict
        Returns dict containing computed CAHVOR parameters from
        photogrammetric model.
    """
    hs = pinhole_model['f'] / pinhole_model['pixelsize']
    vs = pinhole_model['f'] / pinhole_model['pixelsize']
    hc = (pinhole_model['image_size'][1] / 2) + \
         (pinhole_model['principal'][0] / pinhole_model['pixelsize'])
    vc = (pinhole_model['image_size'][0] / 2) - \
         (pinhole_model['principal'][1] / pinhole_model['pixelsize'])

    C = pinhole_model['center']
    A = - pinhole_model['rotation_mat'][2, :]
    Hn = pinhole_model['rotation_mat'][0, :]
    Vn = - pinhole_model['rotation_mat'][1, :]

    H = hs * Hn + hc * A
    V = vs * Vn + vc * A
    O = A        # We assume O = A in converted CAHVOR Model

    # Fixing Axis specifically for PTU unit.
    A[0], A[1], A[2] = A[2], -A[0], -A[1]
    H[0], H[1], H[2] = H[2], -H[0], -H[1]
    V[0], V[1], V[2] = V[2], -V[0], -V[1]
    O[0], O[1], O[2] = O[2], -O[0], -O[1]

    A = compute_coordinates(A, pinhole_model['az'], pinhole_model['el'])
    H = compute_coordinates(H, pinhole_model['az'], pinhole_model['el'])
    V = compute_coordinates(V, pinhole_model['az'], pinhole_model['el'])
    O = compute_coordinates(O, pinhole_model['az'], pinhole_model['el'])

    try:
        R = pinhole_model['K']
    except KeyError:
        R = None

    if not (R is None):
        R = np.array([R[0], R[1] * (pinhole_model['f']**2),
                      R[2] * (pinhole_model['f']**4)])
        R = compute_coordinates(R, pinhole_model['az'], pinhole_model['el'])

    cahvor = dict([('C', C), ('A', A), ('H', H), ('V', V), ('O', O), ('R', R),
                   ('hs', hs), ('hc', hc), ('vs', vs), ('vc', vc)])
    return cahvor
