import numpy as np
import time

import pygame as pg

class Mouse:
    _check5buttons = 3
    DOWN = np.array([0] * 3)
    UP = np.array([0] * 3)
    STILL_DOWN = np.array([0] * 3)

    DOUBLE_CLICK = np.array([0] * 3)
    SumTime = np.array([0] * 3)
    last_fame_time = time.time()

    last_STILL_DOWN = np.array([0] * 3)

    @staticmethod
    def __init__(check5buttons: bool = False):
        Mouse._check5buttons = check5buttons
        Mouse.DOWN = np.array([0] * (int(Mouse._check5buttons) * 2 + 3))
        Mouse.UP = np.array([0] * (int(Mouse._check5buttons) * 2 + 3))
        Mouse.STILL_DOWN = np.array([0] * (int(Mouse._check5buttons) * 2 + 3))

        Mouse.DOUBLE_CLICK = np.array([0] * (int(Mouse._check5buttons) * 2 + 3))
        Mouse.SumTime = np.array([0] * (int(Mouse._check5buttons) * 2 + 3))
        Mouse.last_fame_time = time.time()

        Mouse.last_STILL_DOWN = np.array([0] * (int(Mouse._check5buttons) * 2 + 3))

    @staticmethod
    def update():
        Mouse.STILL_DOWN = np.array(pg.mouse.get_pressed(int(Mouse._check5buttons) * 2 + 3), int)

        time_ = time.time()

        Mouse.SumTime = (Mouse.SumTime + time_ - Mouse.last_fame_time) * np.abs(Mouse.DOWN - 1)

        if len(Mouse.STILL_DOWN) == len(Mouse.last_STILL_DOWN):
            buttons_delta = Mouse.STILL_DOWN - Mouse.last_STILL_DOWN
            Mouse.DOWN = np.int_(buttons_delta == 1)
            Mouse.UP = np.int_(buttons_delta == -1)

        Mouse.DOUBLE_CLICK = np.int_((Mouse.SumTime < .5) * (Mouse.SumTime != 0) * Mouse.DOWN)

        Mouse.last_STILL_DOWN = Mouse.STILL_DOWN.copy()
        Mouse.last_fame_time = time_