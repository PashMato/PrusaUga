import pygame as pg
import numpy as np

from UICore.canvas import Canvas
from UICore.mouse import Mouse

# a class that handle buttons
class Button(Canvas):
    def __init__(self, surface: pg.Surface, position: np.array, layer: int, alpha: int = 255, alpha2: int = 70,
                 back_surface: pg.Surface = None, selected_surface: pg.Surface = None, color2: list = (50, 100, 200),
                 position_offset: np.array = np.array([0, 0]), center_position: bool = True, static: bool = False):

        # calls the Canvas's __init__
        super(Button, self).__init__(surface, position, layer,
                                     position_offset=position_offset, center_position=center_position)

        # makes sure the alpha is in the correct range
        # handle when back_surface is None
        if back_surface is None:
            back_surface = self.surface.copy()

        if not 0 <= alpha <= 255:
            alpha = 255 * int(alpha > 255)

        if not 0 <= alpha2 <= 255:
            alpha2 = 255 * int(alpha2 > 255)

        if selected_surface is None:
            selected_surface = self.surface.copy()

        self.back_surface = back_surface
        self.front_surface = self.surface.copy()
        self.selected_surface = selected_surface

        self.front_surface.set_alpha(alpha)

        highlighted_surface: pg.Surface = pg.Surface((selected_surface.get_size()))
        highlighted_surface.fill(color2)
        highlighted_surface.set_alpha(alpha2)
        self.selected_surface.blit(highlighted_surface, (0, 0))

        self.bg_highlighted = False

        self.is_clicked = False
        self.is_double_clicked = False
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
            if self.bg_highlighted:
                self.surface = self.selected_surface
            else:
                self.surface = self.back_surface

            self.is_double_clicked = Mouse.DOUBLE_CLICK[0]
            self.is_clicked = Mouse.DOWN[0]
        else:
            if self.bg_highlighted:
                self.surface = self.selected_surface
            else:
                self.surface = self.front_surface
            self.is_mouse_on = False
            self.is_clicked = False
            self.is_double_clicked = False

    def highlight_bg(self, mode: bool):
        self.bg_highlighted = mode



# a class that handle buttons with text
class TextButton(Button):
    def __init__(self, position: np.array, layer: int, _text: str, text_color, text_size: int,
                 bg_surface: pg.Surface = None, bbg_surface: pg.Surface = None, selected_surface: pg.Surface = None,
                 alpha: int = 255, alpha2: int = 70, position_offset=np.array([0, 0]),
                 font_type: str = 'Comic Sans MS', center_position: bool = True, static: bool = False):

        # creates the the text surface
        surface = pg.font.SysFont(font_type, text_size).render(_text, False, text_color)

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
        super(TextButton, self).__init__(bbg_surface, position, layer, alpha=alpha, alpha2=alpha2,
                                         selected_surface=selected_surface, back_surface=bg_surface,
                                         position_offset=position_offset, static=static, center_position=center_position)

    # edit the text
    def set_text(self, _text: str, text_color, text_size: int,
                 font_type: str = 'Comic Sans MS', center_position: bool = True):

        self.__init__(self.position, self.layer, _text, text_color, text_size,
                      position_offset=self.position_offset, font_type=font_type, center_position=center_position)

    # draws the TextButton
    def draw(self, surface: pg.Surface = None):
        if self.layer != Canvas.PaintedLayer:
            return
        super(TextButton, self).draw(surface=surface)