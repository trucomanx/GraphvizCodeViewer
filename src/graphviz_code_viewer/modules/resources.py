import sys
import os

# self.icon_path = resource_path("icons", "logo.png")

def resource_path(*parts):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        # sobe de modules → stock_viewer
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base, *parts)


