import os
import yaml
import exiftool


def create_label(image_path, camera_name, ptu_angle, IMU_data,):
    """ Create label for captured image.
    Parameters
    ----------
    camera : camera_object
    file_path : str
    """

    with exiftool.ExifTool() as et:
        flmeta = et.get_tag('FocalLength', image_path)
        #meta = et.get_metadata(file_path)

    #focal_length = '{}'.format(meta['EXIF FocalLength'])
    #focal_length = '{}'.format(meta['XMP:FocalLength'])
    focal_length = '{}'.format(flmeta)

    #pp = ptu_dict['pp']
    #tp = ptu_dict['tp']
    az = ptu_angle[0]
    el = ptu_angle[1]
    IMU_quaternion = IMU_data["quat"]
    yaml_path = os.path.splitext(image_path)[0]
    contents = {
        'AZIMUTH': az,
        'ELEVATION': el,
        # 'PP': float(pp),
        # 'TP': float(tp),
        'f': float(focal_length),
        # 'pr': ptu.pan_res(),
        # 'tr': ptu.tilt_res(),
        # 'temp': ptu.ptu_temp(),
        'Camera': camera_name,
        'below values obtained by stereosim IMU:': 'see below',
        '': IMU_data,
        'IMU_quaternion': IMU_quaternion
    }
    with open('{}.lbl'.format(yaml_path), 'w') as lblfile:
        yaml.dump(contents, lblfile, default_flow_style=False)
