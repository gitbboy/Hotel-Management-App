from log_config import setup_logging
from gui.main_window import HotelApp
import tkinter as tk

def start_window():
    window = tk.Tk()
    app = HotelApp(window)
    window.mainloop()

setup_logging()
start_window()