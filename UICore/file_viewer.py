import numpy as np
import pygame as pg
import os

from UICore.canvas import Canvas
from UICore.buttons import TextButton, Button


class File(TextButton):
    Id = 0
    FilesInLine = 3
    CanvasSize = np.array([165, 120])

    def __init__(self, path: str, layer: int, position_offset: np.array = np.array([0, 0])):
        if len(path) >= 5 and path[-4:] == ".png":
            image = pg.image.load(os.path.abspath(path))
            name = path.split("/")[-1][:-4]
        else:
            image = pg.image.load("UI_Images/FileIcon.png")
            name = path.split("/")[-1]

        image_max = max(image.get_width(), image.get_height())
        canvas_max = File.CanvasSize[image.get_size().index(image_max)]
        size = np.int_(np.array(image.get_size()) * canvas_max * (1/image_max)) + 1

        image = pg.transform.scale(image, size)

        back_image = image.copy()
        back_image.set_alpha(200)

        surface = pg.Surface(File.CanvasSize + 10)
        surface.fill((20, 20, 20))
        back_surface = surface.copy()

        surface.blit(image,
                     ((surface.get_width() - image.get_width()) // 2, (surface.get_height() - image.get_height()) // 2))

        back_surface.blit(back_image,
           ((surface.get_width() - back_image.get_width()) // 2, (surface.get_height() - back_image.get_height()) // 2))

        position = (np.array([File.Id % File.FilesInLine, File.Id // File.FilesInLine])) * (File.CanvasSize + 20)
        position[0] += (pg.display.get_surface().get_width() - (File.FilesInLine - 1) * (File.CanvasSize[0] + 20)) // 2
        position[1] += 40 + File.CanvasSize[1] // 2

        color = (150, 10, 50)

        super(File, self).__init__(position, layer, name, color, 20, font_type="Arial",
                               position_offset=position_offset, alpha=180, bg_surface=surface, bbg_surface=back_surface)
        self.path = path

        File.Id += 1
    
    def draw(self, surface: pg.Surface = None):
        super(File, self).draw(surface=surface)


class FileManager:
    def __init__(self, start_path: str, layer: int,
                 position_offset: np.array = np.array([0, 0]), allow_select_files: bool = False):
        self.current_path = os.path.abspath(start_path)
        self.files = []
        self.layer = layer
        self.offset_position = position_offset
        self.update_files()
        self._chosen_path: str = ""

        self._selected_path: str = ""
        self._selected_file: File = None # noqa

        self.allow_select_files: bool = allow_select_files

        surface: pg.Surface = pg.image.load("UI_Images/Back.png")
        position: np.array = np.array([30, 30])

        self.back_button: Button = Button(surface, position, self.layer,
                                  alpha=150, position_offset=position_offset, static=False)

        surface = pg.image.load("UI_Images/Open.png")
        position: np.array = np.array([pg.display.get_surface().get_width() - 30, 30])

        self.open_button: Button = Button(surface, position, self.layer,
                                  alpha=150, position_offset=position_offset, static=False)

    def update_files(self):
        all_relevant_files = os.listdir(self.current_path)
        self.files = []
        self._selected_file = None
        File.Id = 0
        for file in all_relevant_files:
            if file[0] != "." and (os.path.isdir(self.current_path + "/" + file) or file[-4:] == ".png"):
                file_path = self.current_path + "/" + file
                self.files.append(File(file_path, self.layer, self.offset_position))

    def draw(self):
        if self.layer != Canvas.PaintedLayer:
            return

        self.back_button.draw(pg.display.get_surface())
        self.open_button.draw(pg.display.get_surface())

        if self.back_button.is_clicked and os.path.exists(os.path.abspath(self.current_path + "/..")):
            self.current_path = os.path.abspath(self.current_path + "/..")
            self.update_files()
            return

        if self.open_button.is_clicked:
            self._chosen_path = self._selected_path
            Canvas.PaintedLayer += 1

        for file in self.files:
            file.draw()
            if file.is_double_clicked:
                if file.path.split("/")[-1][0] != "." and os.path.exists(file.path) and os.path.isdir(file.path):
                    self.current_path = file.path
                    self.update_files()
                break
            elif file.is_clicked and os.path.exists(file.path):
                if os.path.isdir(file.path) and not self.allow_select_files:
                    continue
                if self._selected_file is not None:
                    self._selected_file.highlight_bg(False)
                self._selected_path = file.path
                self._selected_file = file
                self._selected_file.highlight_bg(True)

    def read_selected_path(self):
        if self._chosen_path == "":
            return None
        return self._chosen_path

    def change_layer(self, layer: int):
        self.layer = layer
        self.update_files()
        self.open_button.layer = layer
        self.back_button.layer = layer



