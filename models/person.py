from database import Database
from exceptions import InvalidDataError
from log_config import get_logger


class Person:
    def __init__(self, name, surname, phone_num, patronymic=" ", id=None):
        if not name or not surname:
            raise InvalidDataError("Имя и фамилия обязательны")

        if not phone_num:
            raise InvalidDataError("Номер телефона обязателен")

        self.logger = get_logger('person')
        self.id = id
        self._name = name
        self._surname = surname
        self._patronymic = patronymic
        self._phone_num = phone_num
        self.logger.debug(f"Создан объект Person: {self.full_name()}")

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self.logger.debug(f"Изменение имени с {self._name} на {new_name}")
        self._name = new_name

    def get_surname(self):
        return self._surname

    def set_surname(self, new_surname):
        self.logger.debug(f"Изменение фамилии с {self._surname} на {new_surname}")
        self._surname = new_surname

    def get_patronymic(self):
        return self._patronymic

    def set_patronymic(self, new_patronymic):
        self.logger.debug(f"Изменение отчества с {self._patronymic} на {new_patronymic}")
        self._patronymic = new_patronymic

    def get_phone_num(self):
        return self._phone_num

    def set_phone_num(self, value):
        if not value:
            raise InvalidDataError("Номер телефона не может быть пустым")
        self.logger.debug(f"Изменение телефона с {self._phone_num} на {value}")
        self._phone_num = value

    def full_name(self):
        return f"{self._surname} {self._name} {self._patronymic}".strip()

    """Абстрактные методы для переопределения в дочерних классах"""
    def save(self):
        self.logger.debug("Сохранение Person в БД")
        raise NotImplementedError("Метод save должен быть реализован в дочернем классе")

    def update(self):
        self.logger.debug("Обновление Person в БД")
        raise NotImplementedError("Метод update должен быть реализован в дочернем классе")

    def delete(self):
        self.logger.debug("Удаление Person из БД")
        raise NotImplementedError("Метод delete должен быть реализован в дочернем классе")

    @classmethod
    def get_by_id(cls, id):
        logger = get_logger('person')
        logger.debug(f"Поиск Person по ID: {id}")
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

        self.logger = get_logger('person.employee')
        self.__position = position
        self.__mail = mail
        self.__date_of_employment = date_of_employment
        self.logger.info(f"Создан сотрудник: {self.full_name()}, должность: {position}")

    def get_date_of_employment(self):
        return self.__date_of_employment

    def set_date_of_employment(self, value):
        self.logger.debug(f"Изменение даты трудоустройства на {value}")
        self.__date_of_employment = value

    def set_mail(self, value):
        self.logger.debug(f"Изменение email с {self.__mail} на {value}")
        self.__mail = value

    def get_mail(self):
        return self.__mail

    def set_position(self, value):
        self.logger.debug(f"Изменение должности с {self.__position} на {value}")
        self.__position = value

    def get_position(self):
        return self.__position

    # Методы для работы с БД
    def save(self):
        self.logger.info(f"Сохранение сотрудника {self.full_name()} в БД")
        db = Database()
        query = """INSERT INTO employees 
                   (name, surname, patronymic, phone_num, position, mail, date_of_employment) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (self._name, self._surname, self._patronymic, self._phone_num,
                  self.__position, self.__mail, self.__date_of_employment)
        db.execute_query(query, params)
        self.logger.debug("Сотрудник успешно сохранен")

    def update(self):
        if self.id is None:
            self.logger.error("Попытка обновить сотрудника без ID")
            raise ValueError("Нельзя обновить запись без ID")

        self.logger.info(f"Обновление сотрудника ID {self.id} в БД")
        db = Database()
        query = """UPDATE employees SET 
                   name=%s, surname=%s, patronymic=%s, phone_num=%s, 
                   position=%s, mail=%s, date_of_employment=%s 
                   WHERE id=%s"""
        params = (self._name, self._surname, self._patronymic, self._phone_num,
                  self.__position, self.__mail, self.__date_of_employment, self.id)
        db.execute_query(query, params)
        self.logger.debug("Сотрудник успешно обновлен")

    def delete(self):
        if self.id is None:
            self.logger.error("Попытка удалить сотрудника без ID")
            raise ValueError("Нельзя удалить запись без ID")

        self.logger.warning(f"Удаление сотрудника ID {self.id} из БД")
        db = Database()
        query = "DELETE FROM employees WHERE id=%s"
        db.execute_query(query, (self.id,))
        self.logger.info("Сотрудник удален")

    @classmethod
    def get_by_id(cls, id):
        logger = get_logger('person.employee')
        logger.debug(f"Поиск сотрудника по ID: {id}")
        db = Database()
        query = "SELECT * FROM employees WHERE id=%s"
        result = db.fetch_one(query, (id,))

        if result:
            logger.debug(f"Сотрудник с ID {id} найден")
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
        logger.warning(f"Сотрудник с ID {id} не найден")
        return None

    @classmethod
    def get_all(cls):
        logger = get_logger('person.employee')
        logger.debug("Запрос всех сотрудников из БД")
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
        logger.info(f"Получено {len(employees)} сотрудников")
        return employees


class Guest(Person):
    def __init__(self, name, surname, phone_num, passport_data, patronymic="", id=None):
        super().__init__(name, surname, phone_num, patronymic, id)
        self.logger = get_logger('person.guest')
        if not passport_data:
            self.logger.error("Попытка обновить гостя без паспортных данных")
            raise InvalidDataError("Паспортные данные обязательны")

        self.__passport_data = passport_data
        self.logger.info(f"Создан гость: {self.full_name()}, паспорт: {passport_data}")

    def get_passport_data(self):
        return self.__passport_data

    def set_passport_data(self, value):
        self.logger.debug(f"Изменение паспортных данных на {value}")
        self.__passport_data = value

    def save(self):
        self.logger.info(f"Сохранение гостя {self.full_name()} в БД")
        db = Database()
        query = """INSERT INTO guests 
                   (name, surname, patronymic, phone_num, passport_data) 
                   VALUES (%s, %s, %s, %s, %s)"""
        params = (self._name, self._surname, self._patronymic,
                  self._phone_num, self.__passport_data)
        db.execute_query(query, params)
        self.logger.debug("Гость успешно сохранен")

    def update(self):
        if self.id is None:
            self.logger.error("Попытка обновить гостя без ID")
            raise ValueError("Нельзя обновить запись без ID")

        self.logger.info(f"Обновление гостя ID {self.id} в БД")
        db = Database()
        query = """UPDATE guests SET 
                   name=%s, surname=%s, patronymic=%s, phone_num=%s, passport_data=%s 
                   WHERE id=%s"""
        params = (self._name, self._surname, self._patronymic,
                  self._phone_num, self.__passport_data, self.id)
        db.execute_query(query, params)

    def delete(self):
        if self.id is None:
            self.logger.error("Попытка удалить гостя без ID")
            raise ValueError("Нельзя удалить запись без ID")

        self.logger.warning(f"Удаление гостя ID {self.id} из БД")
        db = Database()
        query = "DELETE FROM guests WHERE id=%s"
        db.execute_query(query, (self.id,))
        self.logger.info("Гость удален")

    @classmethod
    def get_by_id(cls, id):
        logger = get_logger('person.guest')
        logger.debug(f"Поиск гостя по ID: {id}")
        db = Database()
        query = "SELECT * FROM guests WHERE id=%s"
        result = db.fetch_one(query, (id,))

        if result:
            logger.debug(f"Гость с ID {id} найден")
            return cls(
                name=result['name'],
                surname=result['surname'],
                phone_num=result['phone_num'],
                passport_data=result['passport_data'],
                patronymic=result['patronymic'],
                id=result['id']
            )
        logger.warning(f"Гость с ID {id} не найден")
        return None

    @classmethod
    def get_all(cls):
        logger = get_logger('person.guest')
        logger.debug("Запрос всех гостей из БД")
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
        logger.info(f"Получено {len(guests)} гостей")
        return guests