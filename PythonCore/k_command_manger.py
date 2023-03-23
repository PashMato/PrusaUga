import os.path
from copy import copy

import numpy as np

from PythonCore.k_command import KCommand
from PythonCore.data import Data
from matplotlib import pyplot as plt

from datetime import date

class KCommandManager: # noqa
    def __init__(self, label: str, commands_protocols: list[KCommand], size: np.ndarray):
        self.label = label.title().replace(" ", "-")
        self.commands: list[KCommand] = commands_protocols
        self.times_head_up = 0
        self.removed_commands = 0
        self.overall_commands = 0
        self.canvas_size: np.ndarray = size.copy()
        self.average_length = 0
        self.average_per_min = 0

    def __str__(self) -> str:
        KCommand.ZPos = 0
        self.optimize()
        Data.late_set_up(self.canvas_size)

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

G1 F{200 * Data.PrintingSpeedFactor}

; code
"""
        max_pos = -np.array([np.inf, np.inf])
        min_pos = np.array([np.inf, np.inf])
        code = ""
        for command in self.commands:
            code += str(command)
            max_pos = np.where(command.end_position > max_pos, command.end_position, max_pos)
            min_pos = np.where(command.end_position < min_pos, command.end_position, min_pos)

        shift = np.array([Data.ShiftX, Data.ShiftY])
        comments += f"""; max position: {(max_pos - shift) * Data.MMPerPoint}
; min position: {(min_pos - shift) * Data.MMPerPoint}'
; max z pos {KCommand.ZPos}
"""
        return comments + meta_data + code

    def __add__(self, other):
        assert type(other) in [KCommandManager, KCommand, type(None)], f"can't add type ({type(other)}) with KCommandManager"

        KCM: KCommandManager = copy(self)
        if type(other) is KCommandManager:
            KCM.commands += other.commands
        elif type(other) is KCommand and np.any(other.end_position != other.start_position):
            KCM.commands.append(other)
        return KCM

    def __reversed__(self):
        r_commends: list[KCommand] = list(reversed(self.commands))
        return KCommandManager(self.label, r_commends, self.canvas_size)

    def __copy__(self):
        return KCommandManager(self.label, self.commands.copy(), self.canvas_size.copy())

    def optimize(self):
        self.removed_commands = self.overall_commands = self.times_head_up = self.average_length = 0

        commands: list[KCommand] = self.commands.copy()

        n = 0
        while n + 1 < len(commands):
            next_sp, last_sp = 0, 0
            if n - 1 >= 0:
                last_sp = commands[n - 1].is_printing
            if n + 1 <= len(commands):
                next_sp = commands[n + 1].is_printing

            # remove two head-up commands in a row
            if n - 1 >= 0 and last_sp == commands[n].is_printing == 0:
                commands[n - 1] = KCommand(commands[n - 1].start_position, commands[n].end_position, False)
                self.removed_commands += 1
                commands.pop(n)
                continue

            # compute the delta positions
            current_dPos = commands[n].end_position - commands[n].start_position  # noqa
            next_dPos = commands[n + 1].end_position - commands[n + 1].start_position  # noqa

            match_sp = commands[n].is_printing == next_sp

            current_dPos_norm = np.linalg.norm(current_dPos)  # noqa
            next_dPos_norm = np.linalg.norm(next_dPos)  # noqa

            any_dPos_zero = current_dPos_norm * next_dPos_norm == 0 # noqa
            same_dir = np.dot(next_dPos, current_dPos) > current_dPos_norm * next_dPos_norm * 0.9

            # minimizing KCode lines (straighten the k_code lines)
            if match_sp and (any_dPos_zero or same_dir):
                commands[n] = KCommand(commands[n].start_position, commands[n + 1].end_position, commands[n].is_printing) # noqa
                self.removed_commands += 1
                commands.pop(n + 1)
                continue
            if not commands[n].is_printing:
                self.times_head_up += 1
            n += 1

        self.commands = commands
        self.overall_commands = len(commands)

        _sum = 0
        _min = commands[0].length
        for command in commands:
            if command.is_printing:
                _sum += command.length
                if command.length < _min:
                    _min = command.length
        self.average_length = _sum / len(commands)

    def write_file(self, file_name, save_outline=True):

        full_path = os.path.expanduser(file_name)

        name = full_path.split('/')[-1].replace(" ", "-")
        path = '/'.join(full_path.split('/')[:-1])

        if os.path.exists(full_path):
            name = self.label.replace(" ", "-")
            path = full_path

        print(f"Saving file in: `{path}`, as: `{name}.gcode`")
        with open(f"{path}/{name}.gcode", "w") as file:
            file.write(str(self))
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

G1 F{400 * Data.PrintingSpeedFactor}

; code

G0 X{(0 - Data.ShiftX) * Data.MMPerPoint} Y{(0 - Data.ShiftY) * Data.MMPerPoint}
G1 X{(self.canvas_size[1] - Data.ShiftX) * Data.MMPerPoint} Y{(0 - Data.ShiftY) * Data.MMPerPoint}
G1 X{(self.canvas_size[1] - Data.ShiftX) * Data.MMPerPoint} Y{(self.canvas_size[0] - Data.ShiftX) * Data.MMPerPoint}
G1 X{(0 - Data.ShiftX) * Data.MMPerPoint} Y{(self.canvas_size[0] - Data.ShiftX) * Data.MMPerPoint}
G1 X{(0 - Data.ShiftX) * Data.MMPerPoint} Y{(0 - Data.ShiftY) * Data.MMPerPoint}
G0 X0 Y0
"""

        if save_outline:
            print(f"Saving file in: `{path}`, as: `{name}-Outline.gcode`")
            with open(f"{path}/{name}-Outline.gcode", "w") as file:
                file.write(gtest)
                file.close()
                print("Done Saving")

    def k_show(self, color="b", head_up_color="r", size=".", linewidth="1.5"):
        plt.figure()
        for line in self.commands:
            if line.is_printing:
                plt.plot([line.start_position[1], line.end_position[1]], [line.start_position[0], line.end_position[0]],
                                                            color + size, linestyle="-", linewidth=linewidth)
            else:
                plt.plot([line.start_position[1], line.end_position[1]], [line.start_position[0], line.end_position[0]],
                                                            head_up_color + size, linestyle="-")

        plt.table(cellText=[[f"Head up: {self.times_head_up}", f"Removed Commands: {self.removed_commands}",
                         f"Overall commands: {self.overall_commands}"]], cellLoc="left", loc="top", edges="open")
        plt.gca().invert_yaxis()
        plt.xlabel(self.label)

    @staticmethod
    def Empty(size: np.ndarray, name: str = "Empty"): return KCommandManager(name, [], size)  # noqa


