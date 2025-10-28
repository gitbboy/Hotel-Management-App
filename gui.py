import tkinter as tk
from curses.ascii import isalpha
from tkinter import ttk, messagebox, filedialog
from models import Employee, Guest, HotelRoom, Booking, Hotel
from datetime import datetime
import pandas as pd
import os
import sys


class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_employees_tab()
        self.create_rooms_tab()
        self.create_bookings_tab()
        self.create_reports_tab()
        self.create_recovery_tab()
        self.refresh_employees()

    def create_employees_tab(self):
        self.employees_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employees_frame, text="Сотрудники")

        self.employees_tree = ttk.Treeview(self.employees_frame,
                                           columns=('ID', 'Name', 'Position', 'Phone', 'Mail', 'Date'),
                                           show='headings')

        self.employees_tree.column('ID', width=0, stretch=tk.NO)
        self.employees_tree.column('Name', width=150, minwidth=150)
        self.employees_tree.column('Position', width=120, minwidth=100)
        self.employees_tree.column('Phone', width=120, minwidth=100)
        self.employees_tree.column('Mail', width=150, minwidth=100)
        self.employees_tree.column('Date', width=120, minwidth=100)

        self.employees_tree.heading('ID', text='ID')
        self.employees_tree.heading('Name', text='ФИО')
        self.employees_tree.heading('Position', text='Должность')
        self.employees_tree.heading('Phone', text='Телефон')
        self.employees_tree.heading('Mail', text='Mail')
        self.employees_tree.heading('Date', text='Дата принятия')
        self.employees_tree.pack(fill='both', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.employees_frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Добавить сотрудника", command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.refresh_employees).pack(side='left', padx=5)

    def refresh_employees(self):
        try:
            for item in self.employees_tree.get_children():
                self.employees_tree.delete(item)

            employees = Employee.get_all()

            for emp in employees:
                self.employees_tree.insert('', 'end', values=(
                    emp.id,
                    emp.full_name(),
                    emp.get_position(),
                    emp.get_phone_num(),
                    emp.get_mail(),
                    emp.get_date_of_employment()

                ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сотрудников: {str(e)}")

    def add_employee(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление сотрудника")
        dialog.geometry("400x450")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Поля для ввода
        fields_frame = tk.Frame(dialog)
        fields_frame.pack(pady=10, padx=20, fill='both')

        tk.Label(fields_frame, text="Фамилия:").grid(row=0, column=0, sticky='w', pady=5)
        surname_entry = tk.Entry(fields_frame, width=20)
        surname_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Имя:").grid(row=1, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(fields_frame, width=20)
        name_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Отчество:").grid(row=2, column=0, sticky='w', pady=5)
        patronymic_entry = tk.Entry(fields_frame, width=20)
        patronymic_entry.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Должность:").grid(row=3, column=0, sticky='w', pady=5)
        position_entry = tk.Entry(fields_frame, width=20)
        position_entry.grid(row=3, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Телефон:").grid(row=4, column=0, sticky='w', pady=5)
        phone_entry = tk.Entry(fields_frame, width=20)
        phone_entry.grid(row=4, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Email:").grid(row=5, column=0, sticky='w', pady=5)
        email_entry = tk.Entry(fields_frame, width=20)
        email_entry.grid(row=5, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Дата принятия (ГГГГ-ММ-ДД):").grid(row=6, column=0, sticky='w', pady=5)
        date_entry = tk.Entry(fields_frame, width=20)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=6, column=1, pady=5, padx=5)

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Сохранить", command=lambda: self.save_employee(
            name_entry.get(),
            surname_entry.get(),
            position_entry.get(),
            phone_entry.get(),
            email_entry.get(),
            date_entry.get(),
            patronymic_entry.get(),
            dialog
        ), width=15).pack(side='left', padx=10)

        tk.Button(buttons_frame, text="Отмена", command=dialog.destroy, width=15).pack(side='left', padx=10)

    def save_employee(self, name, surname, position, phone, email, date_employed, patronymic, dialog):
        try:
            self.__validate_employee(name, surname, position, phone, email, date_employed, patronymic)

            employee = Employee(
                name=name,
                surname=surname,
                position=position,
                phone_num=phone,
                mail=email,
                date_of_employment=date_employed,
                patronymic=patronymic
            )
            employee.save()

            messagebox.showinfo("Успех", f"Сотрудник {employee.full_name()} добавлен!")
            dialog.destroy()
            self.refresh_employees()  # Обновляем список

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить сотрудника: {str(e)}")

    def edit_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для редактирования")
            return

        item = selected[0]
        employee_id = self.employees_tree.item(item, 'values')[0]

        try:
            employee = Employee.get_by_id(employee_id)
            if not employee:
                messagebox.showerror("Ошибка", "Сотрудник не найден")
                return

            self.open_edit_dialog(employee)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные сотрудника: {str(e)}")

    def open_edit_dialog(self, employee):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование сотрудника")
        dialog.geometry("400x450")
        dialog.transient(self.root)
        dialog.grab_set()

        fields_frame = tk.Frame(dialog)
        fields_frame.pack(pady=10, padx=20, fill='both')

        tk.Label(fields_frame, text="Фамилия:").grid(row=0, column=0, sticky='w', pady=5)
        surname_entry = tk.Entry(fields_frame, width=30)
        surname_entry.insert(0, employee.get_surname())
        surname_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Имя:").grid(row=1, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(fields_frame, width=30)
        name_entry.insert(0, employee.get_name())
        name_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Отчество:").grid(row=2, column=0, sticky='w', pady=5)
        patronymic_entry = tk.Entry(fields_frame, width=30)
        patronymic_entry.insert(0, employee.get_patronymic())
        patronymic_entry.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Должность:").grid(row=3, column=0, sticky='w', pady=5)
        position_entry = tk.Entry(fields_frame, width=30)
        position_entry.insert(0, employee.get_position())
        position_entry.grid(row=3, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Телефон:").grid(row=4, column=0, sticky='w', pady=5)
        phone_entry = tk.Entry(fields_frame, width=30)
        phone_entry.insert(0, employee.get_phone_num())
        phone_entry.grid(row=4, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Email:").grid(row=5, column=0, sticky='w', pady=5)
        email_entry = tk.Entry(fields_frame, width=30)
        email_entry.insert(0, employee.get_mail())
        email_entry.grid(row=5, column=1, pady=5, padx=5)

        tk.Label(fields_frame, text="Дата принятия (ГГГГ-ММ-ДД):").grid(row=6, column=0, sticky='w', pady=5)
        date_entry = tk.Entry(fields_frame, width=30)
        date_entry.insert(0, employee.get_date_of_employment())
        date_entry.grid(row=6, column=1, pady=5, padx=5)

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Сохранить", command=lambda: self.update_employee(
            employee,
            name_entry.get(),
            surname_entry.get(),
            position_entry.get(),
            phone_entry.get(),
            email_entry.get(),
            date_entry.get(),
            patronymic_entry.get(),
            dialog
        ), width=15).pack(side='left', padx=10)

        tk.Button(buttons_frame, text="Отмена", command=dialog.destroy, width=15).pack(side='left', padx=10)

    def update_employee(self, employee, name, surname, position, phone, email, date_employed, patronymic, dialog):
        try:

            self.__validate_employee(name, surname, position, phone, email, date_employed, patronymic)

            employee.set_name(name)
            employee.set_surname(surname)
            employee.set_patronymic(patronymic)
            employee.set_position(position)
            employee.set_phone_num(phone)
            employee.set_mail(email)
            employee.set_date_of_employment(date_employed)

            # Сохраняем изменения
            employee.update()

            messagebox.showinfo("Успех", "Данные сотрудника обновлены!")
            dialog.destroy()
            self.refresh_employees()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {str(e)}")

    def delete_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return

        item = selected[0]
        employee_id = self.employees_tree.item(item, 'values')[0]
        employee_name = self.employees_tree.item(item, 'values')[1]

        result = messagebox.askyesno("Подтверждение",
                                     f"Вы уверены, что хотите удалить сотрудника {employee_name}?")
        if result:
            try:
                employee = Employee.get_by_id(employee_id)
                if employee:
                    employee.delete()
                    messagebox.showinfo("Успех", "Сотрудник удален")
                    self.refresh_employees()
                else:
                    messagebox.showerror("Ошибка", "Сотрудник не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить сотрудника: {str(e)}")

    def create_rooms_tab(self):
        self.rooms_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rooms_frame, text="Номера")

        self.rooms_tree = ttk.Treeview(self.rooms_frame, columns=('Number', 'Type', 'Price', 'Status', 'Capacity'),
                                       show='headings')
        self.rooms_tree.heading('Number', text='Номер')
        self.rooms_tree.heading('Type', text='Тип')
        self.rooms_tree.heading('Price', text='Цена/ночь')
        self.rooms_tree.heading('Status', text='Статус')
        self.rooms_tree.heading('Capacity', text='Вместимость')
        self.rooms_tree.pack(fill='both', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.rooms_frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Добавить номер", command=self.add_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.refresh_rooms).pack(side='left', padx=5)

    def create_bookings_tab(self):
        self.bookings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bookings_frame, text="Бронирования")

        self.bookings_tree = ttk.Treeview(self.bookings_frame,
                                          columns=('ID', 'Guest', 'Room', 'CheckIn', 'CheckOut', 'Status'),
                                          show='headings')
        self.bookings_tree.heading('ID', text='ID брони')
        self.bookings_tree.heading('Guest', text='Гость')
        self.bookings_tree.heading('Room', text='Номер')
        self.bookings_tree.heading('CheckIn', text='Заезд')
        self.bookings_tree.heading('CheckOut', text='Выезд')
        self.bookings_tree.heading('Status', text='Статус')
        self.bookings_tree.pack(fill='both', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.bookings_frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Новое бронирование", command=self.new_booking).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Зарегистрировать заезд", command=self.check_in).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Зарегистрировать выезд", command=self.check_out).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отменить бронь", command=self.cancel_booking).pack(side='left', padx=5)

    def create_reports_tab(self):
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Отчеты")

        reports_btn_frame = ttk.Frame(self.reports_frame)
        reports_btn_frame.pack(pady=10)

        ttk.Button(reports_btn_frame, text="Отчет по занятости", command=self.occupancy_report, width=20).pack(
            side='top', pady=5)
        ttk.Button(reports_btn_frame, text="Финансовый отчет", command=self.financial_report, width=20).pack(side='top',
                                                                                                             pady=5)
        ttk.Button(reports_btn_frame, text="Отчет по гостям", command=self.guests_report, width=20).pack(side='top',
                                                                                                         pady=5)
        ttk.Button(reports_btn_frame, text="Отчет по сотрудникам", command=self.staff_report, width=20).pack(side='top',
                                                                                                             pady=5)

        self.report_tree = ttk.Treeview(self.reports_frame, show='headings')
        self.report_tree.pack(fill='both', expand=True, padx=5, pady=5)

        report_actions_frame = ttk.Frame(self.reports_frame)
        report_actions_frame.pack(pady=5)

        ttk.Button(report_actions_frame, text="Экспорт в Excel", command=self.export_report).pack(side='left', padx=5)
        ttk.Button(report_actions_frame, text="Экспорт в PDF", command=self.PDF_report).pack(side='left', padx=5)
        ttk.Button(report_actions_frame, text="Очистить", command=self.clear_report).pack(side='left', padx=5)

    def create_recovery_tab(self):
        self.management_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.management_frame, text="Резервное копирование базы данных")

        ttk.Button(self.management_frame, text="Импортировать данные в Excel", command=self.export_report, width=25).pack(pady=8)
        ttk.Button(self.management_frame, text="Импортировать данные в CSV", command=self.CSV_report, width=25).pack(pady=8)
        ttk.Button(self.management_frame, text="Импортировать данные в PDF", command=self.PDF_report, width=25).pack(pady=8)


    def __validate_employee(self, name, surname, position, phone, email, date_employed, patronymic):
        if not all([name, surname, position, phone, email, date_employed]):
            raise ValueError("Все поля, кроме отчества, обязательны для заполнения")

        if len(name) < 2:
            raise ValueError("Имя не может быть короче двух символов")

        if len(surname) < 2:
            raise ValueError("Фамилия не может быть короче двух символов")

        if not name.isalpha() or not surname.isalpha():
            raise ValueError("Имя и фамилия могут содержать только буквы")

        if patronymic and not patronymic.isalpha():
            raise ValueError("Отчество может содержать только буквы")

        if '@' not in email or '.' not in email:
            raise ValueError("Проверьте правильность ввода Email")

        if len(phone) < 2 or not phone[1:].isdigit():
            raise ValueError("Проверьте правильность ввода номера телефона")

        return True

    # заглушки
    def add_room(self):
        messagebox.showinfo("Информация", "Метод add_room() будет реализован позже")

    def edit_room(self):
        messagebox.showinfo("Информация", "Метод edit_room() будет реализован позже")

    def delete_room(self):
        messagebox.showinfo("Информация", "Метод delete_room() будет реализован позже")

    def refresh_rooms(self):
        messagebox.showinfo("Информация", "Метод refresh_rooms() будет реализован позже")

    def new_booking(self):
        messagebox.showinfo("Информация", "Метод new_booking() будет реализован позже")

    def check_in(self):
        messagebox.showinfo("Информация", "Метод check_in() будет реализован позже")

    def check_out(self):
        messagebox.showinfo("Информация", "Метод check_out() будет реализован позже")

    def cancel_booking(self):
        messagebox.showinfo("Информация", "Метод cancel_booking() будет реализован позже")

    def occupancy_report(self):
        messagebox.showinfo("Информация", "Метод occupancy_report() будет реализован позже")

    def financial_report(self):
        messagebox.showinfo("Информация", "Метод financial_report() будет реализован позже")

    def guests_report(self):
        messagebox.showinfo("Информация", "Метод guests_report() будет реализован позже")

    def staff_report(self):
        messagebox.showinfo("Информация", "Метод staff_report() будет реализован позже")

    def export_report(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить отчет как"
            )

            if not file_path:  # Отмена
                return

            data_sheets = {}

            # 1. Данные сотрудников
            try:
                employees = Employee.get_all()
                if employees:
                    emp_data = []
                    for emp in employees:
                        emp_data.append({
                            'ID': emp.id,
                            'Фамилия': emp.get_surname(),
                            'Имя': emp.get_name(),
                            'Отчество': emp.get_patronymic(),
                            'Должность': emp.get_position(),
                            'Телефон': emp.get_phone_num(),
                            'Email': emp.get_mail(),
                            'Дата принятия': emp.get_date_of_employment()
                        })
                    data_sheets['Сотрудники'] = pd.DataFrame(emp_data)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось получить данные сотрудников: {str(e)}")

            # 2. Данные номеров
            try:
                rooms = HotelRoom.get_all()
                if rooms:
                     room_data = []
                     for room in rooms:
                         room_data.append({
                             'ID': room.id,
                             'Номер': room.get_number(),
                             'Тип': room.get_type(),
                             'Цена': room.get_price(),
                             'Статус': room.is_free(),
                             'Вместимость': room.get_capacity()
                         })
                     data_sheets['Номера'] = pd.DataFrame(room_data)
                pass
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось получить данные номеров: {str(e)}")

            # 3. Данные бронирований
            try:
                bookings = Booking.get_all()
                if bookings:
                    booking_data = []
                    for booking in bookings:
                        """ Получаем информацию о госте и номере по их ID
                        guest = Guest.get_by_id(booking.get_guest_id())  # Нужно реализовать
                        room = HotelRoom.get_by_id(booking.get_room_id())  # Нужно реализовать
                        """
                        booking_data.append({
                            'ID': booking.id,
                            'ID_Гостя': booking.get_guest_id(),
                            'ID_Номера': booking.get_room_id(),
                            'Дата_заезда': booking.get_check_in_date(),
                            'Дата_выезда': booking.get_check_out_date(),
                            'Статус': 'Активно' if booking.get_is_active() else 'Неактивно'

                        })
                    data_sheets['Бронирования'] = pd.DataFrame(booking_data)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось получить данные бронирований: {str(e)}")

            # 4. Данные гостей
            try:
                guests = Guest.get_all()
                if guests:
                     guest_data = []
                     for guest in guests:
                         guest_data.append({
                             'ID': guest.id,
                             'Фамилия': guest.get_surname(),
                             'Имя': guest.get_name(),
                             'Отчество': guest.get_patronymic(),
                             'Телефон': guest.get_phone_num(),
                         })
                     data_sheets['Гости'] = pd.DataFrame(guest_data)
                pass
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось получить данные гостей: {str(e)}")

            if not data_sheets:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in data_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    worksheet = writer.sheets[sheet_name]

                    # Автоподбор
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = (max_length + 2)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo("Успех", f"Данные успешно экспортированы в файл:\n{file_path}")

            open_file = messagebox.askyesno("Открыть файл", "Хотите открыть полученный файл?")
            if open_file:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS, Linux
                    os.system(f'open "{file_path}"' if sys.platform == 'darwin' else f'xdg-open "{file_path}"')

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def PDF_report(self):
        messagebox.showinfo("Информация", "Метод PDF_report() будет реализован позже")

    def CSV_report(self):
        messagebox.showinfo("Информация", "Метод CSV_report() будет реализован позже")

    def clear_report(self):
        messagebox.showinfo("Информация", "Метод clear_report() будет реализован позже")

    def search_guest(self):
        messagebox.showinfo("Информация", "Метод search_guest() будет реализован позже")

    def booking_history(self):
        messagebox.showinfo("Информация", "Метод booking_history() будет реализован позже")

    def hotel_stats(self):
        messagebox.showinfo("Информация", "Метод hotel_stats() будет реализован позже")

    def manage_services(self):
        messagebox.showinfo("Информация", "Метод manage_services() будет реализован позже")

    def occupancy_calendar(self):
        messagebox.showinfo("Информация", "Метод occupancy_calendar() будет реализован позже")

    def backup_data(self):
        messagebox.showinfo("Информация", "Метод backup_data() будет реализован позже")


if __name__ == "__main__":
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()