import numpy as np

# !!!!
# it's important to say that every thing is not shifted and not scaled until we write to the gcode
# !!!!


class Data:
    ShiftX = 0
    ShiftY = 0

    # settings properties
    PenUpFore = 1  # the given fore after a penup
    HeadSpeedRatio = 0.006  # head mm per length mm
    PrintingSpeedFactor = 1  # the printing speed factor
    TouchDownLength = 0  # the touch-down length
    WaitingTime = 1

    MMPerPoint = 1  # mm

    StaticSpeed = 400
    WaitingSpeed = 10

    SettingVersion = 2.5
    Mode = 0  # From Where Should Start Printing (Center, What Corner)

    @staticmethod
    def update_mode(size: np.array):
        """
        set the shift according to the size and mode
        :param size: canvas size
        """
        if Data.Mode == 0:
            Data.ShiftX, Data.ShiftY = -size / 2
        elif Data.Mode == 1:
            Data.ShiftX, Data.ShiftY = -size[0], 0
        elif Data.Mode == 2:
            Data.ShiftX, Data.ShiftY = -size
        elif Data.Mode == 3:
            Data.ShiftX, Data.ShiftY = 0, -size[1]
        elif Data.Mode >= 4:
            Data.ShiftX, Data.ShiftY = 0, 0

    @staticmethod
    def update_values(vals: dict):
        """
        update the Data values through a dict of values
        :param vals: the new values
        """
        Data.PrintingSpeedFactor = vals["PrintingSpeedFactor"]  # the printing speed factor

        Data.PenUpFore = vals["PenUpFore"] # the given fore after a penup
        Data.HeadSpeedRatio = vals["HeadSpeedRatio"]  # head mm per length mm
        Data.TouchDownLength = vals["TouchDownLength"]  # the touch-down length
        Data.WaitingTime = vals["WaitingTime"]  # the touch-down length

        Data.StaticSpeed = vals["StaticSpeed"] * Data.PrintingSpeedFactor
        Data.WaitingSpeed = vals["WaitingSpeed"] * Data.PrintingSpeedFactor

