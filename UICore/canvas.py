import pygame as pg
import numpy as np
from matplotlib import pyplot as plt

def draw(sur: pg.Surface):
    im = np.zeros(list(sur.get_size()) + [4])
    for y in range(sur.get_height()):
        for x in range(sur.get_width()):
            im[y][x] = np.array(sur.get_at((x, y)))
    plt.figure()
    plt.imshow(im)

class Canvas:  # makes an object visible on the screen
    Offset = np.array([0, 0])
    PaintedLayer = 0

    def __init__(self, surface: pg.Surface, position: np.array, layer: int,
                 position_offset: np.array = np.array([0, 0]), center_position: bool = True):

        self.surface = surface

        # makes sure the position is relative to the center of the surface
        if center_position:
            position -= np.array(surface.get_size()) // 2

        self.position = position
        self.position_offset = position_offset
        self.layer = layer

    def draw(self, surface: pg.Surface = None):
        # draws the object
        # child class override this method
        if self.layer != Canvas.PaintedLayer:
            return
        show_canvas(self, surface=surface)

    # change the Canvas's layer
    def change_level(self, layer: int):
        self.layer = layer


def show_canvas(canvas: Canvas, surface: pg.Surface = None):
    # the actual method that draws a Canvas object on the screen
    if canvas.layer != Canvas.PaintedLayer:
        return
    offset = np.zeros(2)
    if surface is None:
        surface = pg.display.get_surface()
        offset = Canvas.Offset
    surface.blit(canvas.surface, canvas.position + offset)


