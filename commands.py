import os.path

from log.log import message, FormatError, DoesNotExitsError, TooManyArgsError
from heandle_svg.svg2lines import Svg2Lines

from settings.settings import (add_setting, edit_setting, remove_setting, get_all_versions, prop_options,
                               get_setting_path_by_version)
from settings.data import Data

from gcode.gcode_base_comands import get_mode_drawing


def path_check(file_name: str):
    if not os.path.exists(os.path.expanduser(file_name)):
        raise FileNotFoundError(f"No such file as `{file_name}` ({os.path.expanduser(file_name)})")


def read_file(file_name: str):
    file_format = file_name.split(".")[-1]
    if file_format == "svg":
        return Svg2Lines(file_name)
    else:
        raise FormatError(f"file format `{file_format}` is not supported")


def add_version(version: float, path: str):
    try:
        version = float(version)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not find path `{path}`")

        add_setting(version, path)
        message(f"Adding setting `{path}` as `{version}`", message_type="Info")
    except ValueError:
        raise ValueError(f"Version must be float (not `{version}`)")


def remove_version(version: float):
    if version not in get_all_versions():
        DoesNotExitsError(f"No Such Version {get_all_versions()}")
    message(f"Removing setting `{version}` at `{get_setting_path_by_version(version)}`", message_type="Info")
    remove_setting(version)


def edit_version(version: float, prop, value):
    # prop check
    if prop is None:
        raise ValueError(" --prop must be given while editing")

    if value is None:
        ValueError(f" --value must be given while editing")

    if prop != "DrawingSize" and len(value) > 1:
        raise TooManyArgsError("Too many args. one arg is expected")

    if prop == "DrawingSize" and len(value) != 2:
        raise TooManyArgsError("Too many args. two args are expected")

    # editing the version
    try:
        if prop == "DrawingSize":
            value = (int(value[0]), int(value[1]))
        else:
            value = float(value[0])
        edit_setting(version, prop, value)
    except ValueError:
        raise ValueError(f"Cannot convert ({value}) to {prop_options[prop]}")


def set_mode(mode: int = 0):
    if mode not in {0, 1, 2, 3, 4}:
        raise ValueError('Mode must be in {0, 1, 2, 3, 4} not ' + str(mode))

    Data.Mode = mode
    mode_help = get_mode_drawing()

    message(f"""Setting Mode to {mode} \n{mode_help}""", message_type="Info")