def generate_tests() -> tuple[KCommandManager, KCommandManager]:
    pix = Data.LineThickness
    test_hsr: KCommandManager = KCommandManager(f"Test HSR {Data.HeadSpeedRatio}", [
        KCommand(np.zeros(2), np.ones(2) * 7 * pix, True),
        KCommand(np.ones(2) * 7 * pix, np.array([0, 1]) * 7 * pix, True),
        KCommand(np.array([0, 1]) * 7 * pix, np.array([1, 0]) * 7 * pix, False),
        KCommand(np.array([1, 0]) * 3.5 * pix, np.zeros(2), False),
    ], np.ones(2) * 20 * pix)

    test_lt: KCommandManager = KCommandManager(f"Test LT {Data.LineThickness}", [
        KCommand(np.zeros(2), np.array([1, 0]) * pix, True),
        KCommand(np.array([1, 0]) * pix, np.array([1, 1]) * pix, True),
        KCommand(np.array([1, 1]) * pix, np.array([-1, 1]) * pix, True),
        KCommand(np.array([-1, 1]) * pix, np.array([-1, -1]) * pix, True),
        KCommand(np.array([-1, -1]) * pix, np.array([2, -1]) * pix, True),
        KCommand(np.array([2, -1]) * pix, np.array([2, 2]) * pix, True),
        KCommand(np.array([2, 2]) * pix, np.array([-2, 2]) * pix, True),
        KCommand(np.array([-2, 2]) * pix, np.array([-2, -2]) * pix, True),
        KCommand(np.array([-2, -2]) * pix, np.array([3, -2]) * pix, True),
        KCommand(np.array([3, -2]) * pix, np.array([3, 3]) * pix, True),
        KCommand(np.array([3, 3]) * pix, np.array([-3, 3]) * pix, True),
        ], np.ones(2) * 10 * pix)

    return test_hsr, test_lt
