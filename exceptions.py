class HotelManagementError(Exception):
    """базовый класс для ошибок управления отелем """
    pass

class RoomNotFoundError(HotelManagementError):
    """вызывается, когда комната не найдена """
    def __init__(self, room_number: str):
        super().__init__(f"Комната {room_number} не найдена.")

class BookingError(HotelManagementError):
    """ошибка при бронировании / освобождении комнаты """
    def __init__(self, room_number: str, action: str):
        super().__init__(f"Ошибка {action} комнаты {room_number}.")

class InvalidDataError(HotelManagementError):
    """ошибка валидации данных """
    def __init__(self, message: str):
        super().__init__(f"Неверные данные: {message}")