from PythonCore.image_to_lines import ImageToLines
from UI_heandler.main_UI import MainUI
from UI_heandler.Kcode_visual_reader import KcodeVisualReader
im2lines = ImageToLines("PythonCore/text.png")

UI = MainUI()
im2lines.get_k_code(raster_mode=True)
UI.raster_simulation = KcodeVisualReader(im2lines.Kcode_manager)
im2lines.get_k_code(raster_mode=False)
UI.circles_simulation = KcodeVisualReader(im2lines.Kcode_manager)
UI.start()
