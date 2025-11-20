from database import Database
from log_config import get_logger
from exceptions import InvalidDataError


class HotelRoom:
    def __init__(self, room_id, price, type, capacity, id=None, is_free=True):

        if not room_id or not isinstance(room_id, (str, int)):
            raise InvalidDataError("Номер комнаты должен быть указан")

        if price < 0:
            raise InvalidDataError("Цена не может быть отрицательной")

        if capacity <= 0:
            raise InvalidDataError("Вместимость должна быть положительным числом")

        if not type:
            raise InvalidDataError("Тип комнаты должен быть указан")

        self.logger = get_logger('room')
        self.id = id  # первичный ключ таблицы
        self.__room_id = room_id
        self.__type = type
        self.__price = price
        self.__capacity = capacity
        self.__is_free = bool(is_free)
        self.logger.info(f"Создана комната: номер {room_id}, тип {type}, цена {price}")

    def get_type(self):
        return self.__type

    def get_number(self):
        return self.__room_id

    def get_price(self):
        return self.__price

    def set_price(self, value):
        if value < 0:
            self.logger.error("Попытка изменения с отрицательной ценой")
            raise InvalidDataError("Цена не может быть отрицательной")
        self.logger.debug(f"Изменение цены комнаты {self.__room_id} с {self.__price} на {value}")
        self.__price = float(value)

    def get_capacity(self):
        return self.__capacity

    def set_capacity(self, value):
        if value <= 0:
            self.logger.error(f"Поптыка изменение вместимости комнаты отрицательной ценой")
            raise InvalidDataError("Вместимость должна быть положительным числом")
        self.logger.debug(f"Изменение вместимости комнаты {self.__room_id} с {self.__capacity} на {value}")
        self.__capacity = int(value)

    def is_free(self):
        return self.__is_free

    def set_free(self, value):
        status = "свободна" if value else "занята"
        self.logger.info(f"Комната {self.__room_id} теперь {status}")
        self.__is_free = bool(value)

    # Методы для работы с БД
    def save(self):
        self.logger.info(f"Сохранение комнаты {self.__room_id} в БД")
        db = Database()
        query = """INSERT INTO rooms 
                   (room_id, type, price, capacity, is_free) 
                   VALUES (%s, %s, %s, %s, %s)"""
        params = (self.__room_id, self.__type, self.__price,
                 self.__capacity, self.__is_free)
        db.execute_query(query, params)
        self.logger.debug("Комната успешно сохранена")

    def update(self):
        if self.id is None:
            self.logger.error("Попытка обновить комнату без ID")
            raise ValueError("Нельзя обновить запись без ID")

        self.logger.info(f"Обновление комнаты ID {self.id} в БД")
        db = Database()
        query = """UPDATE rooms SET 
                   room_id=%s, type=%s, price=%s, 
                   capacity=%s, is_free=%s 
                   WHERE id=%s"""
        params = (self.__room_id, self.__type, self.__price,
                 self.__capacity, self.__is_free, self.id)
        db.execute_query(query, params)
        self.logger.debug("Комната успешно обновлена")

    def delete(self):
        if self.id is None:
            self.logger.error("Попытка удалить комнату без ID")
            raise ValueError("Нельзя удалить запись без ID")

        self.logger.warning(f"Удаление комнаты ID {self.id} из БД")
        db = Database()
        query = "DELETE FROM rooms WHERE id=%s"
        db.execute_query(query, (self.id,))
        self.logger.info("Комната удалена")

    @classmethod
    def get_by_id(cls, id):
        logger = get_logger('room')  # Создаем логгер для classmethod
        logger.debug(f"Поиск комнаты по ID: {id}")
        db = Database()
        query = "SELECT * FROM rooms WHERE id=%s"
        result = db.fetch_one(query, (int(id),))

        if result:
            logger.debug(f"Комната с ID {id} найдена")
            return cls(
                room_id=result['room_id'],
                type=result['type'],
                price=result['price'],
                capacity=result['capacity'],
                id=result['id'],
                is_free=bool(result['is_free'])
            )
        logger.warning(f"Комната с ID {id} не найдена")
        return None

    @classmethod
    def get_by_room_id(cls, room_id):
        logger = get_logger('room')  # Создаем логгер для classmethod
        logger.debug(f"Поиск комнаты по номеру: {room_id}")
        db = Database()
        query = "SELECT * FROM rooms WHERE room_id=%s"
        result = db.fetch_one(query, (int(room_id),))

        if result:
            logger.debug(f"Комната с номером {room_id} найдена")
            return cls(
                room_id=result['room_id'],
                type=result['type'],
                price=result['price'],
                capacity=result['capacity'],
                id=result['id'],
                is_free=bool(result['is_free'])
            )
        logger.warning(f"Комната с номером {room_id} не найдена")
        return None

    @classmethod
    def get_all(cls):
        logger = get_logger('room')
        logger.debug("Запрос всех комнат из БД")
        db = Database()
        query = "SELECT * FROM rooms"
        results = db.fetch_all(query)

        rooms = []
        for result in results:
            rooms.append(cls(
                room_id=result['room_id'],
                type=result['type'],
                price=result['price'],
                capacity=result['capacity'],
                id=result['id'],
                is_free=bool(result['is_free'])
            ))
        logger.info(f"Получено {len(rooms)} комнат")
        return rooms

    @classmethod
    def get_available_rooms(cls):
        logger = get_logger('room')  # Создаем логгер для classmethod
        logger.debug("Запрос доступных комнат из БД")
        db = Database()
        query = "SELECT * FROM rooms WHERE is_free = TRUE"
        results = db.fetch_all(query)

        rooms = []
        for result in results:
            rooms.append(cls(
                room_id=result['room_id'],
                type=result['type'],
                price=result['price'],
                capacity=result['capacity'],
                id=result['id'],
                is_free=bool(result['is_free'])
            ))
        logger.info(f"Найдено {len(rooms)} доступных комнат")
        return rooms