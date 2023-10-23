import os

import matplotlib.pyplot as plt
import numpy as np

from log.log import message
from settings.data import Data

from gcode.gcode_base_comands import create_metadata, create_comments, create_g_test, create_end_data


class GCodeManager:
    def __init__(self, name: str, commends: list[np.ndarray], size: np.ndarray):
        """
        :param name: name
        :param commends: commands list[np.array([<X>, <Y>, <is_printing>])}
        :param size: size
        """
        self.name = name
        self.commands = commends.copy()
        self.size = size
        self.gcode = "; Empty"

        self.commands_num = len(self.commands)
        self.removed_commands = 0
        self.head_ups_num = 0

        self.ap_time = 0

    def optimize(self) -> None:
        """
        optimize the gcode; remove double pen-ups and strait commands
        """
        arr = np.array(self.commands)

        derivative_is_printing = np.ediff1d(arr[:, 2], to_end=0)  # the derivative to the nex element

        # create a cleaner arr
        #          <make sure that there isn't a double pen-up command>  <make sure that the second commend is printing>
        new_arr: np.ndarray = arr[np.where((derivative_is_printing != 0) |
                                           ((derivative_is_printing == 0) & (arr[:, 2] != 0)))]

        self.removed_commands += self.commands_num - new_arr.shape[0]
        self.commands = list(new_arr)
        self.commands_num = len(self.commands)
        self.head_ups_num = sum(~(new_arr[:, 2]).astype(bool))

        norm_xy = get_norms(np.r_[np.zeros(3)[np.newaxis, :], new_arr]) * new_arr[:, 2][:, np.newaxis]
        self.ap_time = np.sum(norm_xy / Data.StaticSpeed)

    def get_g_code(self) -> str:
        """
        generate gcode
        :return: the gcode
        """
        # update the mode
        Data.update_mode(self.size)

        self.optimize()
        arr = np.array(self.commands)
        dot_product = get_dot_product(np.r_[np.zeros((1, 3)), arr, np.zeros((1, 3))])

        # the command type (G0 or G1)
        command_type = np.char.add("G", arr[:, 2].astype(int).astype(str))

        # the speed
        all_f = (arr[:, 2] * Data.StaticSpeed).astype(int).astype(str)
        all_f_str = np.char.add(" ", np.char.add("F", all_f))
        all_f_str[arr[:, 2] == 0] = ""

        # all X positions
        all_x = arr[:, 0] * Data.MMPerPoint + Data.ShiftX
        all_x_str = np.char.add(" X", all_x.astype(str))
        all_x_str[np.where(np.ediff1d(arr[:, 0], to_begin=1) == 0)] = ""

        # all Y positions
        all_y = arr[:, 1] * Data.MMPerPoint + Data.ShiftY
        all_y_str = np.char.add(" Y", all_y.astype(str))
        all_y_str[np.where(np.ediff1d(arr[:, 1], to_begin=1) == 0)] = ""

        # pre-calculations to all Z
        norm_xy = get_norms(np.r_[np.zeros(3)[np.newaxis, :], arr])

        derivative_is_printing = np.ediff1d(arr[:, 2], to_end=0)  # the derivative to the next element

        # the pen down fore delta (relative)
        all_fore_delta = (derivative_is_printing == 1) * Data.PenUpFore * Data.HeadSpeedRatio

        # all Z positions
        all_z = (np.cumsum(norm_xy * arr[:, 2][:, np.newaxis]) * Data.HeadSpeedRatio +
                 np.cumsum(all_fore_delta) - all_fore_delta + 3)

        all_z_str = np.char.add(np.char.add(" Z", all_z.astype(str)), "\n")
        all_z_str[np.where(arr[:, 2] == 0)] = "\n"

        # connect all the information so far
        all_line_codes = np.c_[command_type, all_f_str, all_x_str, all_y_str, all_z_str]

        # calculating the waiting time
        up_waiting_time: np.ndarray = (-Data.WaitingTime * (dot_product - 1) * arr[:, 2] + Data.PenUpFore *
                                       (derivative_is_printing == -1))
        up_waiting_time[up_waiting_time < 0.5] = 0

        # get all the positions (non-relative)
        all_up_wait_pos = all_z - up_waiting_time * Data.WaitingSpeed / 60

        # convert to string
        all_up_wait_pos_str = np.char.add(np.char.add(f"G1 F{Data.WaitingSpeed} Z", all_up_wait_pos.astype(str)), "\n")
        all_down_wait_pos_str = np.char.add(np.char.add(f"G1 F{Data.WaitingSpeed} Z", all_z.astype(str)), '\n')

        # making sure we aren't waiting a tiny bit
        all_up_wait_pos_str[up_waiting_time <= 0.1] = all_down_wait_pos_str[up_waiting_time <= 0.1] = ""

        # if we are in pen down/up we shouldn't go back up (pen-up should be with the head up and pen down has a fore)
        all_down_wait_pos_str[derivative_is_printing != 0] = ""
        all_down_wait_pos_str[-1] = ""

        all_fore = all_z + all_fore_delta  # non-relative
        all_fore_str = np.char.add(np.char.add(f"G1 F{Data.StaticSpeed} Z", all_fore.astype(str)), "\n\n")
        all_fore_str[derivative_is_printing != 1] = ""  # if we aren't pen downing it should be non
        all_fore_str[-1] = ""

        # connect all the information
        all_code = np.c_[all_line_codes, all_up_wait_pos_str, all_down_wait_pos_str, all_fore_str]
        code = "".join(all_code.flat)

        # base calculation of the gcode (almost) constant data
        comments = create_comments(self.name)
        meta_data = create_metadata(self.ap_time, self.size)
        end_data = create_end_data()

        self.gcode = comments + meta_data + code + end_data
        return self.gcode

    def write_file(self, file_name: str, save_outline: bool = True):
        full_path = os.path.expanduser(file_name)

        name = full_path.split('/')[-1].replace(" ", "-").split('.')[0]
        path = '/'.join(full_path.split('/')[:-1])

        if os.path.exists(full_path):
            name = self.name.replace(" ", "-")
            path = full_path

        message(f"Saving file in: `{path}`, as: `{name}-{Data.SettingVersion}-Mode-{Data.Mode}.gcode`",
                message_type="Info")  # noqa
        with open(f"{path}/{name}-{Data.SettingVersion}-Mode-{Data.Mode}.gcode", "w") as file:
            file.write(self.get_g_code())
            file.close()
            message("Done Saving", message_type="Info")

        gtest = create_g_test(self.name, self.size)

        if save_outline:
            message(f"Saving file in: `{path}`, as: `{name}-{Data.SettingVersion}-Mode-{Data.Mode}-Outline.gcode`",
                    message_type="Info")  # noqa
            with open(f"{path}/{name}-{Data.SettingVersion}-Mode-{Data.Mode}-Outline.gcode", "w") as file:
                file.write(gtest)
                file.close()
                message("Done Saving", message_type="Info")

    def g_show(self, color="b", head_up_color="r", size=".", linewidth="1.5") -> None:
        self.optimize()

        plt.figure()
        message("Plotting kcode", message_type="Info")

        arr = np.array(self.commands)

        pen_up_i = np.where(arr[:, 2] == 0)

        # pen ups indexes
        pen_up_start_i = np.array(pen_up_i) - 1  # may contain values like -1 so override variable
        pen_up_start_i = pen_up_start_i[pen_up_start_i >= 0]  # contain only positive values

        pen_up_i = pen_up_start_i + 1

        # the complicity of the line is because pen_up_i format is a tuple that contains a list
        pen_up_start = arr[tuple([list(pen_up_start_i)])][np.newaxis, :, :2]
        pen_up_end = arr[pen_up_i][np.newaxis, :, :2]

        # create the nan layer
        nan_layer = np.zeros(pen_up_start.shape[1:3])[np.newaxis, :, :]
        nan_layer[0, :, :] = np.NAN

        # connect all the layers
        concat_pen_up = np.concatenate([pen_up_start, pen_up_end, nan_layer], axis=0).T

        # simply the all x and all y to two referent variables
        not_raveled_all_x, not_raveled_all_y = list(concat_pen_up)

        # raveling the all x and all y from (, 3) to (,)
        all_penup_x = not_raveled_all_x.ravel()
        all_penup_y = not_raveled_all_y.ravel()

        # non pen ups

        arr[pen_up_i] = np.NAN
        all_x, all_y = list(arr[:, :2].T)

        plt.plot(all_x, all_y, color + size, linestyle="-", linewidth=linewidth)  # plot the non-pen-ups

        plt.plot(all_penup_x, all_penup_y, head_up_color + size, linestyle="-.")  # plot the pen-ups

        # plot the start and end points
        plt.plot(arr[0, 0], arr[0, 1], "m+", linewidth=10)
        plt.plot(arr[-1, 0], arr[-1, 1], "m*", linewidth=10)

        # set up the figure configuration
        plt.table(cellText=[
            [f"Head up: {self.head_ups_num}",
            f"Overall commands: {self.commands_num}",
            f"Estimated printing time: {int(self.ap_time + 1)}"]], cellLoc="left", loc="top", edges="open")

        plt.axis("equal")
        plt.xlabel(self.name)


def get_normalized(arr: np.ndarray) -> np.ndarray:
    """
    compute the normalized gcode (diff)
    :param arr: input gcode (np.ndarray)
    :return: an array of normalized vector (shorter in one than arr from the start)
    """
    vectors = arr[:, :2][1:] - arr[:, :2][:-1]
    norm_xy = np.linalg.norm(vectors, axis=1)[:, np.newaxis]

    norm_xy[np.where(norm_xy == 0)] += 0.0000001

    return vectors / norm_xy


def get_norms(arr: np.ndarray) -> np.ndarray:
    """
    compute the norm of gcode (diff)
    :param arr: input gcode (np.ndarray)
    :return: an array of norms of the vectors (shorter in one than arr from the start)
    """
    vectors = arr[:, :2][1:] - arr[:, :2][:-1]
    return np.linalg.norm(vectors, axis=1)[:, np.newaxis]


def get_dot_product(arr: np.ndarray) -> np.ndarray:
    """
    compute the dot product for a given gcode
    :param arr: input gcode (np.ndarray)
    :return: an array of dot products (shorter in two than arr)
    """
    normalized_xy = get_normalized(arr)
    return np.sum(normalized_xy[1:] * normalized_xy[:-1], axis=1)
