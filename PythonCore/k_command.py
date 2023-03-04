import numpy as np

from PythonCore.data import Data


class KCommand:
    ZPos: float = 0

    def __init__(self, start_position: np.array, end_position: np.array, should_print: bool):
        self.start_position: np.ndarray = start_position
        self.end_position: np.ndarray = end_position
        self.is_printing: bool = should_print
        self.length: float = np.linalg.norm(self.end_position - self.start_position)
        self.real_length: float = np.linalg.norm(self.end_position - self.start_position) * Data.MMPerPoint
        self.time: float = self.real_length / (Data.Speed * (200 * int(not self.is_printing)) + 200)

    def __eq__(self, other):
        return not (np.any(other.start_position != self.start_position) or
            np.any(other.end_position != self.end_position) or
            (self.is_printing != other.is_printing))

    def __str__(self):
        XYZ = self.to_k_code(Data.ShiftX, Data.ShiftY)

        XYZ_label = ["X", "Y", "Z"]  # noqa

        massage = "G1"

        for i in range(len(XYZ)):
            value = str(XYZ[i])[:5 + 1+len(str(int(XYZ[i])))]  # take the 5 first numbers after the digit
            massage += f" {XYZ_label[i]}{value}"

        massage += "\n"

        if not self.is_printing:
            massage = "\nG0" + massage[2:] + \
                      f"G1 Z{KCommand.ZPos - 100 * Data.Speed / 60} (wait a half second)\n"

            KCommand.ZPos += Data.PenUpFor * Data.Speed * Data.HeadSpeedRatio  # compute the start fore
            return massage + f"G1 Z{KCommand.ZPos} (wait a half second and give the suse a start fore)\n\n"
        else:
            massage += f"G1 Z{KCommand.ZPos - 100 * Data.Speed / 60} (wait a half second)\n" + \
                    f"G1 Z{KCommand.ZPos} (wait a half second)\n"
            return massage

    def to_k_code(self, shift_x: float = 0, shift_y: float = 0):
        KCommand.ZPos += int(self.is_printing) * self.real_length * Data.HeadSpeedRatio

        return np.array([(self.end_position[1] - shift_x) * Data.MMPerPoint,  # noqa
                         (self.end_position[0] - shift_y) * Data.MMPerPoint,
                         KCommand.ZPos], dtype=np.float) # noqa

    @staticmethod
    def Empty():
        return KCommand(np.zeros(2), np.zeros(2), False)
