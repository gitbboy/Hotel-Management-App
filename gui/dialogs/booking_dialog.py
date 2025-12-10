import tkinter as tk
from tkinter import ttk, messagebox
from models import Booking, Guest, HotelRoom
from datetime import datetime
from exceptions import (
    InvalidBookingDataError,
    BookingDateError,
    RoomNotAvailableError,
    PersonNotFoundError,
    BookingConflictError,
    InvalidDataError
)


class BookingDialog:
    def __init__(self, parent, title, booking=None):
        self.parent = parent
        self.booking = booking
        self.result = False
        self.new_guest_mode = False  # Флаг режима нового гостя

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.guests = Guest.get_all()
        self.rooms = HotelRoom.get_available_rooms()

        self.create_widgets()
        if not booking:
            self.refresh_guest_list()
        else:
            self.load_reservation_data()
        self.dialog.wait_window()

    def clear_guest_fields(self):
        """Очистить поля нового гостя"""
        self.name_entry.delete(0, tk.END)
        self.surname_entry.delete(0, tk.END)
        self.patronymic_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.passport_entry.delete(0, tk.END)

    def create_widgets(self):
        # Основной контейнер с прокруткой
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Фрейм для переключателя режима гостя
        guest_mode_frame = tk.Frame(self.scrollable_frame)
        guest_mode_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='ew')

        tk.Label(guest_mode_frame, text="Выберите гостя:").pack(side='left', padx=(0, 10))

        # Переключатель режима гостя
        self.guest_mode_var = tk.StringVar(value="existing")
        ttk.Radiobutton(guest_mode_frame, text="Из списка",
                        variable=self.guest_mode_var,
                        value="existing",
                        command=self.toggle_guest_mode).pack(side='left', padx=5)
        ttk.Radiobutton(guest_mode_frame, text="Новый гость",
                        variable=self.guest_mode_var,
                        value="new",
                        command=self.toggle_guest_mode).pack(side='left', padx=5)

        # Фрейм для существующего гостя
        self.existing_guest_frame = tk.Frame(self.scrollable_frame)
        self.existing_guest_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')

        tk.Label(self.existing_guest_frame, text="Гость:*").grid(row=0, column=0, sticky='w', pady=2)

        # Создаем фрейм для Combobox и кнопки обновления
        combo_frame = tk.Frame(self.existing_guest_frame)
        combo_frame.grid(row=0, column=1, pady=2, padx=5, sticky='ew')

        self.guest_combobox = ttk.Combobox(combo_frame, width=23)
        self.guest_combobox.grid(row=0, column=0, sticky='ew')

        # Кнопка обновления списка гостей
        refresh_btn = tk.Button(combo_frame, text="🔄", width=2,
                                command=self.refresh_guest_list,
                                font=("Arial", 8))
        refresh_btn.grid(row=0, column=1, padx=(5, 0))

        combo_frame.columnconfigure(0, weight=1)

        # Фрейм для нового гостя
        self.new_guest_frame = tk.Frame(self.scrollable_frame)
        self.new_guest_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')

        # Поля для нового гостя (согласно классу Guest)
        tk.Label(self.new_guest_frame, text="Имя:*").grid(row=0, column=0, sticky='w', pady=2)
        self.name_entry = tk.Entry(self.new_guest_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=2, padx=5, sticky='ew')

        tk.Label(self.new_guest_frame, text="Фамилия:*").grid(row=1, column=0, sticky='w', pady=2)
        self.surname_entry = tk.Entry(self.new_guest_frame, width=30)
        self.surname_entry.grid(row=1, column=1, pady=2, padx=5, sticky='ew')

        tk.Label(self.new_guest_frame, text="Отчество:").grid(row=2, column=0, sticky='w', pady=2)
        self.patronymic_entry = tk.Entry(self.new_guest_frame, width=30)
        self.patronymic_entry.grid(row=2, column=1, pady=2, padx=5, sticky='ew')

        tk.Label(self.new_guest_frame, text="Телефон:*").grid(row=3, column=0, sticky='w', pady=2)
        self.phone_entry = tk.Entry(self.new_guest_frame, width=30)
        self.phone_entry.grid(row=3, column=1, pady=2, padx=5, sticky='ew')

        tk.Label(self.new_guest_frame, text="Паспорт:*").grid(row=4, column=0, sticky='w', pady=2)
        self.passport_entry = tk.Entry(self.new_guest_frame, width=30)
        self.passport_entry.grid(row=4, column=1, pady=2, padx=5, sticky='ew')

        self.new_guest_frame.grid_remove()  # Скрываем фрейм нового гостя

        # Разделитель
        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(
            row=6, column=0, columnspan=2, pady=10, sticky='ew'
        )

        # Остальные поля бронирования
        row_offset = 7

        # Номер
        tk.Label(self.scrollable_frame, text="Номер:*").grid(
            row=row_offset, column=0, sticky='w', pady=5
        )
        self.room_combobox = ttk.Combobox(self.scrollable_frame, width=25)
        room_numbers = [f"{room.get_number()} ({room.get_type()})" for room in self.rooms]
        self.room_combobox['values'] = room_numbers
        self.room_combobox.grid(row=row_offset, column=1, pady=5, padx=5, sticky='ew')

        # Дата заезда
        tk.Label(self.scrollable_frame, text="Дата заезда:*").grid(
            row=row_offset + 1, column=0, sticky='w', pady=5
        )
        tk.Label(self.scrollable_frame, text="(ГГГГ-ММ-ДД)").grid(
            row=row_offset + 1, column=1, sticky='w', pady=5
        )
        self.checkin_entry = tk.Entry(self.scrollable_frame, width=25)
        self.checkin_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.checkin_entry.grid(
            row=row_offset + 2, column=0, columnspan=2, pady=5, padx=5, sticky='ew'
        )

        # Дата выезда
        tk.Label(self.scrollable_frame, text="Дата выезда:*").grid(
            row=row_offset + 3, column=0, sticky='w', pady=5
        )
        tk.Label(self.scrollable_frame, text="(ГГГГ-ММ-ДД)").grid(
            row=row_offset + 3, column=1, sticky='w', pady=5
        )
        self.checkout_entry = tk.Entry(self.scrollable_frame, width=25)
        tomorrow = datetime.now().replace(day=datetime.now().day + 1)
        self.checkout_entry.insert(0, tomorrow.strftime("%Y-%m-%d"))
        self.checkout_entry.grid(
            row=row_offset + 4, column=0, columnspan=2, pady=5, padx=5, sticky='ew'
        )

        # Статус
        if self.booking:
            tk.Label(self.scrollable_frame, text="Статус:").grid(
                row=row_offset + 5, column=0, sticky='w', pady=5
            )
            self.status_var = tk.BooleanVar()
            self.status_check = ttk.Checkbutton(
                self.scrollable_frame, text="Активно", variable=self.status_var
            )
            self.status_check.grid(row=row_offset + 5, column=1, pady=5, padx=5, sticky='w')

        self.scrollable_frame.columnconfigure(1, weight=1)

        # Фрейм для кнопок (вне скроллируемой области)
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="Сохранить",
                  command=self.save_booking, width=15).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Отмена",
                  command=self.dialog.destroy, width=15).pack(side='left', padx=5)

        self.dialog.bind('<Return>', lambda event: self.save_booking())
        if not self.booking:
            self.name_entry.focus_set()

    def toggle_guest_mode(self):
        """Переключение между режимами выбора гостя"""
        if self.guest_mode_var.get() == "existing":
            self.refresh_guest_list()
            self.existing_guest_frame.grid()
            self.new_guest_frame.grid_remove()
            self.guest_combobox.focus_set()
        else:
            self.existing_guest_frame.grid_remove()
            self.new_guest_frame.grid()
            self.name_entry.focus_set()

    def refresh_guest_list(self):
        """Обновить список гостей в Combobox"""
        try:
            self.guests = Guest.get_all()
            guest_names = [guest.full_name() for guest in self.guests]
            self.guest_combobox['values'] = guest_names

            # Если это редактирование бронирования и есть текущий гость, выбираем его
            if self.booking and self.guests:
                guest_id = self.booking.get_guest_id()
                current_guest = None
                for guest in self.guests:
                    if guest.id == guest_id:
                        current_guest = guest
                        break

                if current_guest:
                    self.guest_combobox.set(current_guest.full_name())
                elif guest_names:
                    # Если не нашли текущего гостя, выбираем первого
                    self.guest_combobox.set(guest_names[0])
            elif guest_names:
                # Для нового бронирования выбираем первого гостя
                self.guest_combobox.set(guest_names[0])
            else:
                self.guest_combobox.set('')

        except Exception as e:
            # Здесь может возникать BookingError с недостающим аргументом action
            # Преобразуем ошибку в более понятную
            error_msg = str(e)
            if "missing 1 required positional argument: 'action'" in error_msg:
                # Скорее всего, это ошибка из BookingError
                messagebox.showerror("Ошибка", "Ошибка при загрузке списка гостей. Проверьте файл exceptions.py")
            else:
                messagebox.showerror("Ошибка", f"Не удалось загрузить список гостей: {error_msg}")

    def load_reservation_data(self):
        """Загрузить данные бронирования для редактирования"""
        if not self.booking:
            return

        # СНАЧАЛА обновляем списки
        self.refresh_guest_list()

        # Затем загружаем гостя
        guest = Guest.get_by_id(self.booking.get_guest_id())
        if guest:
            full_name = guest.full_name()
            self.guest_combobox.set(full_name)

            # Заполняем поля нового гостя (на случай изменения)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, guest.get_name() or "")

            self.surname_entry.delete(0, tk.END)
            self.surname_entry.insert(0, guest.get_surname() or "")

            self.patronymic_entry.delete(0, tk.END)
            patronymic = guest.get_patronymic() or ""
            if patronymic in ["None", "null", "NULL"]:
                patronymic = ""
            self.patronymic_entry.insert(0, patronymic)

            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, guest.get_phone_num() or "")

            self.passport_entry.delete(0, tk.END)
            self.passport_entry.insert(0, guest.get_passport_data() or "")

        # Загружаем номер
        room = HotelRoom.get_by_id(self.booking.get_room_id())
        if room:
            self.room_combobox.set(f"{room.get_number()} ({room.get_type()})")

        # Загружаем даты
        self.checkin_entry.delete(0, tk.END)
        self.checkin_entry.insert(0, str(self.booking.get_check_in_date()))

        self.checkout_entry.delete(0, tk.END)
        self.checkout_entry.insert(0, str(self.booking.get_check_out_date()))

        # Загружаем статус
        if hasattr(self, 'status_var'):
            self.status_var.set(self.booking.get_is_active())

        # Загружаем гостя
        guest = Guest.get_by_id(self.booking.get_guest_id())
        if guest:
            self.guest_combobox.set(guest.full_name())
            self.name_entry.insert(0, guest.get_name())
            self.surname_entry.insert(0, guest.get_surname())
            self.patronymic_entry.insert(0, guest.get_patronymic() or "")
            self.phone_entry.insert(0, guest.get_phone_num() or "")
            self.passport_entry.insert(0, guest.get_passport_data() or "")

        # Загружаем номер
        room = HotelRoom.get_by_id(self.booking.get_room_id())
        if room:
            self.room_combobox.set(f"{room.get_number()} ({room.get_type()})")

        self.checkin_entry.delete(0, tk.END)
        self.checkin_entry.insert(0, str(self.booking.get_check_in_date()))

        self.checkout_entry.delete(0, tk.END)
        self.checkout_entry.insert(0, str(self.booking.get_check_out_date()))

        if hasattr(self, 'status_var'):
            self.status_var.set(self.booking.get_is_active())

    def _validate_guest_fields(self):
        """Валидация полей гостя"""
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        phone_num = self.phone_entry.get().strip()
        passport_data = self.passport_entry.get().strip()
        patronymic = self.patronymic_entry.get().strip()

        # Проверка обязательных полей
        if not all([name, surname, phone_num, passport_data]):
            raise InvalidBookingDataError("Все поля, кроме отчества, обязательны для заполнения")

        # Валидация имени
        if len(name) < 2:
            raise InvalidBookingDataError("Имя не может быть короче двух символов")

        if not name.replace(' ', '').isalpha():
            raise InvalidBookingDataError("Имя может содержать только буквы и пробелы")

        # Валидация фамилии
        if len(surname) < 2:
            raise InvalidBookingDataError("Фамилия не может быть короче двух символов")

        if not surname.replace(' ', '').isalpha():
            raise InvalidBookingDataError("Фамилия может содержать только буквы и пробелы")

        # Валидация отчества (если заполнено)
        if patronymic:
            if not patronymic.replace(' ', '').isalpha():
                raise InvalidBookingDataError("Отчество может содержать только буквы и пробелы")
        else:
            patronymic = ""

        # Валидация телефона
        if len(phone_num) < 5 or not any(c.isdigit() for c in phone_num):
            raise InvalidBookingDataError("Проверьте правильность ввода номера телефона")

        # Валидация паспортных данных
        if len(passport_data) < 5:
            raise InvalidBookingDataError("Паспортные данные должны содержать минимум 5 символов")

        """
        # Проверка уникальности паспортных данных
        for guest in self.guests:
            if guest.get_passport_data() == passport_data:
                raise InvalidBookingDataError("Гость с такими паспортными данными уже существует")

        # Проверка уникальности телефона
        for guest in self.guests:
            if guest.get_phone_num() == phone_num:
                raise InvalidBookingDataError("Гость с таким номером телефона уже существует")
        """
        return {
            'name': name,
            'surname': surname,
            'phone_num': phone_num,
            'passport_data': passport_data,
            'patronymic': patronymic if patronymic else ""
        }

    def _validate_fields(self):
        """Валидация полей формы"""
        # Проверка номера
        room_info = self.room_combobox.get().strip()
        checkin = self.checkin_entry.get().strip()
        checkout = self.checkout_entry.get().strip()

        if not all([room_info, checkin, checkout]):
            raise InvalidBookingDataError("Все поля обязательны для заполнения")

        # Поиск номера
        room_number = room_info.split(' ')[0]
        room = None
        for r in self.rooms:
            if str(r.get_number()) == room_number:
                room = r
                break

        if not room:
            raise RoomNotAvailableError(room_number, "Номер не найден или недоступен")

        # Проверка дат
        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d").date()
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d").date()

            if checkin_date >= checkout_date:
                raise BookingDateError("Дата выезда должна быть позже даты заезда")

            if checkin_date < datetime.now().date():
                raise BookingDateError("Дата заезда не может быть в прошлом")

        except ValueError:
            raise InvalidBookingDataError("Даты должны быть в формате ГГГГ-ММ-ДД", "dates")

        # Обработка гостя в зависимости от режима
        if self.guest_mode_var.get() == "existing":
            # Поиск существующего гостя
            guest_name = self.guest_combobox.get().strip()
            if not guest_name:
                raise InvalidBookingDataError("Выберите гостя из списка")

            self.guests = Guest.get_all()

            guest = None
            for g in self.guests:
                if g.full_name() == guest_name:
                    guest = g
                    break

            if not guest:
                raise PersonNotFoundError(identifier=guest_name)

            guest_id = guest.id
        else:
            # Валидация и создание нового гостя
            try:
                # Используем функцию валидации для гостя
                guest_data = self._validate_guest_fields()

                # ОБНОВЛЯЕМ список гостей перед проверкой
                self.guests = Guest.get_all()

                # Проверяем, существует ли уже такой гость (по паспорту или телефону)
                existing_guest = None
                for guest in self.guests:
                    if guest.get_passport_data() == guest_data['passport_data']:
                        existing_guest = guest
                        break
                    elif guest.get_phone_num() == guest_data['phone_num']:
                        existing_guest = guest
                        break

                if existing_guest:
                    guest_id = existing_guest.id
                    messagebox.showinfo("Информация", f"Гость {existing_guest.full_name()} уже существует в базе")
                else:
                    # Создаем нового гостя
                    guest = Guest(
                        name=guest_data['name'],
                        surname=guest_data['surname'],
                        phone_num=guest_data['phone_num'],
                        passport_data=guest_data['passport_data'],
                        patronymic=guest_data['patronymic']
                    )
                    guest.save()
                    guest_id = guest.id
                    messagebox.showinfo("Успех", f"Новый гость {guest.full_name()} добавлен в базу")

                    # Обновляем список гостей после создания
                    self.refresh_guest_list()

            except InvalidDataError as e:
                raise InvalidBookingDataError(f"Ошибка при создании гостя: {str(e)}")
            except Exception as e:
                raise InvalidBookingDataError(f"Ошибка при создании гостя: {str(e)}")

        return {
            'guest_id': guest_id,
            'room_id': room.id,
            'checkin': checkin_date,
            'checkout': checkout_date,
            'is_active': self.status_var.get() if hasattr(self, 'status_var') else True
        }

    def save_booking(self):
        try:
            self.guests = Guest.get_all()
            self.rooms = HotelRoom.get_available_rooms()

            validated_data = self._validate_fields()

            if self.booking:
                self._update_booking(validated_data)
            else:
                self._create_booking(validated_data)

            self.result = True
            self.dialog.destroy()

        except (InvalidBookingDataError, BookingDateError,
                RoomNotAvailableError, PersonNotFoundError, InvalidDataError) as e:
            messagebox.showerror("Ошибка данных", str(e))
        except Exception as e:
            error_msg = str(e)
            if "missing 1 required positional argument: 'action'" in error_msg:
                messagebox.showerror("Ошибка",
                                     "Ошибка в обработке данных. Проверьте конструктор BookingError в файле exceptions.py")
            else:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {error_msg}")

    def _create_booking(self, data):
        booking = Booking(
            guest_id=data['guest_id'],
            room_id=data['room_id'],
            check_in_date=data['checkin'],
            check_out_date=data['checkout'],
            is_active=data['is_active']
        )
        booking.save()

        # Пометить номер как занятый
        room = HotelRoom.get_by_id(data['room_id'])
        if room:
            room.set_free(False)
            room.update()

        messagebox.showinfo("Успех", "Бронирование создано!")

    def _update_booking(self, data):
        try:
            # Сохраняем старые значения для логирования
            old_guest_id = self.booking.get_guest_id()
            old_room_id = self.booking.get_room_id()

            # Обновляем базовые данные бронирования
            self.booking.set_check_in_date(data['checkin'])
            self.booking.set_check_out_date(data['checkout'])
            self.booking.set_is_active(data['is_active'])

            # Обновляем гостя если изменился
            if old_guest_id != data['guest_id']:
                self.booking.set_guest_id(data['guest_id'])

            # Обновляем комнату если изменилась (нужен метод set_room_id в Booking)
            if old_room_id != data['room_id']:
                self.booking.set_room_id(data['room_id'])

            self.booking.update()
            self.refresh_guest_list()
            messagebox.showinfo("Успех", "Данные бронирования обновлены!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить бронирование: {str(e)}")
            raise