#!usr/bin/env python3
import sys

sys.path.append("/")

from settings.settings import get_all_versions, prop_options, set_settings
from commands import add_version, remove_version, edit_version, path_check, set_mode, read_file

from log.log import message, FormatError
from ASCII_logos import cake, pash_studios_and_prusa_uga, pash_studios, prusa_uga

from gcode.base_converter import BaseConverter

import argparse

from colorama import Fore


def parse_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", '--input', type=str, help="Input the file path")
    parser.add_argument("-w", '--write-to', type=str, help="Write gcode to a file path")
    parser.add_argument("-p", '--plot', help="Plots the image", action='store_true')
    parser.add_argument("-m", '--mode', type=int, choices={0, 1, 2, 3, 4}, default=0,
                        help="From Where Should Start Printing (Center, Corner 1 exc)." +
                             f"{Fore.MAGENTA} 0 is the center [1-4] is the corners (clockwise){Fore.RESET}")
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

    file_name = args.input

    if file_name is not None:
        path_check(args.input)

        message(cake, color=Fore.MAGENTA)  # UI
        message(prusa_uga, color=Fore.MAGENTA)  # UI

        message(f"Using setting `{args.setting}` to generate gcode (version 1.0)", color=Fore.BLUE)

        set_mode(args.mode)

        try:
            conv: BaseConverter = read_file(args.input)
        except FormatError as err:
            # TODO: handle errors in console
            # handle_errors_in_console(err)
            exit(1)

        conv.get_lines()
        gcode = conv.GCM

        if args.write_to:
            gcode.write_file(args.write_to)
        if args.plot:
            conv.g_show()
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
        # UI
        message(cake, color=Fore.MAGENTA)
        message(pash_studios_and_prusa_uga, color=Fore.MAGENTA)

        message("Run with -h or --help to get help")
        exit(0)


if __name__ == '__main__':
    main()

