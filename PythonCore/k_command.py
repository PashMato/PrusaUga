import numpy as np

from PythonCore.data import Data


class KCommand:
    ZPos: float = 0

    def __init__(self, start_position: np.array, end_position: np.array, should_print: bool):
        self.start_position = start_position
        self.end_position = end_position
        self.should_print = should_print
        self.length = np.linalg.norm(self.end_position - self.start_position)
        self.time =  self.length *\
                    1000 * Data.PointsRes / Data.HeadMovingSpeed  # else it would be in seconds

    def __str__(self):
        XYZ = self.to_k_code(Data.ShiftX, Data.ShiftY)

        XYZ_label = ["X", "Y", "Z"]  # noqa

        if XYZ[2] == 0:
            massage = "$J=G90 G21 F2500"
        else:
            massage = "$J=G90 G21 F2000"

        for i in range(len(XYZ)):
            value = str(XYZ[i])[:5 + 1+len(str(int(XYZ[i])))]  # take the 5 first numbers after the digit
            massage += f" {XYZ_label[i]}{value}"

        return massage + "\n"

    def to_k_code(self, shift_x: float = 0, shift_y: float = 0):
        KCommand.ZPos += self.should_print.as_integer_ratio()[0] * self.length * Data.HeadSpeedRatio
        print(KCommand.ZPos)
        return np.array([(self.end_position[1] - shift_x) * Data.MMPerPoint,  # noqa
                         (self.end_position[0] - shift_y) * Data.MMPerPoint,
                         KCommand.ZPos], dtype=np.float) # noqa

