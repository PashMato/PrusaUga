import os

import numpy as np
import matplotlib.pyplot as plt

from PythonCore.k_command_manager import KCommandManager


class BaseConverter:
    def __init__(self, path: str):
        self.file_name = os.path.expanduser(path)
        self.name = path.split("/")[-1].split(".")[0].title()
        self.KCM: KCommandManager = KCommandManager(self.name, [], np.array([1, 1]))  # noqa

    def get_k_code(self, mode: str = None) -> KCommandManager:
        # the only function that the that is used outside class
        return KCommandManager(f"{self.name} Empty", [], np.array([1, 1]))

    def k_show(self):
        self.KCM.k_show()
        plt.show(block=True)








