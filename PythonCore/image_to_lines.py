import numpy as np
from PythonCore.base_converter import BaseConverter

from matplotlib import pyplot as plt

from PythonCore.data import Data
from PythonCore.k_command_manger import KCommandManager
from PythonCore.k_command import KCommand


class ImageToLines(BaseConverter):
    def __init__(self, path: str):
        super(ImageToLines, self).__init__(path)
        self.image: np.ndarray = plt.imread(self.path)
        self.output_matrix: np.ndarray = np.zeros(self.image.shape[:2])
        self._image_to_matrix()

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
            out_0[:mat.shape[0], :mat.shape[1]] = mat

        # takes every X (Data.KernelSize) rows and sum them up
        shape = (out_0[:, 0::Data.KernelSize].shape[0], out_0[:, 0::Data.KernelSize].shape[1] + 1)
        out_1 = np.zeros(shape)
        for i in range(Data.KernelSize):
            mat = out_0[:, i::Data.KernelSize]
            out_1[:mat.shape[0], :mat.shape[1]] = mat

        # crop the extra
        size0 = list(np.argwhere(out_1.any(axis=0))[[0, -1]])
        size1 = list(np.argwhere(out_1.any(axis=1))[[0, -1]])
        self.output_matrix = np.float_(out_1[size1[0][0]:size1[1][0] + 1, size0[0][0]:size0[1][0] + 1] != False)

    def get_k_code(self, raster_mode: bool = False) -> KCommandManager:
        def get_raster_k_code(img_as_matrix: np.ndarray):
            img_as_matrix, command_protocol, is_done = \
                ImageToLines._get_next_move(img_as_matrix, np.array(img_as_matrix.shape) // 2)
            Kcode_Manager = KCommandManager(["Raster", "Circles"][np.argwhere(np.array([True, False]) == raster_mode)[0][0]],  # noqa
                                            [command_protocol], np.array(img_as_matrix.shape))

            if command_protocol is not None:
                Kcode_Manager.commands_protocols.append(command_protocol)

            while not is_done:
                img_as_matrix, command_protocol, is_done = \
                    ImageToLines._get_next_move(img_as_matrix, command_protocol.end_position)
                if command_protocol is not None:
                    Kcode_Manager.commands_protocols.append(command_protocol)
            return Kcode_Manager

        if raster_mode:
            self.KCode_manager = get_raster_k_code(self.output_matrix.copy()) # noqa
        else:
            matrix: np.ndarray = self.output_matrix.copy()
            Kcode_manager = KCommandManager("Circles", [], np.array(matrix.shape)) # noqa
            while matrix.any():
                last_edge = ImageToLines._get_edge(matrix)
                matrix -= last_edge
                Kcode_manager.commands_protocols += get_raster_k_code(last_edge).commands_protocols
            self.KCode_manager = Kcode_manager # noqa
        self.KCode_manager.optimize()
        return self.KCode_manager

    @staticmethod
    def _read_position(image: np.ndarray, x: int, y: int, read_size = True):
        if read_size:
            read_size = Data.KernelSize
        x *= read_size
        y *= read_size
        x1, y1 = x + read_size, y + read_size
        if x1 > len(image[0]):
            x1 = len(image[0])
        if y1 > len(image):
            y1 = len(image)

        return image[y:y1, x:x1]

    @staticmethod
    def _kernel(matrix: np.ndarray, x: int, y: int, weight_mat: np.ndarray = None) -> int:
        assert not (0 > x > len(matrix[0])), \
            f"KernelError: x value cannot be `{x}`. it must be between 0 and matrix size. \nin this case `{len(matrix[0])}`)"
        assert not (0 > y > len(matrix)), \
            f"KernelError: y value cannot be `{y}`. it must be between 0 and matrix size. \nin this case `{len(matrix)}`)"

        x0, y0 = x - 1, y - 1
        x1, y1 = x + 2, y + 2

        if x1 > len(matrix[0]):
            x1 = len(matrix[0])
        if y1 > len(matrix):
            y1 = len(matrix)

        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0

        if weight_mat is None:
            weight_mat = np.ones(matrix[y0:y1, x0:x1].shape)
        else:
            weight_mat = weight_mat[y0 - y + 1:y1 - y + 1, x0 - x + 1:x1 - x + 1]

        assert weight_mat.shape == matrix[y0:y1, x0:x1].shape, \
            f"weight matrix size {weight_mat.shape} must mach the matrix size {matrix[y0:y1, x0:x1].shape}"

        return (matrix[y0:y1, x0:x1] * weight_mat).sum() - matrix[y, x]

    @staticmethod
    def _get_edge(matrix: np.ndarray) -> np.ndarray:
        out_matrix = np.zeros((len(matrix), len(matrix[0])))

        weight_mat = np.array([
                [0, 1, 0],  # noqa
                [1, 1, 1],  # noqa
                [0, 1, 0]]) # noqa

        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                if not matrix[y, x]:
                    continue

                if ImageToLines._kernel(matrix, x, y, weight_mat=weight_mat) <= 3:
                    out_matrix[y, x] = 1
        return out_matrix

    @staticmethod
    def _get_next_move(matrix: np.ndarray, position: np.array) -> np.array:
        y, x = position
        if 0 > x > len(matrix[0]):
            massage = f"KernelError: x value cannot be `{x}`. it must be between 0 and matrix size. \nin this case `{len(matrix[0])}`)"
            raise Exception(massage)
        if 0 > y > len(matrix):
            massage = f"KernelError: y value cannot be `{y}`. it must be between 0 and matrix size. \nin this case `{len(matrix)}`)"
            raise Exception(massage)

        x0, y0 = x - 1, y - 1
        x1, y1 = x + 2, y + 2
        if x1 > len(matrix[0]):
            x1 = len(matrix[0])
        if y1 > len(matrix):
            y1 = len(matrix)
        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0
        temp = matrix[y0:y1, x0:x1]
        if len(np.argwhere(temp)):
            e_x, e_y = ImageToLines._find_closest_one(temp, np.array([y - y0, x - x0]))
            end_position = np.array([y0, x0]) + np.array([e_x, e_y])
            matrix[end_position[0]][end_position[1]] = 0
            return matrix, KCommand(np.array([y, x]), end_position, True), False
        elif np.any(matrix == 1):
            return matrix, KCommand(np.array([y, x]), ImageToLines._find_closest_one(matrix, position), False), False
        else:
            return matrix, None, True

    @staticmethod
    def _find_closest_one(matrix: np.ndarray, position: np.array) -> np.array:
        y, x = position
        matrix[y][x] = 0
        y_cords = (np.arange(len(matrix)) + np.zeros((1, len(matrix)))).T + \
                  np.zeros((len(matrix), len(matrix[0]))) - y
        x_cords = np.arange(len(matrix[0])) + np.zeros((1, len(matrix[0]))) + \
                  np.zeros((len(matrix), len(matrix[0]))) - x

        dis = np.sqrt(y_cords ** 2 + x_cords ** 2) * np.abs((matrix * 3 - 3) * len(matrix) * len(matrix[0]) + 1)
        dis[y][x] = 3 * len(matrix) * len(matrix[0])

        if dis.shape == (3, 3):
            dis -= np.array([
                [  0, 0,   0],  # noqa
                [0.5, 0, 0.5],  # noqa
                [  0, 0,   0]]) # noqa
        return np.argwhere(dis == np.min(dis))[0]





