from colorama import Fore

_did_throw_error = False
_did_throw_warning = False

def message(message_, message_type: str =None, color=Fore.GREEN):
    """
    A log messager. if message_type is: warning of error color is set to red
    """
    global _did_throw_warning, _did_throw_error

    if message_type is None:
        message_type = ""

    if message_type.title() == "Warning":
        color = Fore.RED
        _did_throw_warning = True
    elif message_type.title() == "Error":
        color = Fore.RED
        _did_throw_error = True

    if message_type != "":
        message_type += ": "

    print(color + message_type.title() + str(message_) + Fore.RESET)

def did_throw_warning() -> bool:
    return _did_throw_error or _did_throw_warning

def did_throw_error() -> bool:
    return _did_throw_error
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
