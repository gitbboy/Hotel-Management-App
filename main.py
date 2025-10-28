from gui import HotelApp
from database import Database
import tkinter as tk

#from gui.main_window import HotelApp - будет реализован парсинг файла
db = Database()

def test_database_connection():
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ")

    try:
        result = db.fetch_one("SELECT NOW()")
        if result:
            print(f"Connection success. Время сервера: {result['NOW()']}")

            employees = db.fetch_all("SELECT * FROM employees")
            print("\nПервые 3 записи из БД (сотрудники)")
            for i in range(3):
                print(employees[i])

            return True
        else:
            print("Не удалось выполнить тестовый запрос")
            return False
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False

def start_window():
    window = tk.Tk()
    app = HotelApp(window)
    window.mainloop()

#test_database_connection() - тест подключения к БД
start_window()







