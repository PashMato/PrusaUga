#!usr/bin/env python3
import sys

sys.path.append("/home/pash/PycharmProjects/PrushaUga")


import numpy as np
import matplotlib.pyplot as plt

import scipy.ndimage as snd

import cv2

import argparse
from colorama import Fore

from PythonCore.base_converter import BaseConverter

from PythonCore.data import Data
from PythonCore.k_command_manger import KCommandManager
from PythonCore.k_command import KCommand


class ImageToLines(BaseConverter):
    MinCost = None

    def __init__(self, path: str, is_test: bool = False):
        super(ImageToLines, self).__init__(path)
        self.is_test = is_test

        self.image: np.ndarray = plt.imread(self.path)
        self.output_matrix: np.ndarray = np.zeros(self.image.shape[:2])
        self._image_to_matrix()

        self.edge: np.ndarray = np.ones((1, 1))
        self.last_edge: np.ndarray = np.ones((1, 1))

    def _image_to_matrix(self):
        # crop the unnecessary lines
        occupancy = self.image[:, :, 3] != 0
        size0 = list(np.argwhere(occupancy.any(axis=0))[[0, -1]])
        size1 = list(np.argwhere(occupancy.any(axis=1))[[0, -1]])
        crop_occupancy = occupancy[size1[0][0]:size1[1][0] + 1, size0[0][0]:size0[1][0] + 1]

        # convert to a smaller matrix with a Kernel
        Data.set_up(crop_occupancy.shape)

        # takes every X (Data.KernelSize) lines and sum them up
        shape = (crop_occupancy[0::Data.KernelSize].shape[0] + 1, crop_occupancy[0::Data.KernelSize].shape[1])
        out_0 = np.zeros(shape)
        for i in range(Data.KernelSize):
            mat = crop_occupancy[i::Data.KernelSize]
            out_0[:mat.shape[0], :mat.shape[1]] += mat

        # takes every X (Data.KernelSize) rows and sum them up
        shape = (out_0[:, 0::Data.KernelSize].shape[0], out_0[:, 0::Data.KernelSize].shape[1] + 1)
        out_1 = np.zeros(shape)
        for i in range(Data.KernelSize):
            mat = out_0[:, i::Data.KernelSize]
            out_1[:mat.shape[0], :mat.shape[1]] += mat

        # crop the extra
        size0 = list(np.argwhere(out_1.any(axis=0))[[0, -1]])
        size1 = list(np.argwhere(out_1.any(axis=1))[[0, -1]])
        self.output_matrix: np.ndarray = np.float_(
            out_1[size1[0][0]:size1[1][0] + 1, size0[0][0]:size0[1][0] + 1] != False)

        self.edge = np.ones(self.output_matrix.shape)
        self.last_edge = np.ones(self.output_matrix.shape)
        if self.is_test:
            self.output_matrix = np.zeros(self.output_matrix.shape)
            self.output_matrix[0, :] = 1
            self.output_matrix[:, 0] = 1
            self.output_matrix[-1, :] = 1
            self.output_matrix[:, -1] = 1
            self.name = f"Test-Size-{str(self.output_matrix.shape).replace(' ', '-')}"

    def get_k_code(self, mode: str = "default") -> KCommandManager:
        def depth_matrix() -> np.ndarray:
            # compute the depth map for image
            matrix: np.ndarray = self.output_matrix.copy()

            d_mat = np.zeros(self.output_matrix.shape)
            d = 1

            weight = np.array([
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0]])

            while np.any(matrix):
                _edge = matrix * (snd.convolve(matrix, weight, mode='constant', cval=0) < 4)
                matrix -= _edge

                d_mat += d * _edge
                d += 1
            return d_mat

        self.KCode_manager = KCommandManager(f"{self.name} Circles", [], np.array(self.output_matrix.shape))
        # depth_mat = np.zeros(self.output_matrix.shape)
        depth_mat = depth_matrix()

        # for over the layer
        last_end_pos: np.ndarray = np.array(self.output_matrix.shape) // 2

        i_depth = 0

        while np.any(depth_mat):
            # pen-up required
            if i_depth == 0 or not np.any(depth_mat == i_depth):
                i_depth = np.max(depth_mat)
                end_pos = ImageToLines.get_nearest(depth_mat, last_end_pos, value=i_depth)

                if np.any(end_pos == None):
                    depth_mat[last_end_pos[0], last_end_pos[1]] = 0
                    if not depth_mat.any():
                        # if end_pos is None it means that only depth_mat[c_pos] is True
                        break
                    i_depth = 0
                    continue
                self.KCode_manager += KCommand(last_end_pos, end_pos, False)
                last_end_pos = end_pos
            else:
                last_end_pos = self.KCode_manager.commands[-1].end_position

            components = np.array(cv2.connectedComponents((depth_mat == i_depth).astype(np.int8))[1])  # noqa
            closest_edge_piece = ImageToLines.get_nearest(depth_mat == i_depth, last_end_pos)
            if closest_edge_piece is None:
                # if there isn't any edge peace continue
                i_depth -= 1
                continue

            edge = components == components[closest_edge_piece[0], closest_edge_piece[1]]
            depth_mat *= ~edge

            self.KCode_manager += ImageToLines.close_loop(edge, start_pos=last_end_pos)
            i_depth -= 1

        print(f"Done Slicing {self.name}")
        self.KCode_manager.optimize()
        print(f"Optimizing {self.name}")
        return self.KCode_manager

    @staticmethod
    def close_loop(matrix, start_pos: np.ndarray = None, end_pos: np.ndarray = None) -> KCommandManager:
        if not np.any(matrix):
            # the matrix is empty there is mathing to slice
            return KCommandManager("Empty", [], np.array(matrix.shape))

        assert not (np.any(start_pos != None) and np.any(
            end_pos != None)), "close loop doesn't support dynamic end, start pos at once"  # noqa

        is_reversed = False

        if not np.any(start_pos != end_pos) and not np.any(start_pos != None):  # noqa
            # there aren't any requirements for the start or end position
            start_pos = ImageToLines.get_nearest(matrix, np.zeros(2))
        elif start_pos is None and end_pos is not None:
            # only the end pos is given
            start_pos = end_pos.copy().astype(int)
            is_reversed = True
        start_pos = start_pos.astype(int)

        KM: KCommandManager = KCommandManager("KCommandManager", [], np.array(matrix.shape))

        for cntr in range(np.sum(matrix != 0)):
            command: KCommand = ImageToLines.simple_slice(matrix, start_pos)
            KM += command

            start_pos = KM.commands[-1].end_position.astype(int)

        if is_reversed:
            KM: KCommandManager = KM.__reversed__()
        return KM

    @staticmethod
    def simple_slice(matrix: np.ndarray, start_pos: np.ndarray):
        matrix[start_pos[0], start_pos[1]] = 0
        mat, offset = ImageToLines.get_mat(matrix, start_pos - 1, start_pos + 1)
        nr_end_pos = ImageToLines.get_nearest(mat, np.ones(2) - offset)

        if nr_end_pos is not None:
            end_pos = start_pos + nr_end_pos + offset - 1
            return KCommand(start_pos, end_pos, True)
        elif matrix.any():
            end_pos = ImageToLines.get_nearest(matrix, start_pos)
            return KCommand(start_pos, end_pos, False)
        else:
            return None

    @staticmethod
    def n_friends(matrix: np.ndarray, kernel: np.ndarray = None) -> np.ndarray:
        if kernel is None:
            kernel = np.ones((3, 3))
        return snd.convolve(matrix.astype(float), kernel, mode='constant', cval=0).astype(int) * \
            matrix.astype(bool) - matrix

    @staticmethod
    def get_nearest(mat: np.ndarray, position: np.array, weight: np.ndarray = None, value: int = 1) -> np.ndarray:  # noqa
        """
        return the closest one in a matrix

        :param mat: the input matrix
        :param position: the current position
        :param weight: the weight subtract from the distance matrix
        :return:
        ndarray: the position of the closest one relative to the input matrix.
        None: there aren't any `values` in matrix (maybe the matrix is empty)
        """
        assert weight is None or weight.shape == matrix.shape, f"weight matrix shape {weight.shape} and input matrix shape {matrix.shape} must each ather shape"  # noqa

        if 0 in mat.shape:
            # the matrix is empty
            return None

        y, x = position.astype(int)

        # if it wasn't zero the closest one will be at (x, y)
        matrix = mat.copy() == value
        matrix[y, x] = False

        # the distance from certain point (in one axis)
        x_dis = np.repeat((np.arange(len(matrix[0])) - x)[np.newaxis, :], len(matrix), axis=0)
        y_dis = np.repeat(((np.arange(len(matrix))) - y)[:, np.newaxis], len(matrix[0]), axis=1)
        dis_mat = np.where(matrix, np.sqrt(y_dis ** 2 + x_dis ** 2), np.inf)

        if weight is not None:
            dis_mat -= weight

        if dis_mat.min() == np.inf:
            # there isn't any of `value` in mat
            return None
        else:
            return np.argwhere(dis_mat == np.min(dis_mat))[0]

    @staticmethod
    def get_mat(matrix, start_position: np.ndarray, end_position: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the matrix from a start position to end position
        :param matrix: input matrix
        :param start_position: start reading position
        :param end_position: end reading position
        :returns: the matrix from start position to end position,
        the offset because of the cropping
        """
        assert not np.any(start_position >= np.array(matrix.shape)), "Tried to Crop `nothing` out of matrix"
        assert not np.any(end_position < np.zeros(2)), "Tried to Crop `nothing` out of matrix"

        start_pos = start_position.copy()
        end_pos = end_position.copy()
        end_pos += 1

        start_pos = np.clip(start_pos, 0, np.array(matrix.shape))
        end_pos = np.clip(end_pos, start_pos, np.array(matrix.shape))

        return matrix[start_pos[0]:end_pos[0], start_pos[1]:end_pos[1]], np.abs(start_position - start_pos)


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--input', type=str, help="Input the file path")
    parser.add_argument("-w", '--write_to', type=str, help="Write gcode to a file path")
    parser.add_argument("-p", '--plot', type=str, help="Plots the image", default="off", choices={'on', 'off'})
    parser.add_argument("-t", '--test', type=str, help="Is the image a test", default="off", choices={'on', 'off'})

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.input is None:
        print("Run with -h or --help to get help")
        exit(1)

    im2mat: ImageToLines = ImageToLines(args.input, args.test == "on")
    gcode: KCommandManager = im2mat.get_k_code()

    if args.write_to:
        gcode.write_file(args.write_to)
    if args.plot == "on":
        plt.figure()
        plt.clf()

        plt.imshow(im2mat.output_matrix)

        plt.title(args.input.split("/")[-1].split(".")[0])

        im2mat.KCode_manager.k_show()

        plt.show(block=True)


if __name__ == '__main__':
    main()
