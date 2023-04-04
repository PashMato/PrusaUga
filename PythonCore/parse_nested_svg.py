import numpy as np
import sys
from tqdm import tqdm
import svg.path
from xml.dom import minidom

from PythonCore.base_converter import BaseConverter
from PythonCore.k_command_manager import KCommandManager
from PythonCore.data import Data


class NestedSvgParser:
    def __init__(self, file_name):
        self.file_name = file_name
        self.content: minidom.Document = minidom.parse(self.file_name)
        self.svg = self.content.getElementsByTagName('svg')[0]
        self.all_g = self.svg.getElementsByTagName('g')
        self.size = np.array([
            int(self.content.getElementsByTagName('svg')[0].attributes.get('height').value.rstrip('m')),
            int(self.content.getElementsByTagName('svg')[0].attributes.get('width').value.rstrip('m'))])
        self.all_paths = self.content.getElementsByTagName('path')
        self.parsed_paths = []
        self.lines = []
        self._sampled_arrays: list[list[np.ndarray]] = []
        self._known_gs = {}
        self.parse()

    def parse(self):
        self.collect_paths()
        self.separate_penups()
        self.sample_lines()

    def get_arrays(self):
        return self._sampled_arrays

    def collect_paths(self):
        for path in self.all_paths:
            path_trans = self.get_total_transform(path.parentNode)
            self.parsed_paths.append([path, path_trans])

    def separate_penups(self):
        eacc = []
        for pp, trans in tqdm(self.parsed_paths):
            path_text = pp.attributes['d'].firstChild.data
            path_obj = svg.path.parse_path(path_text)
            l = path_obj.length()

            while True:
                try:
                    elem = path_obj.pop(0)
                    if isinstance(elem, svg.path.Move):
                        eacc.append([svg.path.Path(), trans])
                    eacc[-1][0].append(elem)
                except IndexError:
                    break
        self.lines = eacc

    def sample_lines(self, scale=1):
        self._sampled_arrays = []
        for cur_path, trans in tqdm(self.lines):
            all_s = np.linspace(0, 1, int(scale * np.ceil(cur_path.length())))
            path_coords =[]
            for s in all_s:
                path_coords.append(cur_path.point(s))

            all_pos_1 = np.c_[np.real(path_coords), np.imag(path_coords), np.ones(len(path_coords))]

            all_pos_trans = trans[:2].dot(all_pos_1.T)

            self._sampled_arrays.append([all_pos_trans[0], all_pos_trans[1]])

    def get_total_transform(self, g):
        if g in self._known_gs:
            return self._known_gs[g]

        cur_trans = 1
        while g is not None and g is not self.svg:
            pre_trans = self.parse_transform(g)
            cur_trans = np.dot(pre_trans, cur_trans)
            g = g.parentNode
        self._known_gs[g] = cur_trans
        return cur_trans

    @classmethod
    def parse_transform(cls, g):
        my_transform = g.getAttribute('transform')
        if my_transform == '':
            my_transform = np.eye(3)
        elif 'scale(' in my_transform:
            scale = float(my_transform.replace('scale(', '').replace(')', ''))
            my_transform = np.diag([scale, scale, 1])
        elif 'matrix(' in my_transform:
            floats = my_transform.replace('matrix(', '').replace(')', '').replace(' ', '').split(',')
            my_transform = np.concatenate([np.array([float(f) for f in floats]).reshape(3, 2).T, [[0, 0, 1]]])
        else:
            assert False, F"Don't know transform {my_transform}"
        return my_transform

    def plot(self, fig=None):
        import matplotlib.pyplot as plt
        plt.figure(fig)
        plt.clf()
        for sa in self._sampled_arrays:
            plt.plot(sa[0], sa[1])
        plt.gca().invert_yaxis()
        plt.gca().axis('equal')
        plt.show()

def main():
    default_filename = '/home/pash/PycharmProjects/PrushaUga/theBeatles.svg'
    filename = sys.argv[1] if len(sys.argv) > 1 else default_filename
    s2l = NestedSvgParser(filename)
    s2l.plot()
    a = 4


if __name__ == '__main__':
    main()
