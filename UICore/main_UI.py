import numpy as np
import pygame as pg
from UICore.UI_helper import Canvas, TextButton, Mouse
from UICore.file_viewer import FileManager
from UICore.Kcode_visual_reader import KcodeVisualReader

from PythonCore.image_to_lines import ImageToLines
from PythonCore.data import KcodeManager


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
        self.mouse = Mouse()

        pg.display.set_caption("Pusha Slicer")

        self.im2lines: ImageToLines = None
        self.raster_simulation: KcodeVisualReader = None
        self.circles_simulation: KcodeVisualReader = None
        self.CP: KcodeManager = None

        self.file_manager = FileManager(".", 0)
        self.import_mode = True
        self.file_manager_enable = True

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

        self.mouse.update()

        Canvas.Offset[1] *= int(Canvas.Offset[1] < 0)
        Canvas.Offset[1] = int(Canvas.Offset[1] < -750) * -750 + int(Canvas.Offset[1] >= -750) * Canvas.Offset[1]

        # handle the file manager
        if self.file_manager_enable:
            # draws the file manager when needed
            self.file_manager.draw()

            # set up the system when you pick a file
            if self.file_manager.read_selected_path() is not None:
                if self.import_mode is True:
                    self.im2lines = ImageToLines(self.file_manager.read_selected_path())
                    self.im2lines.get_k_code(raster_mode=True)
                    self.raster_simulation = KcodeVisualReader(self.im2lines.Kcode_manager)
                    self.im2lines.get_k_code(raster_mode=False)
                    self.circles_simulation = KcodeVisualReader(self.im2lines.Kcode_manager)
                    self.file_manager_enable = False
                    self.import_mode = False

                elif self.CP is not None:
                    # self.CP.write_file(f'{self.file_manager.}/{self.im2lines.name}_{self.CP.label}')
                    Canvas.PaintedLayer += 1

        # handle display simulation
        if self.raster_simulation is not None:
            self.raster_simulation.draw()
        if self.circles_simulation is not None:
            self.circles_simulation.draw()

        # handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.keep_running = False
            if event.type == pg.MOUSEWHEEL:
                Canvas.Offset[1] += event.y * 20

        # handle export buttons
        self.export_raster_button.draw(self.screen)
        self.export_circles_button.draw(self.screen)

        if self.export_raster_button.is_clicked or self.export_circles_button.is_clicked:
            self.raster_simulation.change_level(3)
            self.circles_simulation.change_level(3)

            if self.export_circles_button.is_clicked:
                self.CP = self.circles_simulation.CP
            else:
                self.CP = self.raster_simulation.CP

            self.file_manager = FileManager(self.file_manager.current_path, 2,
                                            position_offset=self.file_manager.offset_position, allow_select_files=True)
            self.file_manager_enable = True
            Canvas.PaintedLayer = 2

        pg.display.flip()
        self.clock.tick(25)

