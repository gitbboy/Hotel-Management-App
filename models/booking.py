from exceptions import InvalidDataError, InvalidPersonDataError, InvalidRoomDataError
from datetime import date, datetime
from database import Database
from log_config import get_logger


class Booking:
    def __init__(self, guest_id, room_id, check_in_date, check_out_date, id=None, is_active=True):

        if not guest_id:
            raise InvalidDataError("ID гостя обязателен")

        if not room_id:
            raise InvalidDataError("ID комнаты обязателен")

        if not isinstance(check_in_date, date) or not isinstance(check_out_date, date):
            raise InvalidDataError("Даты должны быть объектами datetime.date")

        if check_in_date >= check_out_date:
            raise InvalidDataError("Дата выезда должна быть позже даты заезда")

        self.logger = get_logger('booking')
        self.id = id
        self.__guest_id = guest_id
        self.__room_id = room_id
        self.__check_in_date = check_in_date
        self.__check_out_date = check_out_date
        self.__is_active = is_active
        self.logger.info(
        f"Создано бронирование: гость {guest_id}, комната {room_id}, {check_in_date} - {check_out_date}")

    def get_guest_id(self):
        return self.__guest_id

    def set_guest_id(self, value):
        if not value:
            self.logger.error(f"Попытка изменение id гостя бронирования")
            raise InvalidPersonDataError("Ошибка смены id комнаты!")

        self.logger.debug(f"Изменение id гостя бронирования {self.id} на {value}")
        self.__guest_id = value

    def get_room_id(self):
        return self.__room_id

    def set_room_id(self, value):
        if not value:
            self.logger.error(f"Попытка изменение id комнаты бронирования")
            raise InvalidRoomDataError("Ошибка смены id комнаты!")

        self.logger.debug(f"Изменение id комнаты бронирования {self.id} на {value}")
        self.__room_id = value

    def get_check_in_date(self):
        return self.__check_in_date

    def set_check_in_date(self, value):
        if not isinstance(value, date):
            self.logger.error(f"Попытка изменение даты заезда бронирования не в формате datetime")
            raise InvalidDataError("Дата должна быть объектом datetime.date")
        self.__check_in_date = value
        self.logger.debug(f"Изменение даты заезда бронирования {self.id} на {value}")

    def get_check_out_date(self):
        return self.__check_out_date

    def set_check_out_date(self, value):
        if not isinstance(value, date):
            self.logger.error(f"Попытка изменение даты заезда бронирования не в формате datetime")
            raise InvalidDataError("Дата должна быть объектом datetime.date")

        if self.__check_in_date and value <= self.__check_in_date:
            self.logger.error(f"Попытка изменение даты заезда позже даты заезда")
            raise InvalidDataError("Дата выезда должна быть позже даты заезда")

        self.__check_out_date = value
        self.logger.debug(f"Изменение даты выезда бронирования {self.id} на {value}")

    def get_is_active(self):
        return self.__is_active

    def set_is_active(self, value):
        status = "активно" if value else "неактивно"
        self.logger.info(f"Бронирование {self.id} теперь {status}")
        self.__is_active = value

    def save(self):
        self.logger.info(f"Сохранение бронирования {self.id} в БД")
        db = Database()
        query = """INSERT INTO bookings 
                      (guest_id, room_id, check_in_date, check_out_date, is_active) 
                      VALUES (%s, %s, %s, %s, %s)"""
        params = (self.__guest_id, self.__room_id, self.__check_in_date,
                 self.__check_out_date, self.__is_active)
        db.execute_query(query, params)
        self.logger.debug("Бронирование успешно сохранено")

    def update(self):
        if self.id is None:
            self.logger.error("Попытка обновить бронирование без ID")
            raise ValueError("Нельзя обновить запись без ID")

        self.logger.info(f"Обновление бронирования ID {self.id} в БД")
        db = Database()
        query = """UPDATE bookings SET 
                      guest_id=%s, room_id=%s, check_in_date=%s, 
                      check_out_date=%s, is_active=%s 
                      WHERE id=%s"""
        params = (self.__guest_id, self.__room_id, self.__check_in_date,
                 self.__check_out_date, self.__is_active, self.id)
        db.execute_query(query, params)
        self.logger.debug("Бронирование успешно обновлено")

    def delete(self):
        if self.id is None:
            self.logger.error("Попытка удалить бронирование без ID")
            raise ValueError("Нельзя удалить запись без ID")

        self.logger.warning(f"Удаление бронирования ID {self.id} из БД")
        db = Database()
        query = "DELETE FROM bookings WHERE id=%s"
        db.execute_query(query, (self.id,))
        self.logger.info("Бронирование удалено")

    @classmethod
    def get_by_id(cls, id):
        logger = get_logger('booking')
        logger.debug(f"Поиск бронирования по ID: {id}")
        db = Database()
        query = "SELECT * FROM bookings WHERE id=%s"
        result = db.fetch_one(query, (id,))

        if result:
            logger.debug(f"Бронирование с ID {id} найдено")
            return cls(
                guest_id=result['guest_id'],
                room_id=result['room_id'],
                check_in_date=result['check_in_date'],
                check_out_date=result['check_out_date'],
                id=result['id'],
                is_active=result['is_active']
            )
        logger.warning(f"Бронирование с ID {id} не найдено")
        return None

    @classmethod
    def get_all(cls):
        logger = get_logger('booking')
        logger.debug("Запрос всех бронирований из БД")
        db = Database()
        query = "SELECT * FROM bookings"
        results = db.fetch_all(query)

        bookings = []
        for result in results:
            bookings.append(cls(
                guest_id=result['guest_id'],
                room_id=result['room_id'],
                check_in_date=result['check_in_date'],
                check_out_date=result['check_out_date'],
                id=result['id'],
                is_active=result['is_active']
            ))
        logger.info(f"Получено {len(bookings)} бронирований")
        return bookings

    @classmethod
    def get_active_bookings(cls):
        logger = get_logger('booking')
        logger.debug("Запрос активных бронирований из БД")
        db = Database()
        query = "SELECT * FROM bookings WHERE is_active = TRUE"
        results = db.fetch_all(query)

        bookings = []
        for result in results:
            bookings.append(cls(
                guest_id=result['guest_id'],
                room_id=result['room_id'],
                check_in_date=result['check_in_date'],
                check_out_date=result['check_out_date'],
                id=result['id'],
                is_active=result['is_active']
            ))
        logger.info(f"Найдено {len(bookings)} активных бронирований")
        return bookings

    @classmethod
    def is_room_available(cls, room_id, check_in_date, check_out_date, exclude_booking_id=None):
        try:
            bookings = cls.get_all()

            if isinstance(check_in_date, str):
                check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            if isinstance(check_out_date, str):
                check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d").date()

            for booking in bookings:
                # Пропускаем исключаемое бронирование (при редактировании)
                if exclude_booking_id and booking.id == exclude_booking_id:
                    continue

                if booking.__room_id == room_id and booking.__is_active:

                    existing_check_in = booking.__check_in_date
                    existing_check_out = booking.__check_out_date

                    if isinstance(existing_check_in, str):
                        existing_check_in = datetime.strptime(existing_check_in, "%Y-%m-%d").date()
                    if isinstance(existing_check_out, str):
                        existing_check_out = datetime.strptime(existing_check_out, "%Y-%m-%d").date()

                    if not (check_out_date <= existing_check_in or check_in_date >= existing_check_out):
                        # Найдено пересечение
                        return False

            return True

        except Exception as e:
            print(f"Ошибка при проверке доступности номера: {e}")
            return False