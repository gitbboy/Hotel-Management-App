from typing import Optional

class HotelManagementError(Exception):
    """базовый класс для ошибок управления отелем """
    pass

class PersonError(HotelManagementError):
    """Базовый класс для ошибок, связанных с людьми"""
    pass

class RoomError(HotelManagementError):
    """Базовый класс для ошибок, связанных с комнатами"""
    pass



class RoomNotFoundError(HotelManagementError):
    """вызывается, когда комната не найдена """
    def __init__(self, room_number: str):
        super().__init__(f"Комната {room_number} не найдена.")

class BookingError(Exception):
    def __init__(self, message, action=None):
        super().__init__(message)
        self.message = message
        self.action = action

class InvalidDataError(HotelManagementError):
    """ошибка валидации данных """
    def __init__(self, message: str):
        super().__init__(f"Неверные данные: {message}")


class PersonNotFoundError(PersonError):
    """Вызывается, когда персона не найдена"""
    def __init__(self, person_id: Optional[str] = None, identifier: Optional[str] = None):
        if person_id:
            super().__init__(f"Человек с ID {person_id} не найдена.")
        elif identifier:
            super().__init__(f"Человек с идентификатором {identifier} не найдена.")
        else:
            super().__init__("Человек не найдена.")

class InvalidPersonDataError(PersonError):
    """Ошибка валидации данных персоны"""
    def __init__(self, message: str, field: Optional[str] = None):
        if field:
            super().__init__(f"Неверные данные персоны ({field}): {message}")
        else:
            super().__init__(f"Неверные данные персоны: {message}")

class PersonAlreadyExistsError(PersonError):
    """Персона с такими данными уже существует"""
    def __init__(self, identifier: str, value: str):
        super().__init__(f"Человек с {identifier} '{value}' уже существует.")


# Room Errors
class InvalidRoomDataError(RoomError):
    """Ошибка валидации данных комнаты"""
    def __init__(self, message: str, field: Optional[str] = None):
        if field:
            super().__init__(f"Неверные данные комнаты ({field}): {message}")
        else:
            super().__init__(f"Неверные данные комнаты: {message}")

class RoomAlreadyExistsError(RoomError):
    """Комната с таким номером уже существует"""
    def __init__(self, room_number: str):
        super().__init__(f"Комната с номером {room_number} уже существует.")

class RoomNotAvailableError(RoomError):
    """Комната недоступна для бронирования"""
    def __init__(self, room_number: str, reason: str = "занята"):
        super().__init__(f"Комната {room_number} недоступна: {reason}")


# Booking Errors
class BookingNotFoundError(BookingError):
    """Бронирование не найдено"""
    def __init__(self, booking_id: Optional[str] = None, guest_id: Optional[str] = None):
        if booking_id:
            super().__init__(f"Бронирование с ID {booking_id} не найдено.")
        elif guest_id:
            super().__init__(f"Бронирование для гостя {guest_id} не найдено.")
        else:
            super().__init__("Бронирование не найдено.")

class InvalidBookingDataError(BookingError):
    """Ошибка валидации данных бронирования"""
    def __init__(self, message: str, field: Optional[str] = None):
        if field:
            super().__init__(f"Неверные данные бронирования ({field}): {message}")
        else:
            super().__init__(f"Неверные данные бронирования: {message}")

class BookingConflictError(BookingError):
    """Конфликт бронирований"""
    def __init__(self, room_number: str, check_in: str, check_out: str):
        super().__init__(
            f"Конфликт бронирований для комнаты {room_number} "
            f"в период с {check_in} по {check_out}"
        )

class BookingDateError(BookingError):
    """Ошибка в датах бронирования"""
    def __init__(self, message: str):
        super().__init__(f"Ошибка дат бронирования: {message}")
