from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Set window background
Window.clearcolor = get_color_from_hex('#121212')

# Custom theme colors
THEME = {
    "primary": "#FF6D00",  # Deep Orange
    "primary_dark": "#E65100",
    "primary_light": "#FFD180",
    "accent": "#FF9800",   # Orange
    "background": "#121212",
    "surface": "#1E1E1E",
    "error": "#CF6679",
    "on_primary": "#000000",
    "on_background": "#FFFFFF",
    "on_surface": "#FFFFFF",
    "on_error": "#000000"
}