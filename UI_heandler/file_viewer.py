import numpy as np
import pygame as pg
import os
import glob

from UI_heandler.UI_helper import TextButton, Button, Canvas


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

        super(File, self).__init__(position, layer, name, (150, 10, 50), 25, font_type="Oswald",
                                   position_offset=position_offset, bg_surface=surface, bbg_surface=back_surface)
        self.path = path

        File.Id += 1


class FileManager:
    def __init__(self, start_path: str, layer: int, position_offset: np.array = np.array([0, 0])):
        self.current_path = start_path
        self.files = []
        self.layer = layer
        self.offset_position = position_offset
        self.update_files()
        self.selected_path = ""

        surface = pg.image.load("UI_Images/Back.png")
        position = np.array([30, 30])

        self.back_button = Button(surface, position, self.layer,
                                  alpha=150, position_offset=position_offset, static=False)

    def update_files(self):
        all_relevent_files = glob.glob(self.current_path + "*.png") + os.listdir(self.current_path)
        self.files = []
        File.Id = 0
        for file in all_relevent_files:
            if file[0] != "." or file[-4:] == ".png":
                file_path = self.current_path + "/" + file
                self.files.append(File(file_path, self.layer, self.offset_position))

    def draw(self):
        if self.layer != Canvas.PaintedLayer:
            return

        self.back_button.draw(pg.display.get_surface())

        if self.back_button.is_clicked:
            self.current_path = os.path.abspath("..")
            self.update_files()
            return

        for file in self.files:
            file.draw()
            if file.is_clicked:
                if len(file.path) >= 5 and file.path[-4:] == ".png":
                    self.selected_path = file.path
                    Canvas.PaintedLayer += 1
                elif "." not in file.path:
                    self.current_path = file.path
                    self.update_files()
                break

