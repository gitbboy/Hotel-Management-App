from exceptions import InvalidDataError, BookingError
from datetime import date
from database import Database


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

        if check_in_date < date.today():
            raise InvalidDataError("Дата заезда не может быть в прошлом")

        self.id = id
        self.__guest_id = guest_id
        self.__room_id = room_id
        self.__check_in_date = check_in_date
        self.__check_out_date = check_out_date
        self.__is_active = is_active

    def get_guest_id(self):
        return self.__guest_id

    def get_room_id(self):
        return self.__room_id

    def get_check_in_date(self):
        return self.__check_in_date

    def set_check_in_date(self, value):
        if not isinstance(value, date):
            raise InvalidDataError("Дата должна быть объектом datetime.date")
        self.__check_in_date = value

    def get_check_out_date(self):
        return self.__check_out_date

    def set_check_out_date(self, value):
        if not isinstance(value, date):
            raise InvalidDataError("Дата должна быть объектом datetime.date")

        if self.__check_in_date and value <= self.__check_in_date:
            raise InvalidDataError("Дата выезда должна быть позже даты заезда")

        self.__check_out_date = value

    def get_is_active(self):
        return self.__is_active

    def set_is_active(self, value):
        self.__is_active = value

    def save(self):
        db = Database()
        query = """INSERT INTO bookings 
                      (guest_id, room_id, check_in_date, check_out_date, is_active) 
                      VALUES (%s, %s, %s, %s, %s)"""
        params = (self.__guest_id, self.__room_id, self.__check_in_date,
                 self.__check_out_date, self.__is_active)
        db.execute_query(query, params)

    def update(self):
        if self.id is None:
            raise ValueError("Нельзя обновить запись без ID")

        db = Database()
        query = """UPDATE bookings SET 
                      guest_id=%s, room_id=%s, check_in_date=%s, 
                      check_out_date=%s, is_active=%s 
                      WHERE id=%s"""
        params = (self.__guest_id, self.__room_id, self.__check_in_date,
                 self.__check_out_date, self.__is_active, self.id)
        db.execute_query(query, params)

    def delete(self):
        if self.id is None:
            raise ValueError("Нельзя удалить запись без ID")

        db = Database()
        query = "DELETE FROM bookings WHERE id=%s"
        db.execute_query(query, (self.id,))

    @classmethod
    def get_by_id(cls, id):
        db = Database()
        query = "SELECT * FROM bookings WHERE id=%s"
        result = db.fetch_one(query, (id,))

        if result:
            return cls(
                guest_id=result['guest_id'],
                room_id=result['room_id'],
                check_in_date=result['check_in_date'],
                check_out_date=result['check_out_date'],
                id=result['id'],
                is_active=result['is_active']
            )
        return None

    @classmethod
    def get_all(cls):
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
        return bookings

    @classmethod
    def get_active_bookings(cls):
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
        return bookings
