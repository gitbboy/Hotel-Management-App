import pandas as pd
from tkinter import filedialog, messagebox
import os
import sys
from models import Employee, Guest, HotelRoom, Booking


class ExportService:
    @staticmethod
    def export_to_excel():
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить отчет как"
            )

            if not file_path:
                return False

            data_sheets = ExportService._collect_data()

            if not data_sheets:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return False

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in data_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    ExportService._auto_adjust_columns(writer.sheets[sheet_name])

            messagebox.showinfo("Успех", f"Данные успешно экспортированы в файл:\n{file_path}")
            ExportService._ask_open_file(file_path)
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
            return False

    @staticmethod
    def export_single_sheet(dataframe, sheet_name="Отчет"):
        """Экспорт одного DataFrame в Excel файл"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить отчет как"
            )

            if not file_path:
                return False

            if dataframe.empty:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return False

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
                ExportService._auto_adjust_columns(writer.sheets[sheet_name])

            messagebox.showinfo("Успех", f"Данные успешно экспортированы в файл:\n{file_path}")
            ExportService._ask_open_file(file_path)
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
            return False

    @staticmethod
    def _collect_data():
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
                        'Статус': 'Свободен' if room.is_free() else 'Занят',
                        'Вместимость': room.get_capacity()
                    })
                data_sheets['Номера'] = pd.DataFrame(room_data)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось получить данные номеров: {str(e)}")

        # 3. Данные бронирований с информацией о гостях и номерах
        try:
            bookings = Booking.get_all()
            if bookings:
                booking_data = []
                for booking in bookings:
                    guest = Guest.get_by_id(booking.get_guest_id())
                    room = HotelRoom.get_by_id(booking.get_room_id())

                    booking_data.append({
                        'ID': booking.id,
                        'Гость': guest.full_name() if guest else 'Неизвестно',
                        'Номер': room.get_number() if room else 'Неизвестно',
                        'Тип_номера': room.get_type() if room else 'Неизвестно',
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
                        'Email': guest.get_mail(),
                        'Дата_регистрации': guest.get_registration_date()
                    })
                data_sheets['Гости'] = pd.DataFrame(guest_data)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось получить данные гостей: {str(e)}")

        return data_sheets

    @staticmethod
    def _auto_adjust_columns(worksheet):
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    @staticmethod
    def _ask_open_file(file_path):
        open_file = messagebox.askyesno("Открыть файл", "Хотите открыть полученный файл?")
        if open_file:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS, Linux
                    if sys.platform == 'darwin':
                        os.system(f'open "{file_path}"')
                    else:
                        os.system(f'xdg-open "{file_path}"')
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось открыть файл: {str(e)}")