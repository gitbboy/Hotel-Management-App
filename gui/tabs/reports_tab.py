import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from models import Employee, Guest, HotelRoom, Booking
from services.export_service import ExportService
from datetime import datetime, timedelta
import re

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
                   command=self.recovery_report, width=20).pack(side='left', padx=5)

        # Фрейм для фильтров
        self.filters_frame = ttk.Frame(self)
        self.filters_frame.pack(pady=5, fill='x')

        # TreeView для отображения отчета
        self.report_tree = ttk.Treeview(self, show='headings')
        self.report_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Нижняя панель с кнопками действий
        report_actions_frame = ttk.Frame(self)
        report_actions_frame.pack(pady=5)

        ttk.Button(report_actions_frame, text="Экспорт в Excel",
                   command=self.excel_report).pack(side='left', padx=5)
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
        periods = [
            ("За месяц", "month"),
            ("За квартал", "quarter"),
            ("За год", "year"),
            ("Произвольный", "custom")
        ]

        for text, value in periods:
            ttk.Radiobutton(period_frame, text=text,
                            variable=self.period_var, value=value).pack(side='left', padx=5)

        # Фрейм для произвольных дат
        self.custom_dates_frame = ttk.Frame(self.filters_frame)

        ttk.Label(self.custom_dates_frame, text="С:").pack(side='left', padx=5)
        self.start_date_entry = ttk.Entry(self.custom_dates_frame, width=12)
        self.start_date_entry.pack(side='left', padx=5)
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        ttk.Label(self.custom_dates_frame, text="По:").pack(side='left', padx=5)
        self.end_date_entry = ttk.Entry(self.custom_dates_frame, width=12)
        self.end_date_entry.pack(side='left', padx=5)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Подсказки для пользователя
        tip_frame = ttk.Frame(self.filters_frame)
        tip_frame.pack(pady=2)
        ttk.Label(tip_frame, text="Формат даты: ГГГГ-ММ-ДД", foreground="gray").pack()

        # Кнопка применения
        ttk.Button(self.filters_frame, text="Применить фильтры",
                   command=self.apply_filters).pack(pady=5)

        self.period_var.trace('w', self.toggle_custom_dates)
        self.toggle_custom_dates()  # Инициализация видимости

    def toggle_custom_dates(self, *args):
        """Показать/скрыть поля для произвольных дат"""
        if hasattr(self, 'custom_dates_frame'):
            if self.period_var.get() == "custom":
                self.custom_dates_frame.pack(pady=5)
            else:
                self.custom_dates_frame.pack_forget()

    def apply_filters(self):
        """Применение фильтров и обновление отчета"""
        if not self.current_report_type:
            return

        try:
            # Получаем диапазон дат перед обновлением отчета
            start_date, end_date = self.get_date_range()

            if self.current_report_type == "occupancy":
                self.update_occupancy_report(start_date, end_date)
            elif self.current_report_type == "financial":
                self.update_financial_report(start_date, end_date)
            elif self.current_report_type == "guests":
                self.update_guests_report(start_date, end_date)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка применения фильтров: {str(e)}")

    def get_date_range(self):
        """Получение диапазона дат на основе выбранного периода"""
        today = datetime.now().date()

        try:
            if self.period_var.get() == "month":
                # Первый день текущего месяца
                start_date = today.replace(day=1)
                end_date = today
            elif self.period_var.get() == "quarter":
                # Первый день текущего квартала
                quarter = (today.month - 1) // 3
                start_month = 3 * quarter + 1
                start_date = today.replace(month=start_month, day=1)
                end_date = today
            elif self.period_var.get() == "year":
                # Первый день текущего года
                start_date = today.replace(month=1, day=1)
                end_date = today
            else:  # custom
                start_str = self.start_date_entry.get()
                end_str = self.end_date_entry.get()

                if not start_str or not end_str:
                    raise ValueError("Даты не могут быть пустыми")

                date_pattern = r'^\d{4}-\d{2}-\d{2}$'
                if not re.match(date_pattern, start_str) or not re.match(date_pattern, end_str):
                    raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД")

                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

                # Валидация дат
                self.validate_date_range(start_date, end_date)

            return start_date, end_date

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат даты: {str(e)}")
            return today.replace(day=1), today

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return today.replace(day=1), today

    def validate_date_range(self, start_date, end_date):
        """Проверка корректности диапазона дат"""
        if start_date > end_date:
            raise ValueError("Начальная дата не может быть больше конечной")

        if start_date > datetime.now().date():
            raise ValueError("Начальная дата не может быть в будущем")

        if (end_date - start_date).days > 1825:
            raise ValueError("Период не может превышать 5 лет")

        return True

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

    def setup_treeview_columns(self, columns_config):
        """Универсальная настройка колонок Treeview"""
        columns = [col[0] for col in columns_config]
        self.report_tree['columns'] = columns

        for col_id, heading, width in columns_config:
            self.report_tree.column(col_id, width=width, minwidth=width - 20)
            self.report_tree.heading(col_id, text=heading)

    def occupancy_report(self):
        """Отчет по занятости номеров"""
        self.clear_report()
        self.current_report_type = "occupancy"
        self.setup_date_filters()

        # Настройка колонок
        columns_config = [
            ('room_number', 'Номер', 100),
            ('room_type', 'Тип', 120),
            ('total_days', 'Всего дней', 100),
            ('occupied_days', 'Занято дней', 100),
            ('occupancy_rate', 'Загрузка %', 100),
            ('revenue', 'Доход', 100)
        ]

        self.setup_treeview_columns(columns_config)
        self.apply_filters()  # Автоматически применяем фильтры после настройки

    def update_occupancy_report(self, start_date, end_date):
        """Обновление отчета по занятости с фильтрами"""
        # Очищаем предыдущие данные
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        try:
            total_days = (end_date - start_date).days + 1
            if total_days <= 0:
                messagebox.showwarning("Предупреждение", "Некорректный период дат")
                return

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
            messagebox.showerror("Ошибка", f"Не удалось обновить отчет по занятости: {str(e)}")

    def financial_report(self):
        """Финансовый отчет"""
        self.clear_report()
        self.current_report_type = "financial"
        self.setup_date_filters()

        # Настройка колонок
        columns_config = [
            ('period', 'Период', 150),
            ('room_revenue', 'Доход от номеров', 120),
            ('avg_occupancy', 'Средняя загрузка %', 120),
            ('total_bookings', 'Всего бронирований', 120)
        ]

        self.setup_treeview_columns(columns_config)
        self.apply_filters()

    def update_financial_report(self, start_date, end_date):
        """Обновление финансового отчета с фильтрами"""
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        try:
            total_days = (end_date - start_date).days + 1
            if total_days <= 0:
                messagebox.showwarning("Предупреждение", "Некорректный период дат")
                return

            rooms = HotelRoom.get_all()
            bookings = Booking.get_all()

            # Общая статистика
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
                        total_occupied_days += overlap_days
                        completed_bookings += 1

            avg_occupancy = (total_occupied_days / total_possible_days * 100) if total_possible_days > 0 else 0

            period_label = f"{start_date} - {end_date}"

            self.report_tree.insert('', 'end', values=(
                period_label,
                f"{room_revenue:.2f}",
                f"{avg_occupancy:.1f}%",
                completed_bookings
            ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить финансовый отчет: {str(e)}")

    def guests_report(self):
        """Отчет по гостям"""
        self.clear_report()
        self.current_report_type = "guests"
        self.setup_date_filters()

        columns_config = [
            ('guest_name', 'Гость', 150),
            ('phone', 'Телефон', 120),
            ('total_bookings', 'Бронирований', 100),
            ('total_nights', 'Ночей всего', 100),
            ('last_booking', 'Последнее', 100),
            ('total_spent', 'Потрачено', 100)
        ]

        self.setup_treeview_columns(columns_config)
        self.apply_filters()

    def update_guests_report(self, start_date, end_date):
        """Обновление отчета по гостям с фильтрами"""
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        try:
            self.validate_date_range(start_date, end_date)

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
                    # Для last_booking_date смотрим все бронирования
                    booking_date = booking.get_check_in_date()
                    if not last_booking_date or booking_date > last_booking_date:
                        last_booking_date = booking_date

                    # Для ночей и денег - только те, что в периоде
                    if (self.dates_overlap(start_date, end_date,
                                           booking.get_check_in_date(),
                                           booking.get_check_out_date())):

                        nights = self.calculate_overlap_days(
                            start_date, end_date,
                            booking.get_check_in_date(),
                            booking.get_check_out_date()
                        )
                        total_nights += nights

                        room = HotelRoom.get_by_id(booking.get_room_id())
                        if room:
                            total_spent += nights * room.get_price()

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
            messagebox.showerror("Ошибка", f"Не удалось обновить отчет по гостям: {str(e)}")

    def staff_report(self):
        """Отчет по сотрудникам"""
        self.clear_report()
        self.current_report_type = "staff"
        self.clear_filters()

        columns_config = [
            ('employee_name', 'Сотрудник', 150),
            ('position', 'Должность', 120),
            ('phone', 'Телефон', 120),
            ('email', 'Email', 150),
            ('hire_date', 'Дата приема', 100),
            ('experience_months', 'Стаж (мес.)', 100)
        ]

        self.setup_treeview_columns(columns_config)

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

    @staticmethod
    def recovery_report():
        """Резервное копирование БД"""
        try:
            ExportService.extract_excel_all()
            messagebox.showinfo("Успех", "Резервное копирование выполнено успешно")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить резервное копирование: {str(e)}")

    def dates_overlap(self, start1, end1, start2, end2):
        """Проверка пересечения дат"""
        return start1 <= end2 and start2 <= end1

    def calculate_overlap_days(self, start1, end1, start2, end2):
        """Вычисление количества дней пересечения"""
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        return max(0, (overlap_end - overlap_start).days + 1)

    def excel_report(self):
        """Экспорт в Excel"""
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

            if not data:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return

            df = pd.DataFrame(data, columns=headers)

            # Определение имени листа на основе типа отчета
            sheet_names = {
                "occupancy": "Отчет по занятости",
                "financial": "Финансовый отчет",
                "guests": "Отчет по гостям",
                "staff": "Отчет по сотрудникам"
            }

            sheet_name = sheet_names.get(self.current_report_type, "Отчет")

            success = ExportService.export_single_sheet(df, sheet_name)

            if success:
                messagebox.showinfo("Успех", "Отчет успешно экспортирован в Excel")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать отчет: {str(e)}")

    def pdf_report(self):
        """Экспорт в PDF"""
        try:
            if not self.current_report_type:
                messagebox.showwarning("Предупреждение", "Сначала сгенерируйте отчет")
                return

            columns = self.report_tree['columns']
            if not columns:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return

            headers = [self.report_tree.heading(col)['text'] for col in columns]

            data = []
            for item in self.report_tree.get_children():
                values = self.report_tree.item(item)['values']
                data.append(values)

            if not data:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return

            df = pd.DataFrame(data, columns=headers)

            report_titles = {
                "occupancy": "Отчет по занятости номеров",
                "financial": "Финансовый отчет",
                "guests": "Отчет по гостям",
                "staff": "Отчет по сотрудникам"
            }

            report_title = report_titles.get(self.current_report_type, "Отчет")
            success = ExportService.export_single_sheet_to_pdf(df, report_title)

            if success:
                messagebox.showinfo("Успех", "Отчет успешно экспортирован в PDF")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать отчет в PDF: {str(e)}")