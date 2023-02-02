import pygame as pg
import numpy as np

from UICore.canvas import Canvas


class Text(Canvas):  # a class that handle text
    def __init__(self, position: np.array, layer: int, _text: str, text_color, text_size: int,
                 position_offset=np.array([0, 0]), font_type: str = 'Comic Sans MS', center_position: bool = True):

        surface = pg.font.SysFont(font_type, text_size).render(_text, False, text_color).convert()

        # calls the Canvas's __init__
        super(Text, self).__init__(surface, position, layer,
                                   position_offset=position_offset, center_position=center_position)

    # edit the text
    def set_text(self, _text: str, text_color, text_size: int,
                 font_type: str = 'Comic Sans MS', center_position: bool = True):

        self.__init__(self.position, self.layer, _text, text_color, text_size,
                      position_offset=self.position_offset, font_type=font_type, center_position=center_position)

    # draws the Text
    def draw(self, surface: pg.Surface = None):
        if self.layer != Canvas.PaintedLayer:
            return
        super(Text, self).draw(surface=surface)