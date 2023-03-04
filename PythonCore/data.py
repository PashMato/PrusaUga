from matplotlib.pyplot import *


class Data:
    KernelSize = 1
    HeadMovingSpeed = 2  # cm/s
    LineThickness = .5  # cm
    DrawingSize = np.array([20, 20])  # cm
    AllDrawingSizes = [(25, 30)]
    HeadSpeedRatio = 1/8  # head mm per length mm
    PenUpFor = 2  # the given fore after a penup
    Speed = 2
    MMPerPoint = 1

    ShiftX = 0
    ShiftY = 0

    @staticmethod
    def set_up(size: np.array):
        Data.KernelSize = max(np.int_(size / (Data.DrawingSize / Data.LineThickness))) + 1
        if Data.KernelSize <= 0:
            Data.KernelSize = 1

    @staticmethod
    def late_set_up(size: np.array):
        Data.MMPerPoint = np.min(Data.DrawingSize * 10 / size)
        Data.ShiftY, Data.ShiftX = size // 2




