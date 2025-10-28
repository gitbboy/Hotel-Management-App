from database import Database


class HotelRoom:
    def __init__(self, room_id, price, type, capacity, id=None, is_free=True):
        self.id = id  # первичный ключ таблицы
        self.__room_id = room_id
        self.__type = type
        self.__price = price
        self.__capacity = capacity
        self.__is_free = bool(is_free)

    def get_type(self):
        return self.__type

    def get_number(self):
        return self.__room_id

    def get_price(self):
        return self.__price

    def set_price(self, value):
        self.__price = float(value)

    def get_capacity(self):
        return self.__capacity

    def set_capacity(self, value):
        self.__capacity = int(value)

    def is_free(self):
        return self.__is_free

    def set_free(self, value):
        self.__is_free = bool(value)

    # Методы для работы с БД
    def save(self):
        db = Database()
        query = """INSERT INTO rooms 
                   (room_id, type, price, capacity, is_free) 
                   VALUES (%s, %s, %s, %s, %s)"""
        params = (self.__room_id, self.__type, self.__price,
                 self.__capacity, self.__is_free)
        db.execute_query(query, params)

    def update(self):
        if self.id is None:
            raise ValueError("Нельзя обновить запись без ID")

        db = Database()
        query = """UPDATE rooms SET 
                   room_id=%s, type=%s, price=%s, 
                   capacity=%s, is_free=%s 
                   WHERE id=%s"""
        params = (self.__room_id, self.__type, self.__price,
                 self.__capacity, self.__is_free, self.id)
        db.execute_query(query, params)

    def delete(self):
        if self.id is None:
            raise ValueError("Нельзя удалить запись без ID")

        db = Database()
        query = "DELETE FROM rooms WHERE id=%s"
        db.execute_query(query, (self.id,))

    @classmethod
    def get_by_id(cls, id):
        db = Database()
        query = "SELECT * FROM rooms WHERE id=%s"
        result = db.fetch_one(query, (int(id),))

        if result:
            return cls(
                room_id=result['room_id'],
                type=result['type'],
                price=result['price'],
                capacity=result['capacity'],
                id=result['id'],
                is_free=bool(result['is_free'])
            )
        return None

    @classmethod
    def get_by_room_id(cls, room_id):
        db = Database()
        query = "SELECT * FROM rooms WHERE room_id=%s"
        result = db.fetch_one(query, (int(room_id),))

        if result:
            return cls(
                room_id=result['room_id'],
                type=result['type'],
                price=result['price'],
                capacity=result['capacity'],
                id=result['id'],
                is_free=bool(result['is_free'])
            )
        return None

    @classmethod
    def get_all(cls):
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
        return rooms

    @classmethod
    def get_available_rooms(cls):
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
        return rooms