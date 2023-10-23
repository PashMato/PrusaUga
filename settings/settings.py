import os
import shutil

import json5
import numpy as np
import pandas as pd

from settings.data import Data  # noqa

prop_options = {
    "PenUpFore": float,
    "HeadSpeedRatio": float,
    "PrintingSpeedFactor": float,
    "TouchDownLength": float,
    "WaitingTime": float,
    "StaticSpeed": float,
    "WaitingSpeed": float,
}


def abs_path(path: str) -> str:
    """
    the absolute path
    :param path: the relative path
    :return: the absolute path
    """
    return "".join(os.path.split(__file__)[:-1]) + "/" + path


def get_all_versions() -> set[float]:
    """
    :returns all the possibles versions
    """
    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json")) \
        .reset_index() \
        .drop("index", axis=1)

    return set(settings["version"].values)


def get_setting_path_by_version(version: float) -> str:
    """
    get setting path by version
    :param version: the input version
    :return: the version's path
    """
    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json")) \
        .reset_index() \
        .drop("index", axis=1)

    if version not in settings["version"].values:
        raise ValueError("No such setting")

    return settings[settings["version"] == version]["path"].values[0]


def set_settings(version: float) -> dict:
    """
    set a setting by version
    :param version:
    :return:
    """
    path = get_setting_path_by_version(version)

    with open(path, "r") as conf:
        data = json5.load(conf)

    Data.update_values(data)
    Data.SettingsVersion = version
    return data


def add_setting(version: float, file_path: str):
    """
    add setting
    :param version: the version name (to be set) can't override other versions
    :param file_path: the version path
    """

    file_path = abs_path(file_path) if file_path.startswith('.') else os.path.expanduser(file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File path `{file_path}` doesn't exits")
    if not os.path.isfile(file_path):
        raise ValueError(f"File path `{file_path}` must be a file (not a directory)")

    path = abs_path(os.path.split(file_path)[-1])

    # copy the file to the setting file
    if file_path != path:
        shutil.copy(file_path, path)

    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json"))

    # make sure that we aren't overriding any versions
    if version in settings["version"].values:
        raise ValueError("Key already exits. to override it you need to turn on override mode")

    # add the new 'link' to setting dict
    settings = pd.concat([settings, pd.DataFrame({"version": [version], "path": [path]})])\
        .reset_index()\
        .drop("index", axis=1)

    # write the new dict
    with open(abs_path("setting_dict.json"), 'w') as settings_file:
        settings_file.write(settings.to_json())


def edit_setting(version: float, prop: str, value):
    path = get_setting_path_by_version(version)

    assert prop not in prop_options.values()

    # open the setting file
    with open(path, "r") as conf:
        setting: dict = json5.load(conf)

    # makes sure that the prop is correct format
    if not set(setting.keys()).issubset(set(prop_options.keys())):  # number of arguments
        raise ImportError(f"Setting file in `{path}` doesn't include all required properties\nmissing {set(prop_options.values()).difference(set(prop_options.values()))}")
    if type(value) != prop_options[prop]:  # type
        raise ValueError(f"Property `{prop}` type's should be {prop_options[prop]}, not {type(value)}")

    setting[prop] = value
    with open(path, "w") as conf:
        json5.dump(setting, fp=conf)


def remove_setting(version: float):
    p_path = get_setting_path_by_version(version)

    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json"))\
        .reset_index()\
        .drop("index", axis=1)

    settings = settings.drop(np.argwhere(settings["version"].values == version)[0, 0])

    # if not a single version 'links' to path delete the file
    if np.all(settings["path"].values != p_path) and os.path.exists(p_path):
        os.remove(p_path)

    with open(abs_path("setting_dict.json"), 'w') as settings_file:
        settings_file.write(settings.to_json())
