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
# для многопоточной обработки экспорта
import threading
import queue


class ExportService:
    """Сервис для экспорта данных с поддержкой многопоточности"""

    # Очередь для коммуникации между потоками
    _result_queue = queue.Queue()

    @staticmethod
    def extract_excel_all_threaded():
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить резервную копию как"
            )

            if not file_path:
                return False, "Операция отменена пользователем"

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
                return False, f"Ошибка получения данных сотрудников: {str(e)}"

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
            except Exception as e:
                return False, f"Ошибка получения данных номеров: {str(e)}"

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
                return False, f"Ошибка получения данных бронирований: {str(e)}"

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
            except Exception as e:
                return False, f"Ошибка получения данных гостей: {str(e)}"

            if not data_sheets:
                return False, "Нет данных для экспорта"

            # Запись в файл
            try:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    for sheet_name, df in data_sheets.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        worksheet = writer.sheets[sheet_name]
                        ExportService._auto_adjust_columns(worksheet)
            except Exception as e:
                return False, f"Ошибка записи в файл: {str(e)}"

            return True, f"Резервная копия успешно создана:\n{file_path}"

        except Exception as e:
            return False, f"Неожиданная ошибка при экспорте: {str(e)}"

    @staticmethod
    def export_single_sheet_threaded(dataframe, sheet_name="Отчет"):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить отчет как XML"
            )

            if not file_path:
                return False, "Операция отменена пользователем", None

            if dataframe.empty:
                return False, "Нет данных для экспорта", None

            # Запись данных
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
                ExportService._auto_adjust_columns(writer.sheets[sheet_name])

            return True, f"Отчет успешно экспортирован в файл:\n{file_path}", file_path

        except PermissionError:
            return False, "Ошибка доступа к файлу. Закройте файл и попробуйте снова.", None
        except Exception as e:
            return False, f"Ошибка экспорта в Excel: {str(e)}", None

    @staticmethod
    def export_single_sheet_to_pdf_threaded(dataframe, title="Отчет"):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Сохранить отчет как PDF"
            )

            if not file_path:
                return False, "Операция отменена пользователем", None

            if dataframe.empty:
                return False, "Нет данных для экспорта", None

            if not ExportService._register_fonts():
                return False, "Не удалось загрузить шрифты для PDF экспорта", None

            # Создание PDF документа
            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=18
            )

            elements = []

            # Стили для PDF
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName='NotoSans-Bold',
                fontSize=16,
                spaceAfter=20,
                alignment=1,
                textColor=colors.HexColor('#2C3E50')
            )

            date_style = ParagraphStyle(
                'CustomDate',
                parent=styles['Normal'],
                fontName='NotoSans',
                fontSize=10,
                spaceAfter=20,
                alignment=1,
                textColor=colors.HexColor('#7F8C8D')
            )

            # Заголовок
            title_paragraph = Paragraph(title, title_style)
            elements.append(title_paragraph)

            # Дата генерации
            date_paragraph = Paragraph(
                f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y в %H:%M')}",
                date_style
            )
            elements.append(date_paragraph)

            elements.append(Spacer(1, 15))

            # Подготовка данных для таблицы
            data = [dataframe.columns.tolist()]
            data.extend(dataframe.values.tolist())

            # Создание таблицы
            table = Table(data, repeatRows=1)

            # Стили таблицы
            table_style = TableStyle([
                # Заголовки
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'NotoSans-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                # Данные
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ])

            table.setStyle(table_style)

            # Расчет ширины колонок
            col_widths = ExportService._calculate_column_widths(data, doc.width)
            table._argW = col_widths

            elements.append(table)

            # Генерация PDF
            doc.build(elements)

            return True, f"PDF отчет успешно создан:\n{file_path}", file_path

        except PermissionError:
            return False, "Ошибка доступа к файлу. Закройте файл и попробуйте снова.", None
        except Exception as e:
            return False, f"Ошибка создания PDF: {str(e)}", None

    # Статические методы для обратной совместимости
    @staticmethod
    def extract_excel_all():
        """Метод резервного копирования"""
        try:
            success, message = ExportService.extract_excel_all_threaded()
            if success:
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить резервное копирование: {str(e)}")

    @staticmethod
    def export_single_sheet(dataframe, sheet_name="Отчет"):
        """Метод экспорта в Excel"""
        try:
            success, message, file_path = ExportService.export_single_sheet_threaded(dataframe, sheet_name)
            if success:
                messagebox.showinfo("Успех", message)
                if file_path:
                    ExportService._ask_open_file(file_path)
                return True
            else:
                messagebox.showerror("Ошибка", message)
                return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
            return False

    @staticmethod
    def export_single_sheet_to_pdf(dataframe, title="Отчет"):
        """Метод экспорта в PDF"""
        try:
            success, message, file_path = ExportService.export_single_sheet_to_pdf_threaded(dataframe, title)
            if success:
                messagebox.showinfo("Успех", message)
                if file_path:
                    ExportService._ask_open_file(file_path)
                return True
            else:
                messagebox.showerror("Ошибка", message)
                return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать в PDF: {str(e)}")
            return False

    # Вспомогательные методы
    @staticmethod
    def _auto_adjust_columns(worksheet):
        """Автоподбор ширины колонок в Excel"""
        try:
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        cell_value = str(cell.value) if cell.value is not None else ""
                        if len(cell_value) > max_length:
                            max_length = len(cell_value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Максимальная ширина 50
                worksheet.column_dimensions[column_letter].width = adjusted_width
        except Exception as e:
            print(f"Warning: Could not adjust columns: {e}")

    @staticmethod
    def _calculate_column_widths(data, available_width):
        """Расчет ширины колонок для PDF таблицы"""
        try:
            num_cols = len(data[0])
            if num_cols == 0:
                return [available_width]

            max_lengths = [0] * num_cols

            for row in data:
                for i, cell in enumerate(row):
                    cell_length = len(str(cell)) if cell is not None else 0
                    if cell_length > max_lengths[i]:
                        max_lengths[i] = cell_length

            total_max_length = sum(max_lengths)
            if total_max_length == 0:
                return [available_width / num_cols] * num_cols

            widths = []
            for max_len in max_lengths:
                width = (max_len / total_max_length) * available_width
                width = max(width, 40)  # Минимальная ширина
                width = min(width, 200)  # Максимальная ширина
                widths.append(width)

            # Корректировка, если суммарная ширина превышает доступную
            total_width = sum(widths)
            if total_width > available_width:
                ratio = available_width / total_width
                widths = [w * ratio for w in widths]

            return widths
        except Exception:
            # В случае ошибки используем равномерное распределение
            num_cols = len(data[0]) if data else 1
            return [available_width / num_cols] * num_cols

    @staticmethod
    def _register_fonts():
        """Регистрация шрифтов для PDF"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            fonts_dir = os.path.join(project_dir, 'fonts')

            regular_font_path = os.path.join(fonts_dir, 'NotoSans.ttf')
            bold_font_path = os.path.join(fonts_dir, 'NotoSansBld.ttf')

            # Проверяем существование шрифтов
            if not os.path.exists(regular_font_path):
                # Пробуем альтернативные пути
                alternative_paths = [
                    os.path.join(os.getcwd(), 'fonts', 'NotoSans.ttf'),
                    os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'fonts', 'NotoSans.ttf')
                ]

                for path in alternative_paths:
                    if os.path.exists(path):
                        regular_font_path = path
                        bold_font_path = path.replace('NotoSans.ttf', 'NotoSansBld.ttf')
                        break
                else:
                    # Если шрифты не найдены, используем стандартные
                    print("Warning: Font files not found, using default fonts")
                    return True

            if not os.path.exists(bold_font_path):
                print("Warning: Bold font not found, using regular font for bold")
                bold_font_path = regular_font_path

            # Регистрируем шрифты
            pdfmetrics.registerFont(TTFont('NotoSans', regular_font_path))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', bold_font_path))

            return True

        except Exception as e:
            print(f"Warning: Could not register custom fonts: {e}")
            # Возвращаем True, чтобы использовать стандартные шрифты
            return True

    @staticmethod
    def _ask_open_file(file_path):
        """Запрос на открытие файла после экспорта"""
        try:
            if not os.path.exists(file_path):
                return

            open_file = messagebox.askyesno(
                "Открыть файл",
                "Хотите открыть полученный файл?"
            )

            if open_file:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS, Linux
                    if sys.platform == 'darwin':
                        os.system(f'open "{file_path}"')
                    else:
                        os.system(f'xdg-open "{file_path}"')
        except Exception as e:
            messagebox.showwarning(
                "Предупреждение",
                f"Не удалось открыть файл: {str(e)}"
            )

    # Методы для асинхронного выполнения
    @staticmethod
    def start_async_export(export_type, dataframe=None, sheet_name="Отчет", title="Отчет"):
        """ Запуск экспорта в отдельном потоке """

        def export_task():
            try:
                if export_type == "excel_backup":
                    result = ExportService.extract_excel_all_threaded()
                    ExportService._result_queue.put(("excel_backup", result))
                elif export_type == "excel_sheet":
                    result = ExportService.export_single_sheet_threaded(dataframe, sheet_name)
                    ExportService._result_queue.put(("excel_sheet", result))
                elif export_type == "pdf":
                    result = ExportService.export_single_sheet_to_pdf_threaded(dataframe, title)
                    ExportService._result_queue.put(("pdf", result))
            except Exception as e:
                ExportService._result_queue.put((export_type, (False, f"Ошибка в потоке: {str(e)}", None)))

        thread = threading.Thread(target=export_task, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def get_async_result():
        """Получение результата асинхронной операции """
        try:
            return ExportService._result_queue.get_nowait()
        except queue.Empty:
            return None

    @staticmethod
    def wait_for_async_completion(timeout=None):
        """Ожидание завершения асинхронной операции"""
        try:
            return ExportService._result_queue.get(timeout=timeout)
        except queue.Empty:
            return None