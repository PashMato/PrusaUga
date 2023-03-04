import os

import numpy as np

from PythonCore.k_command_manger import KCommandManager


class BaseConverter:
    def __init__(self, path: str):
        self.path = os.path.expanduser(path)
        name = path.split("/")[-1].split(".")[0].lower()
        self.name = name[0].upper() + name[1:]
        self.KCode_manager: KCommandManager = KCommandManager(self.name, [], np.array([1, 1]))  # noqa

    def get_k_code(self, mode: str = None) -> KCommandManager:
        # the only function that the that is used outside class
        return KCommandManager(f"{self.name} Empty", [], np.array([1, 1]))






