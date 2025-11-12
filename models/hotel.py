from exceptions import RoomNotFoundError, BookingError, InvalidDataError
from datetime import date
import calendar


class Hotel:
    def __init__(self):
        self.__employees = []
        self.__rooms = []
        self.__active_bookings = []
        self.__completed_bookings = []

    def add_employee(self, employee):
        # Валидация данных сотрудника
        if not employee or not hasattr(employee, 'get_name'):
            raise InvalidDataError("Некорректные данные сотрудника")
        self.__employees.append(employee)

    def remove_employee(self, employee):
        if employee not in self.__employees:
            raise RoomNotFoundError(f"Сотрудник {employee.get_name()} не найден")
        self.__employees.remove(employee)


    def add_room(self, room):
        for existing_room in self.__rooms:
            if existing_room.get_number() == room.get_number():
                raise BookingError(room.get_number(), "добавления - комната уже существует")
        self.__rooms.append(room)

    def remove_room(self, room_number):
        room_to_remove = None
        for room in self.__rooms:
            if room.get_number() == room_number:
                room_to_remove = room
                break

        if not room_to_remove:
            raise RoomNotFoundError(room_number)

        for booking in self.__active_bookings:
            if booking.get_room().get_number() == room_number:
                raise BookingError(room_number, "удаления - есть активные бронирования")

        self.__rooms.remove(room_to_remove)

    def add_booking(self, booking):
        room = booking.get_room()
        if not room.is_free():
            raise BookingError(room.get_number(), "бронирования - комната занята")

        # Проверяем корректность дат
        if booking.get_check_in_date() >= booking.get_check_out_date():
            raise InvalidDataError("Дата выезда должна быть позже даты заезда")

        self.__active_bookings.append(booking)
        room.set_free(False)

    def cancel_booking(self, booking):
        if booking not in self.__active_bookings:
            raise BookingError(booking.get_room().get_number(), "отмены - бронирование не найдено")

        booking.get_room().set_free(True)
        self.__active_bookings.remove(booking)
        self.__completed_bookings.append(booking)

    def get_employees_list(self):
        return self.__employees.copy()

    def get_free_rooms(self):
        return [room for room in self.__rooms if room.is_free()]

    def get_price_list(self):
        return self.get_free_rooms()

    def get_guests_info(self):
        info = []
        for booking in self.__active_bookings:
            info.append({
                'guest': booking.get_guest().full_name(),
                'phone': booking.get_guest().get_phone_num(),
                'period': f"{booking.get_check_in_date()} - {booking.get_check_out_date()}",
                'room': booking.get_room().get_number()
            })
        return info

    def get_monthly_report(self, month, year):
        report = {}

        days_in_month = calendar.monthrange(year, month)[1]

        for room in self.__rooms:
            report[room.get_number()] = {
                'occupied_days': 0,
                'free_days': days_in_month,
                'total_guests': 0
            }

        all_bookings = self.__active_bookings + self.__completed_bookings

        for booking in all_bookings:
            if (booking.get_check_in_date().year == year and booking.get_check_in_date().month == month) or \
                    (booking.get_check_out_date().year == year and booking.get_check_out_date().month == month):

                month_start = date(year, month, 1)
                month_end = date(year, month, days_in_month)

                start_date = max(booking.get_check_in_date(), month_start)
                end_date = min(booking.get_check_out_date(), month_end)

                days_occupied = (end_date - start_date).days + 1

                room_id = booking.get_room().get_number()
                if room_id in report:
                    report[room_id]['occupied_days'] += days_occupied
                    report[room_id]['free_days'] -= days_occupied
                    report[room_id]['total_guests'] += 1

        return report