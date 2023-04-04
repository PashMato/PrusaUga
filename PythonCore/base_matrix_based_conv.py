import numpy as np
import matplotlib.pyplot as plt

import scipy.ndimage as snd

from PythonCore.base_converter import BaseConverter

from PythonCore.data import Data


class MatBasedConverter(BaseConverter):
    def __init__(self, path: str):
        super(MatBasedConverter, self).__init__(path)

        self.image: np.ndarray = plt.imread(self.file_name)
        self.output_matrix: np.ndarray = np.zeros(self.image.shape[:2])
        self.image_to_matrix()

    def image_to_matrix(self):
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

    @staticmethod
    def conv_mat(matrix: np.ndarray, kernel: np.ndarray = None) -> np.ndarray:
        """
        convolve a matrix
        :param matrix: the input matrix
        :param kernel: the kernel. if None then kernel=np.ones((3, 3))
        :return: the convolve matrix
        """
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

    def k_show(self):
        """
        show the image matrix and the KCode
        :return:
        """
        plt.figure()
        plt.clf()

        plt.imshow(self.output_matrix)

        plt.title(self.name)

        self.KCM.k_show()

        plt.show(block=True)

