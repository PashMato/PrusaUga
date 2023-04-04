import numpy as np

import cv2

from PythonCore.base_matrix_based_conv import MatBasedConverter

from PythonCore.k_command_manager import KCommandManager


class ImageToLines(MatBasedConverter):
    def __init__(self, path: str):
        super(ImageToLines, self).__init__(path)

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
                _edge = matrix * (ImageToLines.conv_mat(matrix, kernel=weight) < 3)
                matrix -= _edge

                d_mat += d * _edge
                d += 1
            return d_mat

        self.KCM = KCommandManager(f"{self.name} Circles", [], np.array(self.output_matrix.shape))
        # depth_mat = np.zeros(self.output_matrix.shape)
        depth_mat = depth_matrix()

        # for over the layer
        last_end_pos: np.ndarray = np.array(self.output_matrix.T.shape) // 2

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
                self.KCM += np.concatenate([last_end_pos, end_pos[1::-1], np.zeros(1)])
                last_end_pos = end_pos
            else:
                last_end_pos = self.KCM.commands[-1][2:4][1::-1]

            components = np.array(cv2.connectedComponents((depth_mat == i_depth).astype(np.int8))[1])  # noqa
            closest_edge_piece = ImageToLines.get_nearest(depth_mat == i_depth, last_end_pos)
            if closest_edge_piece is None:
                # if there isn't any edge peace continue
                i_depth -= 1
                continue

            edge = components == components[closest_edge_piece[0], closest_edge_piece[1]]
            depth_mat *= ~edge

            self.KCM += ImageToLines.close_loop(edge, start_pos=last_end_pos)
            i_depth -= 1

        print(f"Done Slicing {self.name}")
        self.KCM.optimize()
        print(f"Optimizing {self.name}")
        return self.KCM

    @staticmethod
    def close_loop(matrix, start_pos: np.ndarray = None, end_pos: np.ndarray = None) -> KCommandManager:
        if not np.any(matrix):
            # the matrix is empty there is mathing to slice
            return KCommandManager("Empty", [], np.array(matrix.shape))

        assert not (np.any(start_pos != None) and np.any(
            end_pos != None)), "close loop doesn't support dynamic end, start pos at once"  # noqa

        is_reversed = False

        if np.all(start_pos == end_pos) and np.all(start_pos == None):  # noqa
            # there aren't any requirements for the start or end position
            start_pos = ImageToLines.get_nearest(matrix, np.zeros(2))
        elif start_pos is None and end_pos is not None:
            # only the end pos is given
            start_pos = end_pos.copy().astype(int)
            is_reversed = True
        start_pos = start_pos.astype(int)

        KM: KCommandManager = KCommandManager("KCommandManager", [], np.array(matrix.shape))

        for cntr in range(np.sum(matrix != 0)):
            command = ImageToLines.simple_slice(matrix, start_pos)
            KM += command

            start_pos = KM.commands[-1][2:4][1::-1].astype(int)

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
            return np.concatenate([start_pos[1::-1], end_pos[1::-1], np.ones(1)])
        elif matrix.any():
            end_pos = ImageToLines.get_nearest(matrix, start_pos)
            return np.concatenate([start_pos[1::-1], end_pos[1::-1], np.zeros(1)])
        else:
            return None

