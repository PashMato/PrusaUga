import numpy as np
import sys

from tqdm import tqdm

from heandle_svg.parse_nested_svg import NestedSvgParser
from gcode.base_converter import BaseConverter
from gcode.g_code_manager import GCodeManager

from log.log import CanvasError


class Svg2Lines(BaseConverter):
    def __init__(self, file_name: str):
        super(Svg2Lines, self).__init__(file_name)

        self.parse_svg = NestedSvgParser(self.file_name)
        self.size = self.parse_svg.size.copy()

    def get_lines(self, scale: float = 4):
        self.lines = []

        raw_data = self.parse_svg.get_arrays()
        commends = []
        for stroke in tqdm(raw_data):
            arr = np.array(stroke).T

            if np.any(arr < 0) or np.any(arr > self.size[np.newaxis, :]):
                raise CanvasError(f"Drawing too big could not fit drawing into canvas {self.size}")

            # making sure that the first commands is goto
            is_printing = np.ones(arr.shape[0])[:, np.newaxis]
            is_printing[0] = 0

            commends += list(np.c_[arr, is_printing])

        self.lines = commends
        self.GCM = GCodeManager(self.name, self.lines, self.size)


def main():
    from settings.settings import set_settings
    filename = sys.argv[1]
    set_settings(2.5)

    s2l = Svg2Lines(filename)
    s2l.get_lines()
    s2l.GCM.write_file("~")


if __name__ == '__main__':
    main()