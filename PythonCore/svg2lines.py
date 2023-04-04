import numpy as np
import sys
from tqdm import tqdm
import svg.path
from xml.dom import minidom

from PythonCore.base_converter import BaseConverter
from PythonCore.k_command_manager import KCommandManager
from PythonCore.data import Data

from PythonCore.parse_nested_svg import NestedSvgParser


class Svg2Lines(BaseConverter):
    def __init__(self, file_name: str):
        super(Svg2Lines, self).__init__(file_name)

        self.nsp: NestedSvgParser = NestedSvgParser(self.file_name)
        self.size = self.nsp.size.copy()

    def get_k_code(self, scale: float = 4) -> KCommandManager:
        km = KCommandManager(self.name, [], self.size)
        start_pos = self.size // 2
        for obj in tqdm(self.nsp.get_arrays()):
            km += np.array([start_pos[0], start_pos[1], obj[0][0], obj[1][0], 0])
            start_pos = np.array([obj[0][0], obj[1][0]])
            for n in range(1, obj[0].shape[0]):
                if not 0 <= obj[0][n] <= self.size[0] or not 0 <= obj[1][n] <= self.size[1]:
                    print("Error: drawing is too big.\n" +
                          f"couldn't fit the drawing into a canvas in a size of `{self.size}`. \n" +
                          "you must make sure that the drawing fits in the canvas")
                    exit(1)
                km += np.array([start_pos[0], start_pos[1], obj[0][n], obj[1][n], 1])
                start_pos = np.array([obj[0][n], obj[1][n]])

        Data.MMPerPoint = 1
        Data.ShiftX, Data.ShiftY = self.size // 2
        self.KCM = km
        self.KCM.optimize()
        return self.KCM


def main():
    filename = sys.argv[1]
    s2l = Svg2Lines(filename)
    s2l.get_k_code()
    s2l.k_show()


if __name__ == '__main__':
    main()
