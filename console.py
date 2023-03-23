#!usr/bin/env python3
import os.path
import sys

sys.path.append("/home/pash/PycharmProjects/PrushaUga")

from PythonCore.image_to_kcommands import ImageToLines
from PythonCore.k_command_manger import KCommandManager, generate_tests

import Setting.get_settings as settings

import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--input', type=str, help="Input the file path")
    parser.add_argument("-w", '--write-to', type=str, help="Write gcode to a file path")
    parser.add_argument("-p", '--plot', type=str, help="Plots the image", default="off", choices={'on', 'off'})
    parser.add_argument("-t", '--test', type=str,
                        help="Create a test and write it to the given path [--test input]. must be a directory")
    parser.add_argument("-s", '--setting', type=float, help="the machine settings", default=1,
                        choices=settings.get_settings_options())

    parser.add_argument('--add', nargs=2, metavar=('(version, ', 'path)'), help="Add a setting by path")
    parser.add_argument('--remove', type=float, help="Remove a setting by path and name")

    parser.add_argument('--list', type=str, help="Show all the possible settings", choices={'on', 'off'}, default='off')
    parser.add_argument('--show', type=float, help="Show a certain setting", choices=settings.get_settings_options())

    parser.add_argument('--edit', type=float, choices=settings.get_settings_options(), help="Edit a setting Version")
    parser.add_argument('--prop', type=str, choices=settings.prop_options.keys(), help="The edited property")
    parser.add_argument('--value', nargs="*", type=str, help="The edited property value")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    settings.set_settings(args.setting)

    if args.test is not None:
        if not os.path.exists(args.test):
            print(f"Error: path `{args.test}` doesn't exists")
            exit(1)
        if not os.path.isdir(args.test):
            print(f"Error: path must be a directory (save 2 files)")
            exit(1)

        test1, test2 = generate_tests()

        test1.write_file(args.test, save_outline=False)
        test2.write_file(args.test, save_outline=False)

    elif args.input is not None and os.path.exists(args.input):
        im2mat: ImageToLines = ImageToLines(args.input)
        gcode: KCommandManager = im2mat.get_k_code()

        if args.write_to:
            gcode.write_file(args.write_to)
        if args.plot == "on":
            im2mat.k_show()
    elif args.add is not None:
        v, path = args.add
        try:
            version = float(v)
            if not os.path.exists(path):
                print(f"Could not find path `{path}`")
                exit(1)

            settings.add_setting(version, path)
        except():
            print(f"Version must be float (not `{v}`")
            exit(1)
    elif args.remove is not None:
        if args.remove not in settings.get_settings_options():
            print(f"No Such Version {settings.get_settings_options()}")

        settings.remove_setting(args.remove)
    elif args.edit is not None:
        if args.prop is None:
            print("Error: --prop must be given while editing")
            exit(1)
        if args.value is None:
            print(f"Error: --value must be given while editing")
            exit(1)
        if args.prop != "DrawingSize" and len(args.value) > 1:
            print("Error: too many args. one arg is expected")
            exit(1)
        if args.prop == "DrawingSize" and len(args.value) != 2:
            print("Error: too many args. two args are expected")
            exit(1)

        try:
            if args.prop == "DrawingSize":
                value = (int(args.value[0]), int(args.value[1]))
            else:
                value = float(args.value)
            settings.edit_setting(args.edit, args.prop, value)
        except():
            print(f"Error: cannot convert ({args.value}) to {settings.prop_options[args.prop]}")
            exit(1)
    elif args.list == 'on':
        print(settings.get_settings_options())
    elif args.show is not None:
        print(settings.set_settings(args.show))
    else:
        print("Run with -h or --help to get help")
        exit(1)


if __name__ == '__main__':
    main()
