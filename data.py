from matplotlib.pyplot import *


class Data:
    HeadWidth = 1
    HeadMovingSpeed = 1  # cm/s
    PointsRes = .3  # cm
    DrawingSize = np.array([25, 30])  # cm
    AllDrawingSizes = [(25, 30)]

    @staticmethod
    def set_up(size: np.array):
        Data.HeadWidth = max(np.int_(size / (Data.DrawingSize / Data.PointsRes))) + 1
        if Data.HeadWidth <= 0:
            Data.HeadWidth = 1


class KcodeManager:
    def __init__(self, label: str, commands_protocols: list):
        self.label = label
        self.commands_protocols = commands_protocols
        self.times_head_up = 0
        self.removed_points = 0
        self.overall_commands = 0
        self.k_code = []

    def to_k_code(self):
        self.k_code = []
        commands_protocols = self.commands_protocols.copy()
        n1 = 0
        self.overall_commands = len(self.commands_protocols)
        for n, command_protocol in enumerate(self.commands_protocols):
            if len(self.commands_protocols) - 1 > n > 0 >= command_protocol.length:
                self.removed_points += 1
                commands_protocols.pop(n1)

                continue
            self.k_code += command_protocol.to_k_code()
            self.times_head_up -= command_protocol.should_print - 1
            n1 += 1

        self.commands_protocols = commands_protocols
        return self.k_code

    def Kshow(self, color="b", size="."):
        figure()
        for line in self.commands_protocols:
            if line.should_print:
                plot([line.start_position[1], line.end_position[1]], [line.start_position[0], line.end_position[0]], color + size, linestyle="-")
        table(cellText=[[f"Head up: {self.times_head_up}", f"Removed Points: {self.removed_points}", f"Overall cammands: {self.overall_commands}"]], cellLoc="left", loc="top", edges="open")
        gca().invert_yaxis()
        xlabel(self.label)


class CommandProtocol:
    def __init__(self, start_position: np.array, end_position: np.array, should_print: bool):
        self.start_position = start_position
        self.end_position = end_position
        self.should_print = should_print
        self.length = np.linalg.norm(self.end_position - self.start_position) * Data.PointsRes
        self.time = self.length / Data.HeadMovingSpeed

    def to_k_code(self):
        self.length = np.linalg.norm(self.end_position - self.start_position) * Data.PointsRes
        self.time = self.length / Data.HeadMovingSpeed

        return f"{self.end_position[1] * Data.PointsRes} {self.end_position[0] * Data.PointsRes} " \
               f"{self.should_print.as_integer_ratio()[0]} {self.time}"

    def str(self):
        return f"{self.end_position[1]} {self.end_position[0]} {self.should_print.as_integer_ratio()[0]}"




