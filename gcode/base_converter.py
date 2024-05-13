import os

import matplotlib.pyplot as plt
import numpy as np

from log.log import message
from gcode.g_code_manager import GCodeManager


class BaseConverter:
    def __init__(self, file_name: str):
        """
        automatically loads the file name's full path and name
        """
        self.file_name = os.path.expanduser(file_name)
        self.name = file_name.split("/")[-1].split(".")[0].title()

        self.lines = []
        self.size = np.array([100, 100])

        self.GCM = GCodeManager(self.name, [], self.size)

    def get_lines(self):
        """
        compute the lines and write them in to the class' GCodeManager instance
        """
        self.lines = []

        raise NotImplemented(f"You are calling the an Empty function from the class `{self.__class__.__name__}`. " +
                             "this function should be overriden")

    def get_canvas_edge_test(self) -> GCodeManager:
        """
        computes the gcode if you want to go around the edge of the canvas and draw lines
        :return: GCodeManager that go around the edge of the canvas and draw lines
        """
        commends = [np.array([0,            0,            0], float),
                    np.array([0,            self.size[1], 1], float),
                    np.array([self.size[0], self.size[1], 1], float),
                    np.array([self.size[0], 0,            1], float),
                    np.array([0,            0,            1], float)]
        return GCodeManager(self.name + "-Edge", commends, self.size)

    def g_show(self, block=True):
        """
        Plots the GCodeManager's gcode
        """

        self.GCM.g_show()

        message(f"Loading `{self.name}` Image...", message_type="Info")
        plt.show(block=block)

