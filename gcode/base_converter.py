import os

import matplotlib.pyplot as plt
import numpy as np

from log.log import message
from gcode.g_code_manager import GCodeManager


class BaseConverter:
    def __init__(self, file_name: str):
        self.file_name = os.path.expanduser(file_name)
        self.name = file_name.split("/")[-1].split(".")[0].title()

        self.lines = []
        self.size = np.array([100, 100])

        self.GCM = GCodeManager(self.name, [], self.size)

    def get_lines(self):
        self.lines = []

        raise NotImplemented(f"You are calling the an Empty function from the class `{self.__class__.__name__}`. " +
                             "this function should be overriden")

    def g_show(self):
        self.GCM.g_show()

        message("Loading Image...", message_type="Info")
        plt.show(block=True)
