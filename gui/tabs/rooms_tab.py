import tkinter as tk
from tkinter import ttk, messagebox
from models import HotelRoom
from gui.dialogs.rooms_dialog import RoomDialog

class RoomsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.refresh_rooms()

    def create_widgets(self):
        self.rooms_tree = ttk.Treeview(self,
                                       columns=('ID', 'Number', 'Type', 'Price', 'Capacity', 'Status'),
                                       show='headings'
                                       )

        self.rooms_tree.column('ID', width=0, stretch=tk.NO)
        self.rooms_tree.column('Number', width=100, minwidth=80)
        self.rooms_tree.column('Type', width=120, minwidth=100)
        self.rooms_tree.column('Price', width=100, minwidth=80)
        self.rooms_tree.column('Capacity', width=100, minwidth=80)
        self.rooms_tree.column('Status', width=100, minwidth=80)

        self.rooms_tree.heading('ID', text='ID')
        self.rooms_tree.heading('Number', text='Номер')
        self.rooms_tree.heading('Type', text='Тип')
        self.rooms_tree.heading('Price', text='Цена/ночь')
        self.rooms_tree.heading('Capacity', text='Вместимость')
        self.rooms_tree.heading('Status', text='Статус')

        self.rooms_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Фрейм для кнопок
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Добавить номер",
                   command=self.add_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать",
                   command=self.edit_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить",
                   command=self.delete_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список",
                   command=self.refresh_rooms).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Показать свободные",
                   command=self.show_available).pack(side='left', padx=5)

    def refresh_rooms(self):
        try:
            for item in self.rooms_tree.get_children():
                self.rooms_tree.delete(item)

            rooms = HotelRoom.get_all()
            for room in rooms:
                status = "Свободен" if room.is_free() else "Занят"
                self.rooms_tree.insert('', 'end', values=(
                    room.id,
                    room.get_number(),
                    room.get_type(),
                    f"{room.get_price():.2f}",
                    room.get_capacity(),
                    status
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить номера: {str(e)}")

    def show_available(self):
        try:
            for item in self.rooms_tree.get_children():
                self.rooms_tree.delete(item)

            rooms = HotelRoom.get_available_rooms()
            for room in rooms:
                self.rooms_tree.insert('', 'end', values=(
                    room.id,
                    room.get_number(),
                    room.get_type(),
                    f"{room.get_price():.2f}",
                    room.get_capacity(),
                    "Свободен"
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить свободные номера: {str(e)}")

    def add_room(self):
        """Добавление нового номера"""
        dialog = RoomDialog(self, "Добавление номера")
        if dialog.result:
            self.refresh_rooms()

    def edit_room(self):
        """Редактирование выбранного номера"""
        selected = self.rooms_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите номер для редактирования")
            return

        item = selected[0]
        room_id = self.rooms_tree.item(item, 'values')[0]

        try:
            room = HotelRoom.get_by_id(room_id)
            if not room:
                messagebox.showerror("Ошибка", "Номер не найден")
                return

            dialog = RoomDialog(self, "Редактирование номера", room)
            if dialog.result:
                self.refresh_rooms()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные номера: {str(e)}")

    def delete_room(self):
        """Удаление выбранного номера"""
        selected = self.rooms_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите номер для удаления")
            return

        item = selected[0]
        room_id = self.rooms_tree.item(item, 'values')[0]
        room_number = self.rooms_tree.item(item, 'values')[1]

        result = messagebox.askyesno("Подтверждение",
                                     f"Вы уверены, что хотите удалить номер {room_number}?")
        if result:
            try:
                room = HotelRoom.get_by_id(room_id)
                if room and room.is_free():
                    room.delete()
                    messagebox.showinfo("Успех", "Номер удален")
                    self.refresh_rooms()

                elif not room.is_free():
                    messagebox.showerror("Ошибка", "Нельзя удалить номер во время бронирования")

                else:
                    messagebox.showerror("Ошибка", "Номер не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить номер: {str(e)}")