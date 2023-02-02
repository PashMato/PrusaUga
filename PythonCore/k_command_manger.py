import numpy as np

from PythonCore.k_command import KCommand
from PythonCore.data import Data
from matplotlib import pyplot as plt

from datetime import date

class KCommandManager: # noqa
    def __init__(self, label: str, commands_protocols: list[KCommand], size: np.ndarray):
        self.label = label
        self.commands_protocols: list[KCommand] = commands_protocols
        self.times_head_up = 0
        self.removed_points = 0
        self.overall_commands = 0
        self.canvas_size: np.ndarray = size

    def __str__(self) -> str:
        KCommand.ZPos = 0
        self.optimize()
        Data.late_set_up(self.canvas_size)

        gcode = f"""; gcode generated at ({date.today()}) with PrusaUgaSlicer
; gcode for {self.label}

; relative moving
; the start point of the head is the center of the drawing

"""

        for command in self.commands_protocols:
            gcode += str(command)
        return gcode

    def optimize(self):
        self.removed_points = self.overall_commands = self.times_head_up = 0

        commands_protocols: list[KCommand] = self.commands_protocols.copy()

        n = 0
        while n + 1 < len(commands_protocols):
            # detecting if it is a single point and if so removing it
            next_sp, last_sp = 0, 0
            if n - 1 >= 0:
                last_sp = commands_protocols[n - 1].should_print
            if n + 1 <= len(commands_protocols):
                next_sp = commands_protocols[n + 1].should_print

            is_single = not np.any(commands_protocols[n].start_position != commands_protocols[n].end_position)
            if is_single:
                self.removed_points += 1
                commands_protocols.pop(n)
                continue

            # remove two head-up commands in a row
            if n - 1 >= 0 and last_sp == commands_protocols[n].should_print == 0:
                commands_protocols[n - 1] = \
                    KCommand(commands_protocols[n - 1].start_position, commands_protocols[n].end_position, False)
                commands_protocols.pop(n)
                continue

            # compute the delta positions
            current_dPos = commands_protocols[n].end_position - commands_protocols[n].start_position
            if n + 1 < len(commands_protocols):
                next_dPos = commands_protocols[n + 1].end_position - commands_protocols[n + 1].start_position
            else:
                break

            # minimizing KCode lines (straighten the k_code lines)
            if commands_protocols[n].should_print == next_sp and \
                    (np.linalg.norm(current_dPos) * np.linalg.norm(next_dPos)) == 0 or \
                    np.abs(np.dot(next_dPos, current_dPos) / (np.linalg.norm(current_dPos) * np.linalg.norm(next_dPos))) == 1:

                commands_protocols[n] = KCommand(commands_protocols[n].start_position,
                                                 commands_protocols[n + 1].end_position, commands_protocols[n].should_print)
                if n + 1 < len(commands_protocols):
                    commands_protocols.pop(n + 1)
                continue
            if not commands_protocols[n].should_print:
                self.times_head_up += 1
            n += 1

        self.commands_protocols = commands_protocols
        self.overall_commands = len(commands_protocols)

    def write_file(self, file_name):
        with open(f"{file_name}.gcode", "w") as file:
            file.write(str(self))
            file.close()

    def k_show(self, color="b", size="."):
        plt.figure()
        for line in self.commands_protocols:
            if line.should_print:
                plt.plot([line.start_position[1], line.end_position[1]], [line.start_position[0], line.end_position[0]],
                                                            color + size, linestyle="-")

        plt.table(cellText=[[f"Head up: {self.times_head_up}", f"Removed Points: {self.removed_points}",
                         f"Overall commands: {self.overall_commands}"]], cellLoc="left", loc="top", edges="open")
        plt.gca().invert_yaxis()
        plt.xlabel(self.label)