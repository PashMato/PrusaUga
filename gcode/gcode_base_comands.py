import numpy as np

from datetime import date

from settings.data import Data


def create_metadata(ap_time, size) -> str:
    return f"""
; meta data
G17 (use XY plane)
G21 (all units in mm)
G90 (use absolute position)

; for canvas in the size ({np.abs(size[0])}, {np.abs(size[1])})
; approximate printing time {int(ap_time) + 1} minutes

G1 F{Data.StaticSpeed}

; 'popping' a little bit of sauce

G0 X{size[0] + Data.ShiftX} Y{size[1] + Data.ShiftY} 
G1 F{Data.WaitingSpeed} Z3
G1 F{Data.StaticSpeed} Z{Data.PenUpFore}
G1 F{Data.StaticSpeed * Data.HeadSpeedRatio} Z0

; code

"""


def get_mode_drawing() -> str:
    if Data.Mode == 0:
        mode_help = """
;         +-------------+
;         |             | 
;         | 0 -> X <- 0 |
;         |             | 
;         +-------------+
        """
    elif Data.Mode == 1:
        mode_help = """
;    1 -> X-------------+
;         |             | 
;         |             | 
;         |             | 
;         +-------------+
        """
    elif Data.Mode == 2:
        mode_help = """
;         +-------------X <- 2
;         |             | 
;         |             | 
;         |             | 
;         +-------------+
        """
    elif Data.Mode == 3:
        mode_help = """
;         +-------------+
;         |             | 
;         |             | 
;         |             | 
;         +-------------X <- 3
        """
    else:
        mode_help = """
;             +-------------+
;             |             | 
;             |             | 
;             |             | 
;        4 -> X-------------+
        """
    return mode_help


def create_comments(label: str, test=False, size=("None", "None")) -> str:
    a_test = ""
    comments = ("", "")
    if test:
        a_test = "test "
        comments = (
            "; make sure that the drawing fits\n"
            f"; test for canvas in the size ({size[0]}, {size[1]})\n"
        )

    return f"""; gcode generated at ({date.today()}) with PrusaUgaSlicer version 2.0.0
; {a_test}gcode for {label} 
{comments[0]}
; relative moving
{comments[1]}
; the start point of the head is in point `{Data.Mode}` of the drawing \n{get_mode_drawing()}
    """


def create_g_test(label: str, size) -> str:
    return (create_comments(label, test=True, size=size) +
f"""\n
; meta data
G17 (use XY plane)
G21 (all units in mm)
G90 (use absolute position)

G1 F{2000 * Data.PrintingSpeedFactor}

; code

G0 X{Data.ShiftX} Y{Data.ShiftY}
G1 X{size[0] + Data.ShiftX} Y{Data.ShiftY}
G1 X{size[0] + Data.ShiftX} Y{size[1] + Data.ShiftY}
G1 X{Data.ShiftX} Y{size[1] + Data.ShiftY}
G1 X{Data.ShiftX} Y{Data.ShiftY}
G0 X0 Y0
""")


def create_end_data() -> str:
    return f"\nG0 X{Data.ShiftX} Y{Data.ShiftY}\n"