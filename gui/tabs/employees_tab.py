import tkinter as tk
from tkinter import ttk, messagebox
from models import Employee
from gui.dialogs.employee_dialog import EmployeeDialog


class EmployeesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        self.refresh_employees()

    def create_widgets(self):
        self.employees_tree = ttk.Treeview(self,
                                           columns=('ID', 'Name', 'Position', 'Phone', 'Mail', 'Date'),
                                           show='headings'
                                           )

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

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Добавить сотрудника",
                   command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать",
                   command=self.edit_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить",
                   command=self.delete_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список",
                   command=self.refresh_employees).pack(side='left', padx=5)

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
        dialog = EmployeeDialog(self, "Добавление сотрудника")
        if dialog.result:
            self.refresh_employees()

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

            dialog = EmployeeDialog(self, "Редактирование сотрудника", employee)
            if dialog.result:
                self.refresh_employees()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные сотрудника: {str(e)}")

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