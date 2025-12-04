from tkinter import ttk
from gui.tabs.employees_tab import EmployeesTab
from gui.tabs.rooms_tab import RoomsTab
from gui.tabs.bookings_tab import BookingsTab
from gui.tabs.reports_tab import ReportsTab

class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)


        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Инициализация вкладок
        self.employees_tab = EmployeesTab(self.notebook)
        self.rooms_tab = RoomsTab(self.notebook)
        self.bookings_tab = BookingsTab(self.notebook)
        self.reports_tab = ReportsTab(self.notebook)

        # Добавление вкладок
        self.notebook.add(self.employees_tab, text="Сотрудники")
        self.notebook.add(self.rooms_tab, text="Номера")
        self.notebook.add(self.bookings_tab, text="Бронирования")
        self.notebook.add(self.reports_tab, text="Отчеты")