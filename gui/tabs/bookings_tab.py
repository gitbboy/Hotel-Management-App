import tkinter as tk
from tkinter import ttk, messagebox
from models import Booking, Guest, HotelRoom
from gui.dialogs.booking_dialog import BookingDialog


class BookingsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.refresh_bookings()

    def create_widgets(self):
        # Создание Treeview для отображения бронирований
        self.bookings_tree = ttk.Treeview(self,
                                          columns=(
                                          'ID', 'GuestID', 'GuestName', 'RoomID', 'RoomNumber', 'CheckIn', 'CheckOut',
                                          'Status'),
                                          show='headings'
                                          )

        # Конфигурация колонок
        self.bookings_tree.column('ID', width=0, stretch=tk.NO)
        self.bookings_tree.column('GuestID', width=0, stretch=tk.NO)
        self.bookings_tree.column('GuestName', width=150, minwidth=120)
        self.bookings_tree.column('RoomID', width=0, stretch=tk.NO)
        self.bookings_tree.column('RoomNumber', width=80, minwidth=60)
        self.bookings_tree.column('CheckIn', width=100, minwidth=80)
        self.bookings_tree.column('CheckOut', width=100, minwidth=80)
        self.bookings_tree.column('Status', width=100, minwidth=80)

        self.bookings_tree.heading('ID', text='ID')
        self.bookings_tree.heading('GuestID', text='GuestID')
        self.bookings_tree.heading('GuestName', text='Гость')
        self.bookings_tree.heading('RoomID', text='RoomID')
        self.bookings_tree.heading('RoomNumber', text='Номер')
        self.bookings_tree.heading('CheckIn', text='Заезд')
        self.bookings_tree.heading('CheckOut', text='Выезд')
        self.bookings_tree.heading('Status', text='Статус')

        self.bookings_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Фрейм для кнопок
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Новое бронирование",
                   command=self.new_booking).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать",
                   command=self.edit_booking).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Зарегистрировать заезд",
                   command=self.check_in).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Зарегистрировать выезд",
                   command=self.check_out).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отменить бронь",
                   command=self.cancel_booking).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список",
                   command=self.refresh_bookings).pack(side='left', padx=5)

    def refresh_bookings(self):
        """Обновление списка бронирований"""
        try:
            # Очистка Treeview
            for item in self.bookings_tree.get_children():
                self.bookings_tree.delete(item)

            bookings = Booking.get_all()
            for booking in bookings:
                # Получаем информацию о госте и номере
                guest = Guest.get_by_id(booking.get_guest_id())
                room = HotelRoom.get_by_id(booking.get_room_id())

                guest_name = guest.full_name() if guest else "Неизвестно"
                room_number = room.get_number() if room else "Неизвестно"
                status = "Активно" if booking.get_is_active() else "Отменено"

                self.bookings_tree.insert('', 'end', values=(
                    booking.id,
                    booking.get_guest_id(),
                    guest_name,
                    booking.get_room_id(),
                    room_number,
                    booking.get_check_in_date(),
                    booking.get_check_out_date(),
                    status
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования: {str(e)}")

    def new_booking(self):
        """Создание нового бронирования"""
        dialog = BookingDialog(self, "Новое бронирование")
        if dialog.result:
            self.refresh_bookings()

    def edit_booking(self):
        """Редактирование выбранного бронирования"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для редактирования")
            return

        item = selected[0]
        booking_id = self.bookings_tree.item(item, 'values')[0]

        try:
            booking = Booking.get_by_id(booking_id)
            if not booking:
                messagebox.showerror("Ошибка", "Бронирование не найдено")
                return

            dialog = BookingDialog(self, "Редактирование бронирования", booking)
            if dialog.result:
                self.refresh_bookings()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные бронирования: {str(e)}")

    def check_in(self):
        """Регистрация заезда"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для регистрации заезда")
            return

        item = selected[0]
        booking_id = self.bookings_tree.item(item, 'values')[0]
        guest_name = self.bookings_tree.item(item, 'values')[2]

        try:
            booking = Booking.get_by_id(booking_id)
            if booking and booking.get_is_active():
                # Здесь можно добавить логику регистрации заезда
                # Например, пометить номер как занятый
                room = HotelRoom.get_by_id(booking.get_room_id())
                if room and room.is_free():
                    room.set_free(False)
                    room.update()

                messagebox.showinfo("Успех", f"Заезд гостя {guest_name} зарегистрирован")
                self.refresh_bookings()
            else:
                messagebox.showerror("Ошибка", "Бронирование неактивно или не найдено")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось зарегистрировать заезд: {str(e)}")

    def check_out(self):
        """Регистрация выезда"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для регистрации выезда")
            return

        item = selected[0]
        booking_id = self.bookings_tree.item(item, 'values')[0]
        guest_name = self.bookings_tree.item(item, 'values')[2]

        try:
            booking = Booking.get_by_id(booking_id)
            if booking and booking.get_is_active():
                # Пометить номер как свободный
                room = HotelRoom.get_by_id(booking.get_room_id())
                if room:
                    room.set_free(True)
                    room.update()

                # Деактивировать бронирование
                booking.set_is_active(False)
                booking.update()

                messagebox.showinfo("Успех", f"Выезд гостя {guest_name} зарегистрирован")
                self.refresh_bookings()
            else:
                messagebox.showerror("Ошибка", "Бронирование неактивно или не найдено")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось зарегистрировать выезд: {str(e)}")

    def cancel_booking(self):
        """Отмена бронирования"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для отмены")
            return

        item = selected[0]
        booking_id = self.bookings_tree.item(item, 'values')[0]
        guest_name = self.bookings_tree.item(item, 'values')[2]

        result = messagebox.askyesno("Подтверждение",
                                     f"Вы уверены, что хотите отменить бронирование для {guest_name}?")
        if result:
            try:
                booking = Booking.get_by_id(booking_id)
                if booking:
                    booking.set_is_active(False)
                    booking.update()

                    # Освободить номер если он был занят
                    room = HotelRoom.get_by_id(booking.get_room_id())
                    if room:
                        room.set_free(True)
                        room.update()

                    messagebox.showinfo("Успех", "Бронирование отменено")
                    self.refresh_bookings()
                else:
                    messagebox.showerror("Ошибка", "Бронирование не найдено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отменить бронирование: {str(e)}")