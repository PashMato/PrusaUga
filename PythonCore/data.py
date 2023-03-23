from matplotlib.pyplot import *


class Data:
    KernelSize = 1
    DrawingSize = np.array([20, 20])  # cm
    LineThickness = 0.5  # cm
    PenUpFore = 2  # the given fore after a penup
    HeadSpeedRatio = 1/8  # head mm per length mm
    PrintingSpeedFactor = 2  # the printing speed factor
    HeadMovingSpeed = 2  # cm/s
    MMPerPoint = 1  # mm

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

    @staticmethod
    def set_setting(Vals: dict):
        Data.DrawingSize = np.array(Vals["DrawingSize"])  # cm
        Data.LineThickness = Vals["LineThickness"]  # cm
        Data.PenUpFore = Vals["PenUpFore"]  # the given fore after a penup
        Data.HeadSpeedRatio = Vals["HeadSpeedRatio"]  # head mm per length mm
        Data.PrintingSpeedFactor = Vals["PrintingSpeedFactor"]  # the printing speed factor
        Data.HeadMovingSpeed = Vals["HeadMovingSpeed"]  # cm/s
