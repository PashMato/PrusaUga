from matplotlib.pyplot import *


class Data:
    KernelSize = 1
    HeadMovingSpeed = 2  # cm/s
    PointsRes = .25  # cm
    DrawingSize = np.array([15, 30])  # cm
    AllDrawingSizes = [(25, 30)]
    HeadSpeedRatio = 1
    MMPerPoint = 1

    ShiftX = 0
    ShiftY = 0

    @staticmethod
    def set_up(size: np.array):
        Data.KernelSize = max(np.int_(size / (Data.DrawingSize / Data.PointsRes))) + 1
        if Data.KernelSize <= 0:
            Data.KernelSize = 1

    @staticmethod
    def late_set_up(size: np.array):
        Data.MMPerPoint = np.min(Data.DrawingSize * 10 / size)
        Data.ShiftX = size[1] / 2
        Data.ShiftY = size[0] / 2




