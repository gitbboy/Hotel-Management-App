import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox, filedialog
from models import Employee, Guest, HotelRoom, Booking
from services.export_service import ExportService
from datetime import datetime, timedelta
import sys, os


class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_report_type = None
        self.create_widgets()

    def create_widgets(self):
        reports_btn_frame = ttk.Frame(self)
        reports_btn_frame.pack(pady=10, fill='x')

        ttk.Button(reports_btn_frame, text="Отчет по занятости",
                   command=self.occupancy_report, width=20).pack(side='left', padx=5)
        ttk.Button(reports_btn_frame, text="Финансовый отчет",
                   command=self.financial_report, width=20).pack(side='left', padx=5)
        ttk.Button(reports_btn_frame, text="Отчет по гостям",
                   command=self.guests_report, width=20).pack(side='left', padx=5)
        ttk.Button(reports_btn_frame, text="Отчет по сотрудникам",
                   command=self.staff_report, width=20).pack(side='left', padx=5)
        ttk.Button(reports_btn_frame, text="Резервное копирование БД",
                   command=self.export_report, width=20).pack(side='left', padx=5)

        # Фрейм для фильтров (будет показываться для некоторых отчетов)
        self.filters_frame = ttk.Frame(self)
        self.filters_frame.pack(pady=5, fill='x')

        # TreeView для отображения отчета
        self.report_tree = ttk.Treeview(self, show='headings')
        self.report_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Нижняя панель с кнопками действий
        report_actions_frame = ttk.Frame(self)
        report_actions_frame.pack(pady=5)

        ttk.Button(report_actions_frame, text="Экспорт в Excel",
                   command=self.export_report).pack(side='left', padx=5)
        ttk.Button(report_actions_frame, text="Экспорт в PDF",
                   command=self.pdf_report).pack(side='left', padx=5)
        ttk.Button(report_actions_frame, text="Очистить",
                   command=self.clear_report).pack(side='left', padx=5)

    def clear_filters(self):
        """Очистка фрейма фильтров"""
        for widget in self.filters_frame.winfo_children():
            widget.destroy()

    def setup_date_filters(self):
        """Настройка фильтров по дате"""
        self.clear_filters()

        # Период отчета
        period_frame = ttk.Frame(self.filters_frame)
        period_frame.pack(pady=5)

        ttk.Label(period_frame, text="Период отчета:").pack(side='left', padx=5)

        self.period_var = tk.StringVar(value="month")
        ttk.Radiobutton(period_frame, text="За месяц",
                        variable=self.period_var, value="month").pack(side='left', padx=5)
        ttk.Radiobutton(period_frame, text="За квартал",
                        variable=self.period_var, value="quarter").pack(side='left', padx=5)
        ttk.Radiobutton(period_frame, text="За год",
                        variable=self.period_var, value="year").pack(side='left', padx=5)
        ttk.Radiobutton(period_frame, text="Произвольный",
                        variable=self.period_var, value="custom").pack(side='left', padx=5)

        # Произвольные даты (скрыты по умолчанию)
        self.custom_dates_frame = ttk.Frame(self.filters_frame)

        ttk.Label(self.custom_dates_frame, text="С:").pack(side='left', padx=5)
        self.start_date_entry = ttk.Entry(self.custom_dates_frame, width=12)
        self.start_date_entry.pack(side='left', padx=5)
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        ttk.Label(self.custom_dates_frame, text="По:").pack(side='left', padx=5)
        self.end_date_entry = ttk.Entry(self.custom_dates_frame, width=12)
        self.end_date_entry.pack(side='left', padx=5)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка применения фильтров
        ttk.Button(self.filters_frame, text="Применить фильтры",
                   command=self.apply_filters).pack(pady=5)

        # Привязка события для показа/скрытия произвольных дат
        self.period_var.trace('w', self.toggle_custom_dates)

    def toggle_custom_dates(self, *args):
        """Показать/скрыть поля для произвольных дат"""
        if self.period_var.get() == "custom":
            self.custom_dates_frame.pack(pady=5)
        else:
            self.custom_dates_frame.pack_forget()

    def apply_filters(self):
        """Применение фильтров и обновление отчета"""
        if self.current_report_type == "occupancy":
            self.occupancy_report()
        elif self.current_report_type == "financial":
            self.financial_report()
        elif self.current_report_type == "guests":
            self.guests_report()
        elif self.current_report_type == "recover":
            self.recover_report()

    def get_date_range(self):
        """Получение диапазона дат на основе выбранного периода"""
        today = datetime.now().date()

        if self.period_var.get() == "month":
            start_date = today.replace(day=1)
            end_date = today
        elif self.period_var.get() == "quarter":
            quarter = (today.month - 1) // 3 + 1
            start_month = 3 * (quarter - 1) + 1
            start_date = today.replace(month=start_month, day=1)
            end_date = today
        elif self.period_var.get() == "year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:  # custom
            try:
                start_date = datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d").date()
                end_date = datetime.strptime(self.end_date_entry.get(), "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                return today.replace(day=1), today

        return start_date, end_date

    def clear_report(self):
        """Очистка отчета"""
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        # Очистка колонок
        for col in self.report_tree['columns']:
            self.report_tree.heading(col, text='')
        self.report_tree['columns'] = []

        self.clear_filters()
        self.current_report_type = None

    def occupancy_report(self):
        """Отчет по занятости номеров"""
        self.clear_report()
        self.current_report_type = "occupancy"  # УСТАНОВКА ТИПА ОТЧЕТА
        self.setup_date_filters()

        # Настройка колонок
        self.report_tree['columns'] = ('room_number', 'room_type', 'total_days', 'occupied_days',
                                       'occupancy_rate', 'revenue')

        self.report_tree.column('room_number', width=100, minwidth=80)
        self.report_tree.column('room_type', width=120, minwidth=100)
        self.report_tree.column('total_days', width=100, minwidth=80)
        self.report_tree.column('occupied_days', width=100, minwidth=80)
        self.report_tree.column('occupancy_rate', width=100, minwidth=80)
        self.report_tree.column('revenue', width=100, minwidth=80)

        self.report_tree.heading('room_number', text='Номер')
        self.report_tree.heading('room_type', text='Тип')
        self.report_tree.heading('total_days', text='Всего дней')
        self.report_tree.heading('occupied_days', text='Занято дней')
        self.report_tree.heading('occupancy_rate', text='Загрузка %')
        self.report_tree.heading('revenue', text='Доход')

        try:
            start_date, end_date = self.get_date_range()
            total_days = (end_date - start_date).days + 1

            rooms = HotelRoom.get_all()
            bookings = Booking.get_all()

            for room in rooms:
                # Подсчет занятых дней для комнаты
                occupied_days = 0
                room_revenue = 0

                for booking in bookings:
                    if (booking.get_room_id() == room.id and
                            booking.get_is_active() and
                            self.dates_overlap(start_date, end_date,
                                               booking.get_check_in_date(),
                                               booking.get_check_out_date())):
                        overlap_days = self.calculate_overlap_days(
                            start_date, end_date,
                            booking.get_check_in_date(),
                            booking.get_check_out_date()
                        )
                        occupied_days += overlap_days
                        room_revenue += overlap_days * room.get_price()

                occupancy_rate = (occupied_days / total_days * 100) if total_days > 0 else 0

                self.report_tree.insert('', 'end', values=(
                    room.get_number(),
                    room.get_type(),
                    total_days,
                    occupied_days,
                    f"{occupancy_rate:.1f}%",
                    f"{room_revenue:.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать отчет по занятости: {str(e)}")

    def financial_report(self):
        """Финансовый отчет"""
        self.clear_report()
        self.current_report_type = "financial"  # УСТАНОВКА ТИПА ОТЧЕТА
        self.setup_date_filters()

        # Настройка колонок
        self.report_tree['columns'] = ('period', 'total_revenue', 'room_revenue',
                                       'avg_occupancy', 'total_bookings')

        self.report_tree.column('period', width=150, minwidth=120)
        self.report_tree.column('total_revenue', width=120, minwidth=100)
        self.report_tree.column('room_revenue', width=120, minwidth=100)
        self.report_tree.column('avg_occupancy', width=120, minwidth=100)
        self.report_tree.column('total_bookings', width=120, minwidth=100)

        self.report_tree.heading('period', text='Период')
        self.report_tree.heading('total_revenue', text='Общий доход')
        self.report_tree.heading('room_revenue', text='Доход от номеров')
        self.report_tree.heading('avg_occupancy', text='Средняя загрузка %')
        self.report_tree.heading('total_bookings', text='Всего бронирований')

        try:
            start_date, end_date = self.get_date_range()
            total_days = (end_date - start_date).days + 1

            rooms = HotelRoom.get_all()
            bookings = Booking.get_all()

            # Общая статистика
            total_revenue = 0
            room_revenue = 0
            total_occupied_days = 0
            total_possible_days = len(rooms) * total_days
            completed_bookings = 0

            for booking in bookings:
                booking_start = booking.get_check_in_date()
                booking_end = booking.get_check_out_date()

                if (booking.get_is_active() and
                        self.dates_overlap(start_date, end_date, booking_start, booking_end)):

                    overlap_days = self.calculate_overlap_days(
                        start_date, end_date, booking_start, booking_end
                    )

                    room = HotelRoom.get_by_id(booking.get_room_id())
                    if room:
                        booking_revenue = overlap_days * room.get_price()
                        room_revenue += booking_revenue
                        total_revenue += booking_revenue
                        total_occupied_days += overlap_days
                        completed_bookings += 1

            avg_occupancy = (total_occupied_days / total_possible_days * 100) if total_possible_days > 0 else 0

            period_label = f"{start_date} - {end_date}"

            self.report_tree.insert('', 'end', values=(
                period_label,
                f"{total_revenue:.2f}",
                f"{room_revenue:.2f}",
                f"{avg_occupancy:.1f}%",
                completed_bookings
            ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать финансовый отчет: {str(e)}")

    def guests_report(self):
        """Отчет по гостям"""
        self.clear_report()
        self.current_report_type = "guests"  # УСТАНОВКА ТИПА ОТЧЕТА
        self.setup_date_filters()

        # Настройка колонок
        self.report_tree['columns'] = ('guest_name', 'phone', 'total_bookings',
                                       'total_nights', 'last_booking', 'total_spent')

        self.report_tree.column('guest_name', width=150, minwidth=120)
        self.report_tree.column('phone', width=120, minwidth=100)
        self.report_tree.column('total_bookings', width=100, minwidth=80)
        self.report_tree.column('total_nights', width=100, minwidth=80)
        self.report_tree.column('last_booking', width=100, minwidth=80)
        self.report_tree.column('total_spent', width=100, minwidth=80)

        self.report_tree.heading('guest_name', text='Гость')
        self.report_tree.heading('phone', text='Телефон')
        self.report_tree.heading('total_bookings', text='Бронирований')
        self.report_tree.heading('total_nights', text='Ночей всего')
        self.report_tree.heading('last_booking', text='Последнее')
        self.report_tree.heading('total_spent', text='Потрачено')

        try:
            start_date, end_date = self.get_date_range()

            guests = Guest.get_all()
            bookings = Booking.get_all()

            for guest in guests:
                guest_bookings = [b for b in bookings if b.get_guest_id() == guest.id]

                if not guest_bookings:
                    continue

                # Статистика по бронированиям гостя
                total_bookings = len(guest_bookings)
                total_nights = 0
                total_spent = 0
                last_booking_date = None

                for booking in guest_bookings:
                    if (self.dates_overlap(start_date, end_date,
                                           booking.get_check_in_date(),
                                           booking.get_check_out_date())):

                        nights = (booking.get_check_out_date() - booking.get_check_in_date()).days
                        total_nights += nights

                        room = HotelRoom.get_by_id(booking.get_room_id())
                        if room:
                            total_spent += nights * room.get_price()

                        if not last_booking_date or booking.get_check_in_date() > last_booking_date:
                            last_booking_date = booking.get_check_in_date()

                last_booking_str = last_booking_date.strftime("%d.%m.%Y") if last_booking_date else "Нет"

                self.report_tree.insert('', 'end', values=(
                    guest.full_name(),
                    guest.get_phone_num(),
                    total_bookings,
                    total_nights,
                    last_booking_str,
                    f"{total_spent:.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать отчет по гостям: {str(e)}")

    def recover_report(self):
        self.clear_report()
        self.current_report_type = "recover"  # УСТАНОВКА ТИПА ОТЧЕТА
        self.clear_filters()  # Для этого отчета фильтры не нужны

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

    def staff_report(self):
        """Отчет по сотрудникам"""
        self.clear_report()
        self.current_report_type = "staff"  # УСТАНОВКА ТИПА ОТЧЕТА
        self.clear_filters()  # Для этого отчета фильтры не нужны

        # Настройка колонок
        self.report_tree['columns'] = ('employee_name', 'position', 'phone', 'email',
                                       'hire_date', 'experience_months')

        self.report_tree.column('employee_name', width=150, minwidth=120)
        self.report_tree.column('position', width=120, minwidth=100)
        self.report_tree.column('phone', width=120, minwidth=100)
        self.report_tree.column('email', width=150, minwidth=120)
        self.report_tree.column('hire_date', width=100, minwidth=80)
        self.report_tree.column('experience_months', width=100, minwidth=80)

        self.report_tree.heading('employee_name', text='Сотрудник')
        self.report_tree.heading('position', text='Должность')
        self.report_tree.heading('phone', text='Телефон')
        self.report_tree.heading('email', text='Email')
        self.report_tree.heading('hire_date', text='Дата приема')
        self.report_tree.heading('experience_months', text='Стаж (мес.)')

        try:
            employees = Employee.get_all()
            current_date = datetime.now().date()

            for emp in employees:
                hire_date = emp.get_date_of_employment()
                if isinstance(hire_date, str):
                    hire_date = datetime.strptime(hire_date, "%Y-%m-%d").date()

                experience_months = (current_date.year - hire_date.year) * 12 + (current_date.month - hire_date.month)

                self.report_tree.insert('', 'end', values=(
                    emp.full_name(),
                    emp.get_position(),
                    emp.get_phone_num(),
                    emp.get_mail(),
                    hire_date.strftime("%d.%m.%Y"),
                    experience_months
                ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать отчет по сотрудникам: {str(e)}")

    def dates_overlap(self, start1, end1, start2, end2):
        """Проверка пересечения дат"""
        return start1 <= end2 and start2 <= end1

    def calculate_overlap_days(self, start1, end1, start2, end2):
        """Вычисление количества дней пересечения"""
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        return max(0, (overlap_end - overlap_start).days + 1)

    def export_report(self):
        """Экспорт текущего отчета в Excel"""
        try:
            if not self.current_report_type:
                messagebox.showwarning("Предупреждение", "Сначала сгенерируйте отчет")
                return

            # Сбор данных из TreeView
            columns = self.report_tree['columns']
            if not columns:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return

            # Получение заголовков
            headers = [self.report_tree.heading(col)['text'] for col in columns]

            # Получение данных
            data = []
            for item in self.report_tree.get_children():
                values = self.report_tree.item(item)['values']
                data.append(values)

            # Создание DataFrame
            import pandas as pd
            df = pd.DataFrame(data, columns=headers)

            # Определение имени листа на основе типа отчета
            sheet_names = {
                "occupancy": "Отчет по занятости",
                "financial": "Финансовый отчет",
                "guests": "Отчет по гостям",
                "staff": "Отчет по сотрудникам"
            }

            sheet_name = sheet_names.get(self.current_report_type, "Отчет")

            # Экспорт
            success = ExportService.export_single_sheet(df, sheet_name)

            if success:
                messagebox.showinfo("Успех", "Отчет успешно экспортирован в Excel")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать отчет: {str(e)}")

    def pdf_report(self):
        """Экспорт в PDF (заглушка)"""
        messagebox.showinfo("Информация", "Экспорт в PDF будет реализован в будущей версии")