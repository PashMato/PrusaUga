import os

import numpy as np

from PythonCore.k_command_manger import KCommandManager


class BaseConverter:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.name = path.split("/")[-1]
        self.KCode_manager: KCommandManager = KCommandManager(self.name, [], np.array([1, 1]))  # noqa

    def get_k_code(self, raster_mode: bool = False) -> KCommandManager:
        # the only function that the that is used outside class
        return KCommandManager("empty", [])






