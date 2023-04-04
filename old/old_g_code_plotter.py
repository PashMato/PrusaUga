#!/usr/bin/env python3
import sys
sys.path.append("/")

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse

from PythonCore.data import Data


def read_gcode(fn):
    acc = []

    with open(fn) as file:
        text = file.readlines()

    curr_x = 0
    curr_y = 0
    curr_z = 0
    for ctr, line in enumerate(text):
        code = line.split(';')[0].strip()
        if code == '':
            continue
        # Expecting something like:
        # $J=G90 G21 F2000 X-7.89473 Y30.26315 Z20.0
        header = "$J=G90 G21 F"

        assert code.startswith(header), f"{ctr + 1}: Don't know this command: {code}"

        fields = code.split(header)[1].split(' ')

        x1 = float(fields[1].lower().lstrip('x'))
        y1 = float(fields[2].lower().lstrip('y'))
        z1 = float(fields[3].lower().lstrip('z'))

        acc.append({'speed': int(fields[0]),
                    'x0': curr_x, 'y0': curr_y, 'z0': curr_z,
                    'x1': x1, 'y1': y1, 'z1': z1})

        curr_x = x1
        curr_y = y1
        curr_z = z1

    return pd.DataFrame(acc)


def draw_gcode(gcode, fignum=None):
    temp = gcode.copy()
    temp['space'] = np.nan
    temp['dz'] = temp['z1'] - temp['z0']
    dl = np.linalg.norm(temp[['x0', 'y0']].values - temp[['x1', 'y1']].values, axis=1)
    temp['width'] = np.where(temp['dz'] < 0, -1, np.ceil((temp['dz'] / 20 * (dl + 1e-10)).clip(0, 3)))

    def plot_group(grp):
        x = grp[['x0', 'x1', 'space']].values.ravel()
        y = grp[['y0', 'y1', 'space']].values.ravel()
        lw = grp['width'].iloc[0]
        if lw > 0:
            # Pen down
            plt.plot(x.ravel(), y.ravel(), 'b.-', ms=7, lw=lw)
        else:
            if lw < 0:
                # Error
                plt.plot(x.ravel(), y.ravel(), 'k:', lw=15, alpha=0.5)
            else:
                # Pen up
                plt.plot(x.ravel(), y.ravel(), 'r:', lw=2)

    plt.figure(fignum)
    plt.clf()
    temp.groupby('width').apply(plot_group)
    plt.gca().invert_yaxis()


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="File to read and plot")
    parser.add_argument("-v", "--version", dest="print_version_and_exit", action='store_true',
                        help="Print version and exit")
    args = parser.parse_args(argv)
    return args


def main(argv=None):
    args = parse_args(argv)
    if args.print_version_and_exit:
        print("No version!")
        exit(0)

    if args.file is None:
        print("Run with -h to get help")
        exit(1)

    file_name = args.file
    gcode = read_gcode(file_name)
    draw_gcode(gcode, os.path.split(file_name)[-1])
    plt.title(file_name)
    plt.show(block=True)


if __name__ == '__main__':
    main()
