import tkinter as tk
from tkinter import ttk, messagebox
from models import Booking, Guest, HotelRoom
from datetime import datetime
from exceptions import (
    InvalidBookingDataError,
    BookingDateError,
    RoomNotAvailableError,
    PersonNotFoundError,
    InvalidPersonDataError
)


class BookingDialog:
    def __init__(self, parent, title, booking=None):
        self.parent = parent
        self.booking = booking
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.guests = Guest.get_all()
        self.rooms = HotelRoom.get_available_rooms()

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        # Основной фрейм для полей ввода
        fields_frame = tk.Frame(self.dialog)
        fields_frame.pack(pady=10, padx=20, fill='both')

        # Гость
        tk.Label(fields_frame, text="Гость:*").grid(row=0, column=0, sticky='w', pady=5)
        self.guest_combobox = ttk.Combobox(fields_frame, width=25)
        guest_names = [guest.full_name() for guest in self.guests]
        self.guest_combobox['values'] = guest_names
        self.guest_combobox.grid(row=0, column=1, pady=5, padx=5, sticky='ew')

        # Номер
        tk.Label(fields_frame, text="Номер:*").grid(row=1, column=0, sticky='w', pady=5)
        self.room_combobox = ttk.Combobox(fields_frame, width=25)
        room_numbers = [f"{room.get_number()} ({room.get_type()})" for room in self.rooms]
        self.room_combobox['values'] = room_numbers
        self.room_combobox.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        # Дата заезда
        tk.Label(fields_frame, text="Дата заезда:*").grid(row=2, column=0, sticky='w', pady=5)
        tk.Label(fields_frame, text="(ГГГГ-ММ-ДД)").grid(row=2, column=1, sticky='w', pady=5)
        self.checkin_entry = tk.Entry(fields_frame, width=25)
        self.checkin_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.checkin_entry.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky='ew')

        # Дата выезда
        tk.Label(fields_frame, text="Дата выезда:*").grid(row=4, column=0, sticky='w', pady=5)
        tk.Label(fields_frame, text="(ГГГГ-ММ-ДД)").grid(row=4, column=1, sticky='w', pady=5)
        self.checkout_entry = tk.Entry(fields_frame, width=25)
        tomorrow = datetime.now().replace(day=datetime.now().day + 1)
        self.checkout_entry.insert(0, tomorrow.strftime("%Y-%m-%d"))
        self.checkout_entry.grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky='ew')

        # Статус
        if self.booking:
            tk.Label(fields_frame, text="Статус:").grid(row=6, column=0, sticky='w', pady=5)
            self.status_var = tk.BooleanVar()
            self.status_check = ttk.Checkbutton(fields_frame, text="Активно",
                                                variable=self.status_var)
            self.status_check.grid(row=6, column=1, pady=5, padx=5, sticky='w')

        fields_frame.columnconfigure(1, weight=1)

        if self.booking:
            self._fill_booking_data()

        # Фрейм для кнопок
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Сохранить",
                  command=self.save_booking, width=15).pack(side='left', padx=10)
        tk.Button(buttons_frame, text="Отмена",
                  command=self.dialog.destroy, width=15).pack(side='left', padx=10)

        self.dialog.bind('<Return>', lambda event: self.save_booking())
        self.guest_combobox.focus_set()

    def _fill_booking_data(self):
        guest = Guest.get_by_id(self.booking.get_guest_id())
        room = HotelRoom.get_by_id(self.booking.get_room_id())

        if guest:
            self.guest_combobox.set(guest.full_name())
        if room:
            self.room_combobox.set(f"{room.get_number()} ({room.get_type()})")

        self.checkin_entry.delete(0, tk.END)
        self.checkin_entry.insert(0, str(self.booking.get_check_in_date()))

        self.checkout_entry.delete(0, tk.END)
        self.checkout_entry.insert(0, str(self.booking.get_check_out_date()))

        if hasattr(self, 'status_var'):
            self.status_var.set(self.booking.get_is_active())

    def _validate_fields(self):
        guest_name = self.guest_combobox.get().strip()
        room_info = self.room_combobox.get().strip()
        checkin = self.checkin_entry.get().strip()
        checkout = self.checkout_entry.get().strip()

        if not all([guest_name, room_info, checkin, checkout]):
            raise InvalidBookingDataError("Все поля обязательны для заполнения")

        # Поиск гостя
        guest = None
        for g in self.guests:
            if g.full_name() == guest_name:
                guest = g
                break

        if not guest:
            raise PersonNotFoundError(identifier=guest_name)

        room_number = room_info.split(' ')[0]
        room = None
        for r in self.rooms:
            if str(r.get_number()) == room_number:
                room = r
                break

        if not room:
            raise RoomNotAvailableError(room_number, "номер не найден или недоступен")

        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d").date()
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d").date()

            if checkin_date >= checkout_date:
                raise BookingDateError("Дата выезда должна быть позже даты заезда")

            if checkin_date < datetime.now().date():
                raise BookingDateError("Дата заезда не может быть в прошлом")

        except ValueError:
            raise InvalidBookingDataError("Даты должны быть в формате ГГГГ-ММ-ДД", "dates")

        return {
            'guest_id': guest.id,
            'room_id': room.id,
            'checkin': checkin_date,
            'checkout': checkout_date,
            'is_active': self.status_var.get() if hasattr(self, 'status_var') else True
        }

    def save_booking(self):
        try:
            validated_data = self._validate_fields()

            if self.booking:
                self._update_booking(validated_data)
            else:
                self._create_booking(validated_data)

            self.result = True
            self.dialog.destroy()

        except (InvalidBookingDataError, BookingDateError, RoomNotAvailableError, PersonNotFoundError) as e:
            messagebox.showerror("Ошибка данных", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")

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
        self.booking.set_check_in_date(data['checkin'])
        self.booking.set_check_out_date(data['checkout'])
        self.booking.set_is_active(data['is_active'])

        self.booking.update()
        messagebox.showinfo("Успех", "Данные бронирования обновлены!")