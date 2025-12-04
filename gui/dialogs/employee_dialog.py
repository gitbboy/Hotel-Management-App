# employee_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from models import Employee
from datetime import datetime
from exceptions import InvalidPersonDataError, PersonAlreadyExistsError


class EmployeeDialog:
    def __init__(self, parent, title, employee=None):
        self.parent = parent
        self.employee = employee
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.existing_positions = self._get_existing_positions()

        self.create_widgets()
        self.dialog.wait_window()

    def _get_existing_positions(self):
        try:
            employees = Employee.get_all()
            positions = set()
            for emp in employees:
                if self.employee and emp.id == self.employee.id:
                    continue
                positions.add(emp.get_position())
            return sorted(list(positions))
        except Exception as e:
            print(f"Ошибка при получении списка должностей: {e}")
            return []

    def create_widgets(self):
        # Основной фрейм для полей ввода
        fields_frame = tk.Frame(self.dialog)
        fields_frame.pack(pady=10, padx=20, fill='both')

        tk.Label(fields_frame, text="Фамилия:*").grid(row=0, column=0, sticky='w', pady=5)
        self.surname_entry = tk.Entry(fields_frame, width=25)
        self.surname_entry.grid(row=0, column=1, pady=5, padx=5, sticky='ew')

        tk.Label(fields_frame, text="Имя:*").grid(row=1, column=0, sticky='w', pady=5)
        self.name_entry = tk.Entry(fields_frame, width=25)
        self.name_entry.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        tk.Label(fields_frame, text="Отчество:").grid(row=2, column=0, sticky='w', pady=5)
        self.patronymic_entry = tk.Entry(fields_frame, width=25)
        self.patronymic_entry.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

        tk.Label(fields_frame, text="Должность:*").grid(row=3, column=0, sticky='w', pady=5)
        self.position_combobox = ttk.Combobox(fields_frame, width=23)
        self.position_combobox['values'] = self.existing_positions
        self.position_combobox.grid(row=3, column=1, pady=5, padx=5, sticky='ew')
        self.position_combobox.configure(state='normal')

        tk.Label(fields_frame, text="Телефон:*").grid(row=5, column=0, sticky='w', pady=5)
        self.phone_entry = tk.Entry(fields_frame, width=25)
        self.phone_entry.grid(row=5, column=1, pady=5, padx=5, sticky='ew')

        tk.Label(fields_frame, text="Email:*").grid(row=6, column=0, sticky='w', pady=5)
        self.email_entry = tk.Entry(fields_frame, width=25)
        self.email_entry.grid(row=6, column=1, pady=5, padx=5, sticky='ew')

        tk.Label(fields_frame, text="Дата принятия:*").grid(row=7, column=0, sticky='w', pady=5)
        tk.Label(fields_frame, text="(ГГГГ-ММ-ДД)").grid(row=7, column=1, sticky='w', pady=5)
        self.date_entry = tk.Entry(fields_frame, width=25)
        self.date_entry.grid(row=8, column=0, columnspan=2, pady=5, padx=5, sticky='ew')

        fields_frame.columnconfigure(1, weight=1)

        if self.employee:
            self._fill_employee_data()
        else:
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Фрейм для кнопок
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Сохранить",
                  command=self.save_employee, width=15).pack(side='left', padx=10)
        tk.Button(buttons_frame, text="Отмена",
                  command=self.dialog.destroy, width=15).pack(side='left', padx=10)

        self.dialog.bind('<Return>', lambda event: self.save_employee())
        self.surname_entry.focus_set()

    def _fill_employee_data(self):
        """Заполняет поля данными сотрудника для редактирования"""
        self.surname_entry.insert(0, self.employee.get_surname())
        self.name_entry.insert(0, self.employee.get_name())
        self.patronymic_entry.insert(0, self.employee.get_patronymic() or "")

        current_position = self.employee.get_position()
        self.position_combobox.set(current_position)

        if current_position and current_position not in self.existing_positions:
            self.position_combobox['values'] = tuple(list(self.existing_positions) + [current_position])

        self.phone_entry.insert(0, self.employee.get_phone_num())
        self.email_entry.insert(0, self.employee.get_mail())
        self.date_entry.insert(0, self.employee.get_date_of_employment())

    def _validate_fields(self):
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        position = self.position_combobox.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        date_employed = self.date_entry.get().strip()
        patronymic = self.patronymic_entry.get().strip()

        if not all([name, surname, position, phone, email, date_employed]):
            raise InvalidPersonDataError("Все поля, кроме отчества, обязательны для заполнения")

        if len(name) < 2:
            raise InvalidPersonDataError("Имя не может быть короче двух символов")

        if not name.replace(' ', '').isalpha():
            raise InvalidPersonDataError("Имя может содержать только буквы и пробелы")

        if len(surname) < 2:
            raise InvalidPersonDataError("Фамилия не может быть короче двух символов")

        if not surname.replace(' ', '').isalpha():
            raise InvalidPersonDataError("Фамилия может содержать только буквы и пробелы")

        # Валидация должности
        if len(position) < 2:
            raise InvalidPersonDataError("Должность не может быть короче двух символов")

        if patronymic:
            if not patronymic.replace(' ', '').isalpha():
                raise InvalidPersonDataError("Отчество может содержать только буквы и пробелы")
        else:
            patronymic = ""

        if '@' not in email or '.' not in email:
            raise InvalidPersonDataError("Проверьте правильность ввода Email")

        if len(phone) < 5 or not any(c.isdigit() for c in phone):
            raise InvalidPersonDataError("Проверьте правильность ввода номера телефона")

        try:
            datetime.strptime(date_employed, "%Y-%m-%d")
        except ValueError:
            raise InvalidPersonDataError("Дата должна быть в формате ГГГГ-ММ-ДД")

        return {
            'name': name,
            'surname': surname,
            'position': position,
            'phone': phone,
            'email': email,
            'date_employed': date_employed,
            'patronymic': patronymic if patronymic else ""
        }

    def save_employee(self):
        try:
            validated_data = self._validate_fields()

            if self.employee:
                self._update_employee(validated_data)
            else:
                self._create_employee(validated_data)

            self.result = True
            self.dialog.destroy()

        except (InvalidPersonDataError, PersonAlreadyExistsError) as e:
            messagebox.showerror("Ошибка данных", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")

    def _create_employee(self, data):
        employee = Employee(
            name=data['name'],
            surname=data['surname'],
            position=data['position'],
            phone_num=data['phone'],
            mail=data['email'],
            date_of_employment=data['date_employed'],
            patronymic=data['patronymic']
        )
        employee.save()
        messagebox.showinfo("Успех", f"Сотрудник {employee.full_name()} добавлен!")

    def _update_employee(self, data):
        self.employee.set_name(data['name'])
        self.employee.set_surname(data['surname'])
        self.employee.set_patronymic(data['patronymic'])
        self.employee.set_position(data['position'])
        self.employee.set_phone_num(data['phone'])
        self.employee.set_mail(data['email'])
        self.employee.set_date_of_employment(data['date_employed'])

        self.employee.update()
        messagebox.showinfo("Успех", "Данные сотрудника обновлены!")

class DeleteEmployeeDialog:
    def __init__(self, parent, employee_name):
        self.parent = parent
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Подтверждение удаления")
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets(employee_name)
        self.dialog.wait_window()

    def create_widgets(self, employee_name):
        message_frame = tk.Frame(self.dialog)
        message_frame.pack(pady=20, padx=20, fill='both', expand=True)

        tk.Label(message_frame, text=f"Вы уверены, что хотите удалить сотрудника?",
                 wraplength=350).pack(pady=5)
        tk.Label(message_frame, text=f"«{employee_name}»",
                 font=('Arial', 10, 'bold'), wraplength=350).pack(pady=5)
        tk.Label(message_frame, text="Это действие нельзя отменить.",
                 fg='red', wraplength=350).pack(pady=5)

        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="Удалить",
                  command=self.confirm_delete, width=12, bg='#ff6b6b').pack(side='left', padx=10)
        tk.Button(buttons_frame, text="Отмена",
                  command=self.dialog.destroy, width=12).pack(side='left', padx=10)

    def confirm_delete(self):
        self.result = True
        self.dialog.destroy()