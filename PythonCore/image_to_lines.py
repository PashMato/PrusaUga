import os

from matplotlib.pyplot import *
from PythonCore.data import Data, KcodeManager, CommandProtocol


class ImageToLines:
    def __init__(self, path: str):
        self.image = imread(os.path.abspath(path))
        self.name = path.split("/")[-1]
        self.out_matrix = np.zeros(self.image.shape[:2])
        self.get_matrix()
        self.Kcode_manager = KcodeManager("None", []) # noqa

    def get_matrix(self):
        occupancy = self.image[:, :, 3] != 0
        size0 = list(np.argwhere(occupancy.any(axis=0))[[0, -1]])
        size1 = list(np.argwhere(occupancy.any(axis=1))[[0, -1]])
        crop_occupancy = occupancy[size1[0][0]:size1[1][0], size0[0][0]:size0[1][0]]

        Data.set_up(crop_occupancy.shape)
        out_matrix = np.zeros(np.array(crop_occupancy.shape) // Data.KernelSize + 1)
        for i in range(len(out_matrix)):
            for j in range(len(out_matrix[0])):
                out_matrix[i][j] = np.any(ImageToLines.read_position(crop_occupancy, j, i))
        self.out_matrix = out_matrix

    def get_k_code(self, raster_mode: bool = False) -> KcodeManager:
        def get_raster_k_code(img_as_matrix: np.ndarray):
            img_as_matrix, command_protocol, is_done = ImageToLines.get_next_move(img_as_matrix, np.array(img_as_matrix.shape) // 2)
            Kcode_Manager = KcodeManager(["Raster", "Circles"][np.argwhere(np.array([True, False]) == raster_mode)[0][0]], [command_protocol]) # noqa

            if command_protocol is not None:
                Kcode_Manager.commands_protocols.append(command_protocol)

            while not is_done:
                img_as_matrix, command_protocol, is_done = ImageToLines.get_next_move(img_as_matrix, command_protocol.end_position)
                if command_protocol is not None:
                    Kcode_Manager.commands_protocols.append(command_protocol)
            return Kcode_Manager

        if raster_mode:
            self.Kcode_manager = get_raster_k_code(self.out_matrix.copy()) # noqa
        else:
            matrix = self.out_matrix.copy()
            Kcode_manager = KcodeManager("Circles", []) # noqa
            while matrix.any():
                last_edge = ImageToLines.get_edge(matrix)
                matrix -= last_edge
                Kcode_manager.commands_protocols += get_raster_k_code(last_edge).commands_protocols
            self.Kcode_manager = Kcode_manager # noqa
        return self.Kcode_manager

    @staticmethod
    def read_position(image: np.ndarray, x: int, y: int, read_size = True):
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
    def kernel(matrix: np.matrix, x: int, y: int) -> int:
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
        if y1 > len(matrix): y1 = len(matrix)
        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0

        return matrix[y0:y1, x0:x1].sum() - matrix[y, x]

    @staticmethod
    def get_edge(matrix: np.matrix) -> np.ndarray:
        out_matrix = np.zeros((len(matrix), len(matrix[0])))
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                if not matrix[y, x]:
                    continue

                if ImageToLines.kernel(matrix, x, y) <= 7:
                    out_matrix[y, x] = 1
        return out_matrix

    @staticmethod
    def get_next_move(matrix: np.ndarray, position: np.array) -> np.array:
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
            e_x, e_y = ImageToLines.find_closest_one(temp, np.array([y - y0, x - x0]))
            end_position = np.array([y0, x0]) + np.array([e_x, e_y])
            matrix[end_position[0]][end_position[1]] = 0
            return matrix, CommandProtocol(np.array([y, x]), end_position, True), False
        elif np.any(matrix == 1):
            return matrix, CommandProtocol(np.array([y, x]), ImageToLines.find_closest_one(matrix, position), False), False
        else:
            return matrix, None, True

    @staticmethod
    def find_closest_one(matrix: np.ndarray, position: np.array) -> np.array:
        y, x = position
        matrix[y][x] = 0
        y_cords = (np.arange(len(matrix)) + np.zeros((1, len(matrix)))).T\
                  + np.zeros((len(matrix), len(matrix[0]))) - y
        x_cords = np.arange(len(matrix[0])) + np.zeros((1, len(matrix[0])))\
                  + np.zeros((len(matrix), len(matrix[0]))) - x
        dis = np.sqrt(y_cords ** 2 + x_cords ** 2) * np.abs((matrix * 3 - 3) * len(matrix) * len(matrix[0]) + 1)
        dis[y][x] = 3 * len(matrix) * len(matrix[0])
        return np.argwhere(dis == np.min(dis))[0]





