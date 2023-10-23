from colorama import Fore


def message(message_, message_type=None, color=Fore.GREEN):
    if message_type is not None:
        message_type += ": "
    else:
        message_type = ""

    if message_type == "Warning: ":
        color = Fore.RED

    print(color + message_type + str(message_) + Fore.RESET)


class FormatError(Exception):
    pass


class DoesNotExitsError(Exception):
    pass


class TooManyArgsError(Exception):
    pass


class CanvasError(Exception):
    pass

class EmptyCall(Exception):
    pass
