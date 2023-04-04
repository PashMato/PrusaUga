#!usr/bin/env python3
import sys
import os
sys.path.append("/home/pash/PycharmProjects/PrushaUga")


import numpy as np
import matplotlib.pyplot as plt

import scipy
import cv2

import argparse

from PythonCore.base_converter import BaseConverter

from PythonCore.data import Data
from PythonCore.k_command_manger import KCommandManager
from PythonCore.k_command import KCommand


class ImageToLines(BaseConverter):
    ReadChanel = 3

    def __init__(self, path: str):
        super(ImageToLines, self).__init__(path)
        self.image: np.ndarray = plt.imread(self.file_name)
        self.output_matrix: np.ndarray = np.zeros(self.image.shape[:2])
        self.image_to_matrix()

    def image_to_matrix(self):
        # crop the unnecessary lines
        occupancy = self.image[:, :, ImageToLines.ReadChanel] != 0
        size0 = list(np.argwhere(occupancy.any(axis=0))[[0, -1]])
        size1 = list(np.argwhere(occupancy.any(axis=1))[[0, -1]])
        crop_occupancy = occupancy[size1[0][0]:size1[1][0] + 1, size0[0][0]:size0[1][0] + 1]

        # convert to a smaller matrix with a Kernel
        Data.set_up(crop_occupancy.size)

        # takes every X (Data.KernelSize) lines and sum them up
        shape = (crop_occupancy[0::Data.KernelSize].size[0] + 1, crop_occupancy[0::Data.KernelSize].size[1])
        out_0 = np.zeros(shape)
        for i in range(Data.KernelSize):
            mat = crop_occupancy[i::Data.KernelSize]
            out_0[:mat.size[0], :mat.size[1]] += mat

        # takes every X (Data.KernelSize) rows and sum them up
        shape = (out_0[:, 0::Data.KernelSize].size[0], out_0[:, 0::Data.KernelSize].size[1] + 1)
        out_1 = np.zeros(shape)
        for i in range(Data.KernelSize):
            mat = out_0[:, i::Data.KernelSize]
            out_1[:mat.size[0], :mat.size[1]] += mat

        # crop the extra
        size0 = list(np.argwhere(out_1.any(axis=0))[[0, -1]])
        size1 = list(np.argwhere(out_1.any(axis=1))[[0, -1]])
        self.output_matrix = np.float_(out_1[size1[0][0]:size1[1][0] + 1, size0[0][0]:size0[1][0] + 1] != False)
        return out_1[size1[0][0]:size1[1][0] + 1, size0[0][0]:size0[1][0] + 1] / 9

    def get_k_code(self, mode: str = None, start_pos: np.ndarray = None) -> KCommandManager:
        def get_raster_k_code(mat: np.ndarray, start_position: np.ndarray) -> KCommandManager:
            """
            calculte the gcode for the input matrix

            :param mat: input matrix
            :param start_position: where to start slice from
            :return:
            KCommandManager of the input matrix
            """

            # calling the first command
            mat, command, is_done = \
                ImageToLines._get_next_move(mat, start_position)

            KManager: KCommandManager = KCommandManager(f"{self.name} {mode[0].upper() + mode[1:]}",  # noqa
                                                        [command], np.array(mat.size))

            while not is_done:
                mat, command, is_done = \
                    ImageToLines._get_next_move(mat, command.end_position)

                if command is not None:
                    KManager.commands.append(command)

            return KManager

        if mode is None:
            mode = "circles"

        if start_pos is None:
            start_pos = np.array(self.output_matrix.shape, dtype=int) // 2  # the center

        weight = np.array([[0, 1, 0],
                           [1, 0, 1],
                           [0, 1, 0]])

        matrix: np.ndarray = self.output_matrix.copy()

        if mode == "raster":
            # slicing in raster mode
            edge = matrix * (scipy.ndimage.convolve(matrix, weight, mode='constant', cval=0) < 4)
            matrix -= edge
            self.KCode_manager = get_raster_k_code(edge, start_pos)
            self.KCode_manager += get_raster_k_code(matrix, self.KCode_manager.commands[-1].end_position) # noqa
        elif mode == "circles":
            # slicing in circles mode
            Kcode_manager: KCommandManager = KCommandManager(f"{self.name} Circles", [], np.array(matrix.shape)) # noqa
            position = start_pos

            # loop over the edges
            while matrix.any():
                edge = matrix * (scipy.ndimage.convolve(matrix, weight, mode='constant', cval=0) < 4)
                closest_one = ImageToLines.get_nearset(edge, position)

                # get closest component
                component = np.array(cv2.connectedComponents(edge.astype(np.int8))[1]) # noqa
                # edge_component = component == component[closest_one[0]][closest_one[1]]
                edge_component = edge

                matrix -= edge_component
                Kcode_manager += get_raster_k_code(edge_component, position)

                position = Kcode_manager.commands[-1].end_position
            self.KCode_manager = Kcode_manager
        else:
            massage = f"unknown mode `{mode}`"
            raise Exception(massage)
            self.KCM = Kcode_manager # noqa
        self.KCode_manager.optimize()
        return self.KCode_manager

    @staticmethod
    def _get_next_move(matrix: np.ndarray, position: np.array) -> type[np.ndarray, KCommand, bool]:
        """
        compute the next move in the GCode

        :param matrix: input matrix
        :param position: the current position
        :return:
            output matrix; input matrix without the current move
            KCommand; the KCommand to the new position
            IsDone; did we finish slicing?
        """

        y, x = position

        assert 0 <= x < len(matrix[0]), f"KernelError: x value cannot be `{x}`. it must be between 0 and matrix size. \nin this case `{len(matrix[0])}`)" # noqa
        assert 0 <= y < len(matrix), f"KernelError: y value cannot be `{y}`. it must be between 0 and matrix size. \nin this case `{len(matrix)}`)" # noqa

        # matrix start positions
        x0, y0 = np.array([x - 1, y - 1]).clip(0, x + y)

        # matrix end position
        x1 = np.clip(x + 2, 0, len(matrix[0]))
        y1 = np.clip(y + 2, 0, len(matrix))

        # 3 by 3 block around (x0, y0)
        temp = matrix[y0:y1, x0:x1]

        if np.any(temp == 1):
            # if exits a 1 in temp
            weight = np.array([[  0, 0,   0], # noqa
                               [0.5, 0, 0.5], # noqa
                               [  0, 0,   0]]) # noqa

            end_position = np.array([y0, x0]) + ImageToLines.get_nearset(temp, np.array([y - y0, x - x0]),
                                                                         weight=weight[y0 - y+1:y1 - y+1, x0 - x+1:x1 - x+1])
            end_position.clip(0, np.array(matrix.shape))

            matrix[end_position[0]][end_position[1]] = 0
            return matrix, KCommand(np.array([y, x]), end_position, True), False
        elif np.any(matrix == 1):
            # if there's anything else to slice
            end_position = ImageToLines.get_nearset(matrix, position)

            end_position.clip(0, np.array(matrix.shape))

            return matrix, KCommand(np.array([y, x]), end_position, False), False
        else:
            # there aren't any 1 in the image (matrix)
            return matrix, None, True

    @staticmethod
    def get_nearset(mat: np.ndarray, position: np.array, weight: np.ndarray = None, value = 1) -> np.ndarray:
        """
        return the closest one in a matrix

        :param matrix: the input matrix
        :param position: the current position
        :param weight: the weight subtract from the distance matrix
        :return:
        the position of the closest one relative to the input matrix
        """
        matrix = mat == value

        assert weight is None or weight.shape == matrix.shape, f"weight matrix shape {weight.shape} and input matrix shape {matrix.shape} must each ather shape" # noqa

        y, x = position

        # if it wasn't zero the closest one will be at (x, y)
        matrix[y][x] = 0

        # the distance from certain point (in one axis)
        x_dis = np.repeat((np.arange(len(matrix[0])) - x)[np.newaxis, :], len(matrix), axis=0)
        y_dis = np.repeat(((np.arange(len(matrix))) - y)[:, np.newaxis], len(matrix[0]), axis=1)

        dis_mat = np.where(matrix == 1, np.sqrt(y_dis ** 2 + x_dis ** 2), np.inf)

        if weight is not None:
            dis_mat -= weight
        return np.argwhere(dis_mat == np.min(dis_mat))[0]


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--input', type=str, help="Input the file path")
    parser.add_argument("-w", '--write_to', type=str, help="Write gcode to a file path")
    parser.add_argument("-p", '--plot', type=str, help="Plots the image", default="off", choices={'on', 'off'})

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.input is None:
        print("Run with -h or --help to get help")
        exit(1)

    im2mat: ImageToLines = ImageToLines(args.input)
    gcode: KCommandManager = im2mat.get_k_code(mode=args.mode)
    if args.split_color == "on":
        im2mat0: ImageToLines = ImageToLines(args.input)
        alpha_channel: np.ndarray = im2mat0.output_matrix.copy() != 0

        ImageToLines.ReadChanel = 0
        red_channel: np.ndarray = im2mat0.image_to_matrix()

        ImageToLines.ReadChanel = 1
        green_channel: np.ndarray = im2mat0.image_to_matrix()

        ImageToLines.ReadChanel = 2
        blue_channel: np.ndarrim.ay = im2mat0.image_to_matrix()

        ImageToLines.ReadChanel = 3

        comeponet_red = cv2.connectedComponents(red_channel.astype(np.int8))[1]
        comeponet_green = cv2.connectedComponents(green_channel.astype(np.int8))[1]
        comeponet_blue = cv2.connectedComponents(blue_channel.astype(np.int8))[1]

        matrix = np.zeros(comeponet_blue.size)

        i = 0
        for l_red in range(comeponet_red.max() + 1):
            for l_green in range(comeponet_green.max() + 1):
                for l_blue in range(comeponet_blue.max() + 1):
                    mat = ((comeponet_red == l_red) * (comeponet_green == l_green) * (comeponet_blue == l_blue)) * alpha_channel
                    con_mat = i + cv2.connectedComponents(mat.astype(np.int8))[1]
                    matrix += con_mat
                    i = con_mat.max()

        alpha_channel = alpha_channel.astype(int)

        end_position = np.array(alpha_channel.shape) // 2
        gcode: KCommandManager = KCommandManager(im2mat0.name, [], np.array(comeponet_red.size))
        while alpha_channel.any():
            closest_one = ImageToLines.get_nearset(alpha_channel, end_position)
            layer = (matrix == matrix[closest_one[0], closest_one[1]]).astype(int)
            alpha_channel -= layer
            im2mat0.output_matrix = layer
            im2mat0.get_k_code(mode="circles", start_pos=end_position)
            gcode += im2mat0.KCode_manager
            end_position = gcode.commands[-1].end_position

        gcode.optimize()

    if args.plot == "on":
        plt.figure()
        plt.clf()

        plt.imshow(im2mat.output_matrix)

        plt.title(args.input.split("/")[-1].split(".")[0])

        gcode.k_show()

        plt.show(block=True)
    if args.write_to:
        gcode.write_file(os.path.expanduser(args.write_to))


if __name__ == '__main__':
    main()


