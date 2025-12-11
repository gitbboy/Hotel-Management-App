import tkinter as tk
from tkinter import ttk, messagebox
from models import HotelRoom
from exceptions import InvalidDataError, RoomNotFoundError


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

        self.dialog.bind('<Return>', lambda event: self.save_room())
        self.number_entry.focus_set()

    def _fill_room_data(self):
        self.number_entry.insert(0, self.room.get_number())
        self.type_combobox.set(self.room.get_type())
        self.price_entry.insert(0, str(self.room.get_price()))
        self.capacity_combobox.set(str(self.room.get_capacity()))
        if hasattr(self, 'status_var'):
            self.status_var.set(self.room.is_free())

    def _validate_number_format(self, number):
        """Валидация формата номера комнаты"""
        if not number.isdigit():
            raise InvalidDataError("Номер комнаты должен содержать только цифры")

        if len(number) != 3:
            raise InvalidDataError("Номер комнаты должен состоять из 3 цифр")

        floor_number = int(number[0])
        if floor_number not in [1, 2, 3, 4, 5]:
            raise InvalidDataError("Номер комнаты должен начинаться с номера этажа (1-5)")

        room_number = int(number[1:])
        if room_number < 1 or room_number > 50:
            raise InvalidDataError("Номер комнаты на этаже должен быть от 01 до 50")

        return number

    def _check_room_unique(self, number):
        if not self.room:
            existing_rooms = HotelRoom.get_all()
            for room in existing_rooms:
                if room.get_number() == number:
                    raise InvalidDataError(f"Комната с номером {number} уже существует")

    def _validate_fields(self):
        number = self.number_entry.get().strip()
        room_type = self.type_combobox.get().strip()
        price = self.price_entry.get().strip()
        capacity = self.capacity_combobox.get().strip()

        # Проверка обязательных полей
        if not all([number, room_type, price, capacity]):
            raise InvalidDataError("Все поля обязательны для заполнения")

        # Валидация номера комнаты
        validated_number = self._validate_number_format(number)

        # Проверка уникальности
        self._check_room_unique(validated_number)

        # Валидация типа комнаты
        valid_types = ["Стандарт", "Люкс", "Полулюкс", "Семейный", "Бизнес"]
        if room_type not in valid_types:
            raise InvalidDataError(f"Тип комнаты должен быть одним из: {', '.join(valid_types)}")

        # Валидация цены
        try:
            price_value = float(price)
            if price_value <= 0:
                raise InvalidDataError("Цена должна быть положительным числом")
            if price_value > 100000:  # Максимальная цена 100 000 за ночь
                raise InvalidDataError("Цена не может превышать 100 000 за ночь")
        except ValueError:
            raise InvalidDataError("Цена должна быть числом")

        # Валидация вместимости
        if not capacity.isdigit() or int(capacity) <= 0:
            raise InvalidDataError("Вместимость должна быть положительным целым числом")

        capacity_value = int(capacity)
        if capacity_value > 5:
            raise InvalidDataError("Вместимость не может превышать 5 человек")

        return {
            'number': validated_number,
            'type': room_type,
            'price': price_value,
            'capacity': capacity_value,
            'is_free': self.status_var.get() if hasattr(self, 'status_var') else True
        }

    def save_room(self):
        """Сохранение номера с обработкой пользовательских исключений"""
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

        except InvalidDataError as e:
            # Показываем пользовательские ошибки валидации
            messagebox.showerror("Ошибка данных", str(e))
        except RoomNotFoundError as e:
            # Ошибка, если комната не найдена при обновлении
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            # Общие ошибки
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")

    def _create_room(self, data):
        """Создание новой комнаты"""
        try:
            room = HotelRoom(
                room_id=data['number'],
                type=data['type'],
                price=data['price'],
                capacity=data['capacity'],
                is_free=data['is_free']
            )
            room.save()
            messagebox.showinfo("Успех", f"Номер {data['number']} успешно добавлен!")
        except Exception as e:
            # Преобразуем общие исключения в пользовательские
            raise InvalidDataError(f"Ошибка при создании комнаты: {str(e)}")

    def _update_room(self, data):
        """Обновление данных номера"""
        try:
            self.room.set_free(data['is_free'])
            self.room._HotelRoom__room_id = data['number']

            self.room.set_type(data['type'])
            self.room.set_price(data['price'])
            self.room.set_capacity(data['capacity'])

            self.room.update()
            messagebox.showinfo("Успех", "Данные номера успешно обновлены!")
        except Exception as e:
            raise InvalidDataError(f"Ошибка при обновлении комнаты: {str(e)}")