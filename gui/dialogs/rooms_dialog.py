import tkinter as tk
from tkinter import ttk, messagebox
from models import HotelRoom

class RoomDialog:
    def __init__(self, parent, title, room=None):
        self.parent = parent
        self.room = room
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        # Основной фрейм для полей ввода
        fields_frame = tk.Frame(self.dialog)
        fields_frame.pack(pady=10, padx=20, fill='both')

        # Номер комнаты
        tk.Label(fields_frame, text="Номер комнаты:*").grid(row=0, column=0, sticky='w', pady=5)
        self.number_entry = tk.Entry(fields_frame, width=25)
        self.number_entry.grid(row=0, column=1, pady=5, padx=5, sticky='ew')

        # Тип комнаты
        tk.Label(fields_frame, text="Тип комнаты:*").grid(row=1, column=0, sticky='w', pady=5)
        self.type_combobox = ttk.Combobox(fields_frame, width=23,
                                          values=["Стандарт", "Люкс", "Полулюкс", "Семейный", "Бизнес"])
        self.type_combobox.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        # Цена
        tk.Label(fields_frame, text="Цена за ночь:*").grid(row=2, column=0, sticky='w', pady=5)
        self.price_entry = tk.Entry(fields_frame, width=25)
        self.price_entry.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

        # Вместимость
        tk.Label(fields_frame, text="Вместимость:*").grid(row=3, column=0, sticky='w', pady=5)
        self.capacity_combobox = ttk.Combobox(fields_frame, width=23,
                                              values=["1", "2", "3", "4", "5"])
        self.capacity_combobox.grid(row=3, column=1, pady=5, padx=5, sticky='ew')

        # Статус (только для редактирования)
        if self.room:
            tk.Label(fields_frame, text="Статус:").grid(row=4, column=0, sticky='w', pady=5)
            self.status_var = tk.BooleanVar()
            self.status_check = ttk.Checkbutton(fields_frame, text="Свободен",
                                                variable=self.status_var)
            self.status_check.grid(row=4, column=1, pady=5, padx=5, sticky='w')

        fields_frame.columnconfigure(1, weight=1)

        if self.room:
            self._fill_room_data()

        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Сохранить",
                  command=self.save_room, width=15).pack(side='left', padx=10)
        tk.Button(buttons_frame, text="Отмена",
                  command=self.dialog.destroy, width=15).pack(side='left', padx=10)

        # Привязка события Enter для быстрого сохранения
        self.dialog.bind('<Return>', lambda event: self.save_room())

        # Фокус на первом поле
        self.number_entry.focus_set()

    def _fill_room_data(self):
        self.number_entry.insert(0, self.room.get_number())
        self.type_combobox.set(self.room.get_type())
        self.price_entry.insert(0, str(self.room.get_price()))
        self.capacity_combobox.set(str(self.room.get_capacity()))
        if hasattr(self, 'status_var'):
            self.status_var.set(self.room.is_free())

    def _validate_fields(self):
        number = self.number_entry.get().strip()
        room_type = self.type_combobox.get().strip()
        price = self.price_entry.get().strip()
        capacity = self.capacity_combobox.get().strip()

        # Проверка обязательных полей
        if not all([number, room_type, price, capacity]):
            raise ValueError("Все поля обязательны для заполнения")

        # Валидация номера
        if not number.isdigit():
            raise ValueError("Номер комнаты должен содержать только цифры")

        # Валидация цены
        try:
            price_value = float(price)
            if price_value <= 0:
                raise ValueError("Цена должна быть положительным числом")
        except ValueError:
            raise ValueError("Цена должна быть числом")

        # Валидация вместимости
        if not capacity.isdigit() or int(capacity) <= 0:
            raise ValueError("Вместимость должна быть положительным целым числом")

        return {
            'number': number,
            'type': room_type,
            'price': price_value,
            'capacity': int(capacity),
            'is_free': self.status_var.get() if hasattr(self, 'status_var') else True
        }

    def save_room(self):
        """Сохранение номера"""
        try:
            # Валидация данных
            validated_data = self._validate_fields()

            if self.room:
                # Обновление существующего номера
                self._update_room(validated_data)
            else:
                # Создание нового номера
                self._create_room(validated_data)

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _create_room(self, data):
        room = HotelRoom(
            room_id=data['number'],
            type=data['type'],
            price=data['price'],
            capacity=data['capacity'],
            is_free=data['is_free']
        )
        room.save()
        messagebox.showinfo("Успех", f"Номер {data['number']} добавлен!")

    def _update_room(self, data):
        """Обновление данных номера"""
        self.room.set_free(data['is_free'])
        # Для других полей нужны сеттеры - добавим их в класс HotelRoom
        # Временно используем прямой доступ или добавим сеттеры
        self.room._HotelRoom__room_id = data['number']
        self.room._HotelRoom__type = data['type']
        self.room._HotelRoom__price = data['price']
        self.room._HotelRoom__capacity = data['capacity']

        self.room.update()
        messagebox.showinfo("Успех", "Данные номера обновлены!")