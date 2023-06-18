import os
import numpy as np

from PythonCore.data import Data
from matplotlib import pyplot as plt

from datetime import date
from tqdm import tqdm


class KCommandManager:
    def __init__(self, label, commands: list[np.ndarray], canvas_size: np.ndarray):
        self.label = label
        self.commands = commands
        self.canvas_size = canvas_size

        self.commands_num = len(self.commands)
        self.removed_commands = 0
        self.head_ups_num = 0

    def __add__(self, other):
        if type(other) == KCommandManager:
            assert not np.any(other.canvas_size != self.canvas_size), \
                f"Error: CanvasSize must be the same for adding not `{other.canvas_size}`, `{self.canvas_size}`"
            self.commands += other.commands
            return self
        elif type(other) == np.ndarray:
            assert other.shape == (5,), f"Error: invalid line `{str(other)}`"
            self.commands.append(other.copy())
            return self
        elif other is None:
            return self
        else:
            raise Exception(f"Error: cannot add type `{type(other)}` with type `{type(self)}`")

    def __reversed__(self):
        km = KCommandManager(self.label, list(reversed(self.commands)), self.canvas_size)
        return km

    def __str__(self):
        return f"KCommandManager of `{self.label}` who has {len(self.commands)} commands and canvas size of {self.canvas_size}" # noqa

    @staticmethod
    def decode(line: np.ndarray, shift=True) -> tuple[np.ndarray, np.ndarray, bool]:
        if shift:
            s_pos = line[0:2] - np.array([Data.ShiftX, Data.ShiftY])
            e_pos = line[2:4] - np.array([Data.ShiftX, Data.ShiftY])
        else:
            s_pos = line[0:2]
            e_pos = line[2:4]
        is_printing = bool(line[4])
        return s_pos, e_pos, is_printing

    def optimize(self):
        self.head_ups_num = len(self.commands)

        for command in tqdm(self.commands):
            self.head_ups_num -= command[4]

    def to_gcode(self) -> str:
        zpos = 3
        did_print_already = False
        comments = f"""; gcode generated at ({date.today()}) with PrusaUgaSlicer
; gcode for {self.label}

; relative moving
; the start point of the head is the center of the drawing

        """
        meta_data = f"""
; meta data
G17 (use XY plane)
G21 (all units in mm)
G90 (use absolute position)

G1 F{400 * Data.PrintingSpeedFactor}

; 'popping' a little bit of sauce
G0 X{-Data.ShiftY * Data.MMPerPoint} Y{-Data.ShiftX * Data.MMPerPoint}
G1 Z-20
G1 Z{zpos}
G1 Z-20
G0 X0 Y0
G1 Z{zpos - 2}

; code

        """

        code = ""
        if self.commands[0][4] == 1:
            zpos += Data.PenUpFore * Data.PrintingSpeedFactor * Data.HeadSpeedRatio  # compute the start fore
            code = f"G1 F{400 * Data.PrintingSpeedFactor} Z{zpos}\n"

        for n, line in tqdm(enumerate(self.commands[:-1])):
            s_pos, e_pos, is_printing = self.decode(line)
            ns_pos, ne_pos, nis_printing = self.decode(self.commands[n + 1])

            ndpos, dpos = ne_pos - ns_pos, e_pos - s_pos

            dotp = np.dot(ndpos, dpos) / (np.linalg.norm(ndpos) * np.linalg.norm(dpos))
            xp = [-1, .5, 1]
            yp = [1.5, 1, 0]
            wait = np.interp(dotp, xp, yp) if is_printing and nis_printing else 0

            if wait <= 0.05:
                gwait = ""
            else:
                gwait = f"""G1 Z{zpos - wait * 10 / 6 * Data.PrintingSpeedFactor}
G1 Z{zpos}\n"""

            if is_printing:
                zpos += int(is_printing) * np.linalg.norm(dpos) * Data.MMPerPoint * Data.HeadSpeedRatio
                line_gcode = f"G1 X{e_pos[1]} Y{e_pos[0]} Z{zpos}\n"
            else:
                line_gcode = f"""
G1 F{20 * Data.PrintingSpeedFactor} Z{zpos - 3 * Data.PrintingSpeedFactor}
G0 X{e_pos[1]} Y{e_pos[0]}
G1 F{400 * Data.PrintingSpeedFactor}\n"""

            if (not is_printing) and nis_printing:
                if not did_print_already:
                    did_print_already = True
                    penup_fore = ""
                else:
                    zpos += Data.PenUpFore * Data.PrintingSpeedFactor * Data.HeadSpeedRatio  # compute the start fore
                    penup_fore = f"G1 F{400 * Data.PrintingSpeedFactor} Z{zpos}\n\n"
            else:
                penup_fore = ""

            code += line_gcode + gwait + penup_fore

        gcode = comments + meta_data + code
        gcode += f"\nG1 Z{zpos - 2}\nG0 X{-Data.ShiftY * Data.MMPerPoint} Y{-Data.ShiftX * Data.MMPerPoint}" # noqa

        return gcode

    def write_file(self, file_name, save_outline: bool = True):
        full_path = os.path.expanduser(file_name)

        name = full_path.split('/')[-1].replace(" ", "-").split('.')[0]
        path = '/'.join(full_path.split('/')[:-1])

        if os.path.exists(full_path):
            name = self.label.replace(" ", "-")
            path = full_path

        print(f"Saving file in: `{path}`, as: `{name}-{Data.SettingsVersion}.gcode`")
        with open(f"{path}/{name}-{Data.SettingsVersion}.gcode", "w") as file:
            file.write(self.to_gcode())
            file.close()
            print("Done Saving")

        gtest = f"""; gcode generated at ({date.today()}) with PrusaUgaSlicer
; test gcode for {self.label}

; make sure that the drawing fits

; relative moving
; the start point of the head is the center of the drawing

; meta data
G17 (use XY plane)
G21 (all units in mm)
G90 (use absolute position)

G1 F{1000 * Data.PrintingSpeedFactor}

; code

G0 X{(0 - Data.ShiftX) * Data.MMPerPoint} Y{(0 - Data.ShiftY) * Data.MMPerPoint}
G1 X{(self.canvas_size[1] - Data.ShiftX) * Data.MMPerPoint} Y{(0 - Data.ShiftY) * Data.MMPerPoint}
G1 X{(self.canvas_size[1] - Data.ShiftX) * Data.MMPerPoint} Y{(self.canvas_size[0] - Data.ShiftX) * Data.MMPerPoint}
G1 X{(0 - Data.ShiftX) * Data.MMPerPoint} Y{(self.canvas_size[0] - Data.ShiftX) * Data.MMPerPoint}
G1 X{(0 - Data.ShiftX) * Data.MMPerPoint} Y{(0 - Data.ShiftY) * Data.MMPerPoint}
G0 X0 Y0
        """

        if save_outline:
            print(f"Saving file in: `{path}`, as: `{name}-{Data.SettingsVersion}-Outline.gcode`")
            with open(f"{path}/{name}-{Data.SettingsVersion}-Outline.gcode", "w") as file:
                file.write(gtest)
                file.close()
                print("Done Saving")

    def k_show(self, color="b", head_up_color="r", size=".", linewidth="1.5"):
        plt.figure()
        for line in tqdm(self.commands):
            if line[4]:
                plt.plot([line[0], line[2]], [line[1], line[3]], color + size, linestyle="-", linewidth=linewidth)
            else:
                plt.plot([line[0], line[2]], [line[1], line[3]], head_up_color + size, linestyle="-.")

        plt.table(cellText=[[f"Head up: {self.head_ups_num}",
                         f"Overall commands: {len(self.commands)}"]], cellLoc="left", loc="top", edges="open")
        plt.gca().invert_yaxis()
        plt.axis("equal")
        plt.xlabel(self.label)









