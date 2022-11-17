import numpy as np
import pygame as pg
from UICore.UI_helper import Canvas, TextButton
from UICore.file_viewer import FileManager

from PythonCore.image_to_lines import ImageToLines
from UICore.Kcode_visual_reader import KcodeVisualReader


class MainUI:
    def __init__(self):
        # setup pygame
        pg.init()
        pg.display.init()
        pg.font.init()

        # setting up the class
        self.keep_running = True
        self.screen = pg.display.set_mode((850, 600))
        self.clock = pg.time.Clock()

        pg.display.set_caption("Pusha Slicer")

        self.im2lines = None
        self.raster_simulation = None
        self.circles_simulation = None
        self.CP = None

        self.file_manager = FileManager(".", 0)

        self.export_raster_button = TextButton(np.array([20, 10]), 1, "Export Raster K-code", (100, 150, 200), 30,
                                               alpha=100, center_position=False, static=True)

        self.export_circles_button = TextButton(np.array([self.screen.get_width() - 20, 10]), 1,
                                                "Select Circles K-code", (100, 150, 200), 30,
                                                alpha=100, center_position=False, static=True)
        self.export_circles_button.position[0] -= self.export_circles_button.surface.get_width()

    def start(self):
        while self.keep_running:
            self.update()

    def update(self):
        self.screen.fill((5, 5, 5))

        Canvas.Offset[1] *= int(Canvas.Offset[1] < 0)
        Canvas.Offset[1] = int(Canvas.Offset[1] < -750) * -750 + int(Canvas.Offset[1] >= -750) * Canvas.Offset[1]

        # handle the file manager
        if self.file_manager is not None:
            # draws the file manager when needed
            self.file_manager.draw()

            # set up the system when you pick a file
            if self.file_manager.read_selected_path() is not None:
                self.im2lines = ImageToLines(self.file_manager.read_selected_path())
                self.im2lines.get_k_code(raster_mode=True)
                self.raster_simulation = KcodeVisualReader(self.im2lines.Kcode_manager)
                self.im2lines.get_k_code(raster_mode=False)
                self.circles_simulation = KcodeVisualReader(self.im2lines.Kcode_manager)
                self.file_manager = None

        # handle display simulation
        if self.raster_simulation is not None:
            self.raster_simulation.draw()
        if self.circles_simulation is not None:
            self.circles_simulation.draw()

        # handle export buttons
        if self.export_raster_button is not None and self.export_raster_button.is_clicked is True:
            self.raster_simulation.change_level(2)
            self.circles_simulation.change_level(2)
            Canvas.PaintedLayer = 2
        if self.export_circles_button is not None and self.export_circles_button.is_clicked is True:
            self.raster_simulation.change_level(2)
            self.circles_simulation.change_level(2)
            Canvas.PaintedLayer = 2

        # handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.keep_running = False
            if event.type == pg.MOUSEWHEEL:
                Canvas.Offset[1] += event.y * 20

        self.export_raster_button.draw(self.screen)
        self.export_circles_button.draw(self.screen)

        pg.display.flip()
        self.clock.tick(25)

