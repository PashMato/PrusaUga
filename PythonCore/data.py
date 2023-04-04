import numpy as np


class Data:
    KernelSize = 1
    DrawingSize = np.array([20, 20])  # cm
    LineThickness = 0.5  # cm
    PenUpFore = 2  # the given fore after a penup
    HeadSpeedRatio = 1/8  # head mm per length mm
    PrintingSpeedFactor = 2  # the printing speed factor
    MMPerPoint = 1  # mm

    ShiftX = 0
    ShiftY = 0

    @staticmethod
    def set_up(size: np.array):
        Data.KernelSize = np.max(np.int_(size / (Data.DrawingSize / Data.LineThickness))) + 1
        if Data.KernelSize <= 0:
            Data.KernelSize = 1

    @staticmethod
    def late_set_up(size: np.array):
        Data.MMPerPoint = np.min(Data.DrawingSize * 10 / size)
        Data.ShiftY, Data.ShiftX = size // 2

    @staticmethod
    def set_setting(vals: dict):
        Data.DrawingSize = np.array(vals["DrawingSize"])  # cm
        Data.LineThickness = vals["LineThickness"]  # cm
        Data.PenUpFore = vals["PenUpFore"]  # the given fore after a penup
        Data.HeadSpeedRatio = vals["HeadSpeedRatio"]  # head mm per length mm
        Data.PrintingSpeedFactor = vals["PrintingSpeedFactor"]  # the printing speed factor
