from turtle import position

import numpy as np
import pygame as pg


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


class Button(Canvas):  # a class that handle buttons
    def __init__(self, surface: pg.Surface, position: np.array, layer: int, alpha: int = 255,
                 back_surface: pg.Surface = None, position_offset: np.array = np.array([0, 0]),
                 center_position: bool = True, static: bool = False):

        # calls the Canvas's __init__
        super(Button, self).__init__(surface, position, layer,
                                     position_offset=position_offset, center_position=center_position)

        # makes sure the alpha is in the correct range
        # handle when back_surface is None
        if back_surface is None:
            back_surface = self.surface.copy()

        if not 0 <= alpha <= 255:
            alpha = 255 * int(alpha > 255)

        self.back_surface = back_surface
        self.front_surface = self.surface.copy()
        self.front_surface.set_alpha(alpha)

        self.is_clicked = False
        self.is_mouse_on = False

        self.static = static  # if the Button is static it would be static on the screen

    # draws the Button
    def draw(self, surface: pg.Surface = None):
        if self.layer != Canvas.PaintedLayer:
            return
        super(Button, self).draw(surface=surface)
        self.update()

    # handle when the Button is pressed
    def update(self):
        right_bottom = np.array(self.surface.get_size()) + self.position + self.position_offset + \
                       Canvas.Offset * (not self.static)

        left_top = self.position + self.position_offset + Canvas.Offset * (not self.static)

        mouse_pos = np.array(pg.mouse.get_pos())

        # check if the mouse position is in the correct rage
        if not np.any((left_top <= mouse_pos) == False) and not np.any((mouse_pos <= right_bottom) == False):
            self.is_mouse_on = True
            self.surface = self.back_surface

            if pg.mouse.get_pressed(3)[0]:
                self.is_clicked = True
        else:
            self.surface = self.front_surface
            self.is_mouse_on = False
            self.is_clicked = False


class Text(Canvas):  # a class that handle text
    def __init__(self, position: np.array, layer: int, text, text_color, text_size: int,
                 position_offset=np.array([0, 0]), font_type: str = 'Comic Sans MS', center_position: bool = True):

        surface = pg.font.SysFont(font_type, text_size).render(text, False, text_color).convert()

        # calls the Canvas's __init__
        super(Text, self).__init__(surface, position, layer,
                                   position_offset=position_offset, center_position=center_position)

    # edit the text
    def set_text(self, text: str, text_color, text_size: int,
                 font_type: str = 'Comic Sans MS', center_position: bool = True):

        self.__init__(self.position, self.layer, text, text_color, text_size,
                      position_offset=self.position_offset, font_type=font_type, center_position=center_position)

    # draws the Text
    def draw(self, surface: pg.Surface = None):
        if self.layer != Canvas.PaintedLayer:
            return
        super(Text, self).draw(surface)


class TextButton(Button):
    def __init__(self, position: np.array, layer: int, text, text_color, text_size: int,
                 bg_surface: pg.Surface = None, bbg_surface: pg.Surface = None, alpha: int = 255,
                 position_offset=np.array([0, 0]), font_type: str = 'Comic Sans MS',
                 center_position: bool = True, static: bool = False):

        # creates the the text surface
        surface = pg.font.SysFont(font_type, text_size).render(text, False, text_color)

        # handle when the bg_surface or bg_surface is None
        if bg_surface is None:
            bg_surface = pg.Surface(surface.get_size(), pg.SRCALPHA, 32)
        if bbg_surface is None:
            bbg_surface = pg.Surface(surface.get_size(), pg.SRCALPHA, 32)

        # draws the Text surface on the bg_surface and bg_surface
        bg_surface.blit(surface,
                        (np.array(bg_surface.get_size()) - np.array(surface.get_size())) // 2)
        bbg_surface.blit(surface,
                         (np.array(bbg_surface.get_size()) - np.array(surface.get_size())) // 2)

        # calls the Button's __init__
        super(TextButton, self).__init__(bbg_surface, position, layer, alpha=alpha,
                                         back_surface=bg_surface, position_offset=position_offset, static=static, center_position=center_position)

    # edit the text
    def set_text(self, text: str, text_color, text_size: int,
                 font_type: str = 'Comic Sans MS', center_position: bool = True):

        self.__init__(self.position, self.layer, text, text_color, text_size,
                      position_offset=self.position_offset, font_type=font_type, center_position=center_position)

    # draws the TextButton
    def draw(self, surface: pg.Surface = None):
        if self.layer != Canvas.PaintedLayer:
            return
        super(TextButton, self).draw(surface)

