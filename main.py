import sys
import numpy as np
import mido
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QFontDatabase
from PySide6.QtCore import Qt
from subsnake.gui import MainWindow
from subsnake.audio import AudioEngine
from importlib import resources

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi

#get midi inputs & channels
input_list = mido.get_input_names()
midi_channels = np.arange(1, 17)

#init audio engine
engine = AudioEngine()

#instance app
app = QApplication(sys.argv)
window = MainWindow(engine)
window.setObjectName("main_window")
window.setMaximumWidth(1600)

#add midi inputs
if input_list is not None:
    window.midi_group.midi_select.addItems(input_list)

#assign midi channels
for channel in midi_channels:
    window.midi_group.channel_select.addItem(str(channel))

#start audio & assign midi input
window.engine.start_audio()

#load font (Dogica Pixel)
with resources.as_file(resources.files("subsnake").joinpath("gui/fonts/dogica/dogicapixel.ttf")) as font_file:
    font_id = QFontDatabase.addApplicationFont(str(font_file))
    if font_id == -1:
        print(f"error: could not load font file at {font_file}")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

with resources.as_file(resources.files("subsnake").joinpath("gui/fonts/dogica/dogicapixelbold.ttf")) as font_file:
    font_id = QFontDatabase.addApplicationFont(str(font_file))
    if font_id == -1:
        print(f"error: could not load font file at {font_file}")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

app.setApplicationName("subsnake")
app.setApplicationDisplayName("subsnake")
app.setDesktopFileName("subsnake")
light_tooltip = "QToolTip { background-color: #cc94f8; font-family: 'Dogica Pixel'; font-size: 12px; color: #1c0627; border: 1px solid white; border-radius: 3px;}"
app.setStyleSheet(light_tooltip)

#load icon
with resources.as_file(resources.files("subsnake").joinpath("images/icon.png")) as icon_path:
    path_str = str(icon_path)
    app_pixmap = QPixmap(path_str)
    app_icon = QIcon()
    app_icon.addPixmap(app_pixmap)
    for size in [16, 24, 32, 48, 64, 256]:
        smooth_pixmap = app_pixmap.scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        app_icon.addPixmap(smooth_pixmap)
    app.setWindowIcon(app_icon)
    window.setWindowIcon(app_icon)

#show window
window.show()

#autodetect theme
style_hints = app.styleHints()
if style_hints.colorScheme() == Qt.ColorScheme.Dark:
    window.toggle_dark.setChecked(True)
else:
    window.toggle_dark.setChecked(False)

#start app
app.exec()
