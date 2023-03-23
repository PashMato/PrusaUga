import os

import numpy as np
import pandas as pd
import shutil

import json5

from PythonCore.data import Data

prop_options = {
    "DrawingSize": tuple,
    "LineThickness": float,
    "PenUpFore": float,
    "HeadSpeedRatio": float,
    "PrintingSpeedFactor": float,
    "HeadMovingSpeed": float,
}


def abs_path(path: str) -> str:
    return "".join(os.path.split(__file__)[:-1]) + "/" + path


def get_settings_options() -> set[float]:
    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json")) \
        .reset_index() \
        .drop("index", axis=1)

    return set(settings["version"].values)


def set_settings(version: float) -> dict:
    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json")) \
        .reset_index() \
        .drop("index", axis=1)

    assert version in settings["version"].values, "No such setting"

    path = settings["path"].values[np.argwhere(settings["version"].values == version)[0, 0]]

    with open(path, "r") as conf:
        data = json5.load(conf)

    Data.set_setting(data)
    return data


def add_setting(version: float, file_path: str):
    if file_path[0] == '.':
        file_path = abs_path(file_path)
    else:
        file_path = os.path.expanduser(file_path)

    assert os.path.exists(file_path), f"File path `{file_path}` doesn't exits"
    assert os.path.isfile(file_path), f"File path `{file_path}` must be a file (not a directory)"

    path = abs_path(os.path.split(file_path)[-1])
    if file_path != path:
        shutil.copy(file_path, path)

    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json"))

    assert version not in settings["version"].values, \
        "Key already exits. to override it you need to turn on override mode"

    settings = pd.concat([settings, pd.DataFrame({"version": [version], "path": [path]})])\
        .reset_index()\
        .drop("index", axis=1)

    with open(abs_path("setting_dict.json"), 'w') as settings_file:
        settings_file.write(settings.to_json())


def edit_setting(version: float, prop: str, value):
    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json")) \
        .reset_index() \
        .drop("index", axis=1)

    assert version in settings["version"].values, "No such setting"

    assert prop not in prop_options.values()
    assert type(value) == prop_options[prop], \
        f"property `{prop}` type's should be {prop_options[prop]}, not {type(value)}"

    path = settings["path"].values[np.argwhere(settings["version"].values == version)[0, 0]]

    with open(path, "r") as conf:
        setting: dict = json5.load(conf)

    assert set(setting.keys()).issubset(set(prop_options.keys())), \
        f"setting file in `{path}` doesn't include all required properties\nmissing {set(prop_options.values()).difference(set(prop_options.values()))}"

    setting[prop] = value
    with open(path, "w") as conf:
        json5.dump(setting, fp=conf)


def remove_setting(version: float):
    settings: pd.DataFrame = pd.read_json(abs_path("setting_dict.json"))\
        .reset_index()\
        .drop("index", axis=1)

    assert version in settings["version"].values, "No such setting"

    p_path = settings["path"][np.argwhere(settings["version"].values == version)[0, 0]]
    settings = settings.drop(np.argwhere(settings["version"].values == version)[0, 0])

    if np.all(settings["path"].values != p_path) and os.path.exists(p_path):
        os.remove(p_path)

    with open(abs_path("setting_dict.json"), 'w') as settings_file:
        settings_file.write(settings.to_json())
