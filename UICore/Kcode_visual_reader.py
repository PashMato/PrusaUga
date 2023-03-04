import numpy as np
import pygame as pg
import time
import os
from PythonCore.data import Data
from PythonCore.k_command_manger import KCommandManager
from UICore.canvas import Canvas
from UICore.buttons import Button
from UICore.text import Text


class KcodeVisualReader(Canvas): # noqa
    Counter = 0

    def __init__(self, cp: KCommandManager, speed: int = 10, factor: int = 20, position_offset: np.array = np.array([0, 0])):
        self.factor = factor * Data.LineThickness
        self.CP = cp

        # setting up the canvas that the simulation is painted on
        self.canvas = pg.Surface(np.array([[0, 1], [1, 0]]).dot(Data.DrawingSize * self.factor // Data.LineThickness) + 20)
        self.canvas.fill((10, 10, 10))

        # the main surface position
        pos = np.array([pg.display.get_surface().get_width() // 2, (pg.display.get_surface().get_height() // 2) +
                        (20 + self.canvas.get_height() + 60) * KcodeVisualReader.Counter])

        # set up the main surface (Canvas)
        super(KcodeVisualReader, self).__init__(pg.Surface((self.canvas.get_width(), self.canvas.get_height() + 60)),
                                                pos, 1, position_offset=position_offset)

        self.Speed = speed
        self._cp_pointer = 0
        self.dt = time.time()

        self.start_pos: np.ndarray = self.CP.commands[0].start_position

        # set up the replay button
        back_surface = pg.transform.scale(pg.image.load(os.path.abspath("UI_Images/Replay.png")), (60, 60))
        front_surface = pg.transform.scale(pg.image.load(os.path.abspath("UI_Images/Half_Transparent_Replay.png")), (60, 60))

        self.replay_button = \
            Button(front_surface, (np.array(self.surface.get_size()) - np.array(back_surface.get_size())) // 2,
                   self.layer, back_surface=back_surface, position_offset=self.position + self.position_offset)

        # title
        self.title = Text(np.array([self.surface.get_width() // 2, 10]), self.layer, self.CP.label,
                          (10, 100, 100), 30, position_offset=self.position + self.position_offset)

        # data
        text = f"Removed Commands: {self.CP.removed_commands}   Overall Commands: {self.CP.overall_commands}"\
               + f"  Times Head Up: {self.CP.times_head_up}"
        self.data_table = Text(np.array([self.surface.get_width() // 2, self.surface.get_height() - 20]), self.layer,
                               text, (100, 150, 150), 25, position_offset=self.position + self.position_offset)
        KcodeVisualReader.Counter += 1

    def draw(self, surface: pg.Surface = None):
        if self.layer != Canvas.PaintedLayer:
            return

        # check if there are steps to step and enough time passed
        if self._cp_pointer < len(self.CP.commands) and\
                (time.time() - self.dt) * self.Speed >= self.CP.commands[self._cp_pointer].time / 1000:
            command_protocol = self.CP.commands[self._cp_pointer]

            end_pos = np.dot(np.array([[0, 1], [1, 0]]), command_protocol.end_position * self.factor) + 10

            if command_protocol.is_printing:
                # draws the current step
                pg.draw.circle(self.canvas, (10, 10, 255), self.start_pos, 3)
                pg.draw.circle(self.canvas, (10, 10, 255), end_pos, 3)
                pg.draw.line(self.canvas, (10, 10, 255), self.start_pos, end_pos, 2)
                self.start_pos = end_pos
            else:
                # draws the current step (the head is up)
                pg.draw.line(self.canvas, (100, 10, 10), self.start_pos, end_pos, 1)
                self.start_pos = end_pos

            self._cp_pointer += 1
            self.dt = time.time()

        # draws all the surfaces on each other
        self.surface.blit(self.canvas, (0, 20))
        self.replay_button.draw(self.surface)
        self.title.draw(self.surface)
        self.data_table.draw(self.surface)
        super(KcodeVisualReader, self).draw(surface=surface)

        # handle replay
        if self.replay_button.is_clicked:
            self.canvas.fill((10, 10, 10))
            self._cp_pointer = 0
            self.replay_button.is_clicked = False

    def change_level(self, layer: int):
        super(KcodeVisualReader, self).change_level(layer)
        self.replay_button.change_level(layer)
        self.title.change_level(layer)
        self.data_table.change_level(layer)

