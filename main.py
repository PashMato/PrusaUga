#!usr/bin/env python3
import sys

import matplotlib.pyplot as plt

import log.log

sys.path.append("/")

from settings.settings import get_all_versions, prop_options, set_settings
from commands import add_version, remove_version, edit_version, path_check, set_mode, read_file

from log.log import message, FormatError, CanvasError
from ASCII_logos import cake, pash_studios_and_prusa_uga, pash_studios, prusa_uga

from gcode.base_converter import BaseConverter

import argparse

from colorama import Fore


def parse_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", '--input', nargs="*", type=str, help="Input the file path")
    parser.add_argument("-w", '--write-to', type=str, help="Write gcode to a file path")
    parser.add_argument("-p", '--plot', help="Plots the image", action='store_true', default=False)
    parser.add_argument("-o", '--outline', help="Doesn't save the outline gcode", action='store_false', default=True)
    parser.add_argument("-e", '--edge', help="Save only the edge drawing outline gcode", action='store_true', default=False)
    parser.add_argument("-m", '--mode', type=int, choices={-1, 0, 1, 2, 3, 4}, default=0,
                        help="From Where Should Start Printing (Center, Corner 1 exc)." +
                             f"-1 is to start from the corner of the printer (0, 0) and print the drawing centered in the middle of the printer. " +
                             f" 0 is the center [1-4] is the corners (clockwise). You can run just -m to print what each more does")
    parser.add_argument("-s", '--setting', type=float, help="the machine settings", default=2.5,
                        choices=get_all_versions())

    parser.add_argument('--add', nargs=2, metavar=('(version, ', 'path)'), help="Add a setting by path")
    parser.add_argument('--remove', type=float, help="Remove a setting by path and name")

    parser.add_argument('--list', action='store_true', help="Show all the possible settings")
    parser.add_argument('--show', type=float, help="Show a certain setting", choices=get_all_versions())

    parser.add_argument('--edit', type=float, choices=get_all_versions(), help="Edit a setting Version")
    parser.add_argument('--prop', type=str, choices=prop_options.keys(), help="The edited property")
    parser.add_argument('--value', nargs="*", type=str, help="The edited property value")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    set_settings(args.setting)

    message(cake, color=Fore.MAGENTA)  # UI
    message(prusa_uga, color=Fore.MAGENTA)  # UI

    try:
        set_mode(args.mode)
        message(f"Using setting `{args.setting}` to generate gcode (version 2.0)", color=Fore.BLUE)
    except ValueError as err:
        message(str(err), "error")
        exit(1)

    if args.input is not None:
        conv_list = []

        for file_name in args.input:
            try:
                path_check(file_name)
            except FileNotFoundError as err:
                message(err.__str__(), message_type="error")
                continue

            try:
                conv: BaseConverter = read_file(file_name)
            except FormatError as err:
                message(str(err), "error")
                continue

            try:
                conv.get_lines()
            except CanvasError as err:
                message(str(err), "error")
                continue
            conv_list.append(conv)

        for conv in conv_list:
            gcode = conv.GCM

            if args.write_to:
                if args.edge:  # saving the edge drawing outline
                    conv.get_canvas_edge_test().write_file(args.write_to, False)
                else: # saves the gcode and (if needed) the outline
                    gcode.write_file(args.write_to, args.outline)


        if args.plot:
            for conv in conv_list:
                if args.plot:
                    conv.g_show(block=False)
            plt.show()
        # end of writing if
    elif args.add is not None:
        v, path = args.add
        add_version(v, path)

    elif args.remove is not None:
        remove_version(args.remove)

    elif args.edit is not None:
        edit_version(args.edit, args.prop, args.value)

    elif args.list:
        message(get_all_versions(), color=Fore.LIGHTYELLOW_EX)
    elif args.show is not None:
        message(set_settings(args.show), color=Fore.LIGHTYELLOW_EX)
    else:
        message("Run with -h or --help to get help")
        exit(0)


if __name__ == '__main__':
    main()

