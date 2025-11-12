from database import Database
from exceptions import InvalidDataError


class Person:
    def __init__(self, name, surname, phone_num, patronymic="", id=None):
        if not name or not surname:
            raise InvalidDataError("Имя и фамилия обязательны")

        if not phone_num:
            raise InvalidDataError("Номер телефона обязателен")

        self.id = id
        self._name = name
        self._surname = surname
        self._patronymic = patronymic
        self._phone_num = phone_num

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    def get_surname(self):
        return self._surname

    def set_surname(self, new_surname):
        self._surname = new_surname

    def get_patronymic(self):
        return self._patronymic

    def set_patronymic(self, new_patronymic):
        self._patronymic = new_patronymic

    def get_phone_num(self):
        return self._phone_num

    def set_phone_num(self, value):
        if not value:
            raise InvalidDataError("Номер телефона не может быть пустым")
        self._phone_num = value

    def full_name(self):
        return f"{self._surname} {self._name} {self._patronymic}".strip()

    """Абстрактные методы для переопределения в дочерних классах"""
    def save(self):
        raise NotImplementedError("Метод save должен быть реализован в дочернем классе")

    def update(self):
        raise NotImplementedError("Метод update должен быть реализован в дочернем классе")

    def delete(self):
        raise NotImplementedError("Метод delete должен быть реализован в дочернем классе")

    @classmethod
    def get_by_id(cls, id):
        raise NotImplementedError("Метод get_by_id должен быть реализован в дочернем классе")


class Employee(Person):
    def __init__(self, name, surname, position, phone_num, mail, date_of_employment, patronymic="", id=None):
        super().__init__(name, surname, phone_num, patronymic, id)

        if not position:
            raise InvalidDataError("Должность обязательна")

        if not mail or "@" not in mail:
            raise InvalidDataError("Некорректный email")

        if not date_of_employment:
            raise InvalidDataError("Дата приема на работу обязательна")

        self.__position = position
        self.__mail = mail
        self.__date_of_employment = date_of_employment

    def get_date_of_employment(self):
        return self.__date_of_employment

    def set_date_of_employment(self, value):
        self.__date_of_employment = value

    def set_mail(self, value):
        self.__mail = value

    def get_mail(self):
        return self.__mail

    def set_position(self, value):
        self.__position = value

    def get_position(self):
        return self.__position

    # Методы для работы с БД
    def save(self):
        db = Database()
        query = """INSERT INTO employees 
                   (name, surname, patronymic, phone_num, position, mail, date_of_employment) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (self._name, self._surname, self._patronymic, self._phone_num,
                  self.__position, self.__mail, self.__date_of_employment)
        db.execute_query(query, params)

    def update(self):
        if self.id is None:
            raise ValueError("Нельзя обновить запись без ID")

        db = Database()
        query = """UPDATE employees SET 
                   name=%s, surname=%s, patronymic=%s, phone_num=%s, 
                   position=%s, mail=%s, date_of_employment=%s 
                   WHERE id=%s"""
        params = (self._name, self._surname, self._patronymic, self._phone_num,
                  self.__position, self.__mail, self.__date_of_employment, self.id)
        db.execute_query(query, params)

    def delete(self):
        if self.id is None:
            raise ValueError("Нельзя удалить запись без ID")

        db = Database()
        query = "DELETE FROM employees WHERE id=%s"
        db.execute_query(query, (self.id,))

    @classmethod
    def get_by_id(cls, id):
        db = Database()
        query = "SELECT * FROM employees WHERE id=%s"
        result = db.fetch_one(query, (id,))

        if result:
            return cls(
                name=result['name'],
                surname=result['surname'],
                position=result['position'],
                phone_num=result['phone_num'],
                mail=result['mail'],
                date_of_employment=result['date_of_employment'],  # исправлено
                patronymic=result['patronymic'],
                id=result['id']
            )
        return None

    @classmethod
    def get_all(cls):
        db = Database()
        query = "SELECT * FROM employees"
        results = db.fetch_all(query)

        employees = []
        for result in results:
            employees.append(cls(
                name=result['name'],
                surname=result['surname'],
                position=result['position'],
                phone_num=result['phone_num'],
                mail=result['mail'],
                date_of_employment=result['date_of_employment'],
                patronymic=result['patronymic'],
                id=result['id']
            ))
        return employees


class Guest(Person):
    def __init__(self, name, surname, phone_num, passport_data, patronymic="", id=None):
        super().__init__(name, surname, phone_num, patronymic, id)

        if not passport_data:
            raise InvalidDataError("Паспортные данные обязательны")

        self.__passport_data = passport_data

    def get_passport_data(self):
        return self.__passport_data

    def set_passport_data(self, value):
        self.__passport_data = value

    def save(self):
        db = Database()
        query = """INSERT INTO guests 
                   (name, surname, patronymic, phone_num, passport_data) 
                   VALUES (%s, %s, %s, %s, %s)"""
        params = (self._name, self._surname, self._patronymic,
                  self._phone_num, self.__passport_data)
        db.execute_query(query, params)

    def update(self):
        if self.id is None:
            raise ValueError("Нельзя обновить запись без ID")

        db = Database()
        query = """UPDATE guests SET 
                   name=%s, surname=%s, patronymic=%s, phone_num=%s, passport_data=%s 
                   WHERE id=%s"""
        params = (self._name, self._surname, self._patronymic,
                  self._phone_num, self.__passport_data, self.id)
        db.execute_query(query, params)

    def delete(self):
        if self.id is None:
            raise ValueError("Нельзя удалить запись без ID")

        db = Database()
        query = "DELETE FROM guests WHERE id=%s"
        db.execute_query(query, (self.id,))

    @classmethod
    def get_by_id(cls, id):
        db = Database()
        query = "SELECT * FROM guests WHERE id=%s"
        result = db.fetch_one(query, (id,))

        if result:
            return cls(
                name=result['name'],
                surname=result['surname'],
                phone_num=result['phone_num'],
                passport_data=result['passport_data'],
                patronymic=result['patronymic'],
                id=result['id']
            )
        return None

    @classmethod
    def get_all(cls):
        db = Database()
        query = "SELECT * FROM guests"
        results = db.fetch_all(query)

        guests = []
        for result in results:
            guests.append(cls(
                name=result['name'],
                surname=result['surname'],
                phone_num=result['phone_num'],
                passport_data=result['passport_data'],
                patronymic=result['patronymic'],
                id=result['id']
            ))
        return guests