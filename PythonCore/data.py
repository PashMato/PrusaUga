from matplotlib.pyplot import *


class Data:
    KernelSize = 1
    HeadMovingSpeed = 2  # cm/s
    PointsRes = .25  # cm
    DrawingSize = np.array([25, 30])  # cm
    AllDrawingSizes = [(25, 30)]
    SteppesPerCm = 50
    HeadSpeedRatio = 20

    @staticmethod
    def set_up(size: np.array):
        Data.KernelSize = max(np.int_(size / (Data.DrawingSize / Data.PointsRes))) + 1
        if Data.KernelSize <= 0:
            Data.KernelSize = 1


class KcodeManager: # noqa
    def __init__(self, label: str, commands_protocols: list):
        self.label = label
        self.commands_protocols: list = commands_protocols
        self.times_head_up = 0
        self.removed_points = 0
        self.overall_commands = 0
        self.k_code: np.array = np.array([], dtype=np.float32)

    def to_k_code(self):
        self.k_code = np.array([], dtype=np.float32)
        commands_protocols = self.commands_protocols.copy()
        n1 = 0
        self.overall_commands = len(self.commands_protocols)
        for n, command_protocol in enumerate(self.commands_protocols):
            if len(self.commands_protocols) - 1 > n > 0 >= command_protocol.length:
                self.removed_points += 1
                commands_protocols.pop(n1)

                continue
            np.concatenate((self.k_code, command_protocol.to_k_code()))
            self.times_head_up -= command_protocol.should_print - 1
            n1 += 1

        self.commands_protocols = commands_protocols
        return self.k_code

    def write_file(self, file_name):
        if len(self.k_code) > 2:
            self.k_code.tofile(file_name + ".kcode") # noqa
        else:
            self.to_k_code().tofile(file_name + ".kcode") # noqa

    def write(self):
        commands_protocols = self.commands_protocols
        lengths = f"const unsigned int LEN = {len(commands_protocols)};\n\n"
        all_xs = "short X[LEN] = {"
        all_ys = "short Y[LEN] = {"
        all_ts = "unsigned int T[LEN] = {"

        for command_protocal in commands_protocols:
            cp_k_code = command_protocal.to_k_code()
            all_xs += str(cp_k_code[0]) + ", "
            all_ys += str(cp_k_code[1]) + ", "
            all_ts += str(cp_k_code[3]) + ", "

        all_xs = all_xs[:-2] + "};\n"
        all_ys = all_ys[:-2] + "};\n"
        all_ts = all_ts[:-2] + "};\n"
        file = open("CppCore/data.h", 'w')
        file.write(lengths + all_xs + all_ys + all_ts)
        file.close()

    def k_show(self, color="b", size="."):
        figure()
        for line in self.commands_protocols:
            if line.should_print:
                plot([line.start_position[1], line.end_position[1]], [line.start_position[0], line.end_position[0]], color + size, linestyle="-")
        table(cellText=[[f"Head up: {self.times_head_up}", f"Removed Points: {self.removed_points}",
                         f"Overall commands: {self.overall_commands}"]], cellLoc="left", loc="top", edges="open")
        gca().invert_yaxis()
        xlabel(self.label)


class CommandProtocol:
    def __init__(self, start_position: np.array, end_position: np.array, should_print: bool):
        self.start_position = start_position
        self.end_position = end_position
        self.should_print = should_print
        self.length = np.linalg.norm(self.end_position - self.start_position) * Data.PointsRes
        self.time = self.length / Data.HeadMovingSpeed * 1000 # else it would be in seconds

    def to_k_code(self):
        self.length = np.linalg.norm(self.end_position - self.start_position) * Data.PointsRes
        self.time = self.length / Data.HeadMovingSpeed * 1000 # else it would be in seconds

        return np.array([self.end_position[1] * Data.PointsRes * Data.SteppesPerCm,
                         self.end_position[0] * Data.PointsRes * Data.SteppesPerCm,
                         self.should_print.as_integer_ratio()[0] * Data.HeadSpeedRatio, self.time], dtype=np.int)

    def str(self):
        return f"{self.end_position[1]} {self.end_position[0]} {self.should_print.as_integer_ratio()[0]}"




