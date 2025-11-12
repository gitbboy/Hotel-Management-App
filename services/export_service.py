from models import Employee, Guest, HotelRoom, Booking
from tkinter import filedialog, messagebox
import pandas as pd
import os
import sys

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


class ExportService:
    """Работы с Эксель"""
    @staticmethod
    def extract_excel_all():
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить отчет как"
            )

            if not file_path:
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

    @staticmethod
    def export_single_sheet(dataframe, sheet_name="Отчет"):
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

    """Работы с ПДФ"""
    @staticmethod
    def export_single_sheet_to_pdf(dataframe, title="Отчет"):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Сохранить отчет как PDF"
            )

            if not file_path:
                return False

            if dataframe.empty:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return False

            if not ExportService._register_fonts():
                return False

            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=18
            )

            elements = []
            # custom fonts styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName='NotoSans-Bold',
                fontSize=14,
                spaceAfter=20,
                alignment=1,
                textColor=colors.darkblue
            )

            date_style = ParagraphStyle(
                'CustomDate',
                parent=styles['Normal'],
                fontName='NotoSans',
                fontSize=9,
                spaceAfter=15,
                alignment=1,
                textColor=colors.grey
            )

            title_paragraph = Paragraph(title, title_style)
            elements.append(title_paragraph)

            date_paragraph = Paragraph(
                f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                date_style
            )
            elements.append(date_paragraph)

            elements.append(Spacer(1, 15))

            data = [dataframe.columns.tolist()]  # Заголовки
            data.extend(dataframe.values.tolist())  # Данные

            table = Table(data, repeatRows=1)

            table.setStyle(TableStyle([
                # titles
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'NotoSans-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

                # data
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            col_widths = ExportService._calculate_column_widths(data, doc.width)
            table._argW = col_widths

            elements.append(table)

            doc.build(elements)

            messagebox.showinfo("Успех", f"Отчет успешно экспортирован в PDF:\n{file_path}")
            ExportService._ask_open_file(file_path)
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать в PDF: {str(e)}")
            return False

    @staticmethod
    def _calculate_column_widths(data, available_width):
        num_cols = len(data[0])
        max_lengths = [0] * num_cols

        for row in data:
            for i, cell in enumerate(row):
                cell_length = len(str(cell))
                if cell_length > max_lengths[i]:
                    max_lengths[i] = cell_length

        total_max_length = sum(max_lengths)
        if total_max_length == 0:
            return [available_width / num_cols] * num_cols

        widths = []
        for max_len in max_lengths:
            width = (max_len / total_max_length) * available_width
            width = max(width, 60)
            width = min(width, 300)
            widths.append(width)

        return widths

    @staticmethod
    def _register_fonts():
        try:
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            fonts_dir = os.path.join(project_dir, 'fonts')

            regular_font_path = os.path.join(fonts_dir, 'NotoSans.ttf')
            bold_font_path = os.path.join(fonts_dir, 'NotoSansBld.ttf')

            # Проверяем существование шрифтов
            if not os.path.exists(regular_font_path):
                messagebox.showerror(
                    "Ошибка",
                    f"Шрифт NotoSans не найден: {regular_font_path}\n\n"
                    "Пожалуйста, поместите файлы NotoSans.ttf и NotoSansBld.ttf в папку fonts."
                )
                return False

            if not os.path.exists(bold_font_path):
                messagebox.showerror(
                    "Ошибка",
                    f"Жирный шрифт NotoSans не найден: {bold_font_path}\n\n"
                    "Пожалуйста, поместите файлы NotoSans.ttf и NotoSansBld.ttf в папку fonts."
                )
                return False

            # Регистрируем шрифты
            pdfmetrics.registerFont(TTFont('NotoSans', regular_font_path))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', bold_font_path))

            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось зарегистрировать шрифты: {str(e)}")
            return False
