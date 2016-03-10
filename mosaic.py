import logging
from camera import StereoCamera, CameraID
from flir_ptu.ptu import PTU
import os
import yaml


def mosaic(camera, ptu, filepath, azimuth=0, elevation=0):
    increments = [(0, 0), (15, 0), (15, 0), (0, -15), (-15, 0), (-15, 0)]
    file_name_count = 1

    if not os.path.isdir(filepath):
        raise Exception("Invalid path: {}".format(filepath))

    # Move to the initial position
    ptu.pan_angle(azimuth)
    ptu.tilt_angle(elevation)

    curr_az = azimuth
    curr_el = elevation
    for inc in increments:
        curr_az += inc[0]
        curr_el += inc[1]

        ptu.pan_angle(curr_az)
        ptu.tilt_angle(curr_el)

        filename = str(file_name_count).zfill(5)
        logger.debug('Current Position:- Az: {}, El: {}, Current File:- {}'.format(curr_az, curr_el, filename))

        camera_files = camera.capture_image(filepath, '{}.dat'.format(filename))
        logger.debug(camera_files)
        pp = ptu.pan()
        tp = ptu.tilt()

        for f in camera_files:
            yaml_path = os.path.splitext(f)[0]
            contents = {
                'AZIMUTH': curr_az,
                'ELEVATION': curr_el,
                'PP': pp,
                'TP': tp
            }
            with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
                yaml.dump(contents, lblfile, default_flow_style=False)

        file_name_count += 1


if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    cam = StereoCamera()
    cam.detect_cameras()
    cam.get_summary()

    ptu = PTU("129.219.136.149", 4000)
    ptu.connect()

    cam.set_config('imageformat', 'Large Normal JPEG', CameraID.LEFT)
    cam.set_config('imageformat', 'Large Normal JPEG', CameraID.RIGHT)
    mosaic(cam, ptu, '/tmp/cam_files', 0, 0)
