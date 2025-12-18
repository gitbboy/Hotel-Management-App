import pytest
from datetime import date
from database import Database
#from unittest.mock import Mock
from exceptions import RoomNotFoundError, BookingError, InvalidDataError


from models import Person, Employee, Guest
from models import HotelRoom
from models import Booking


def test_database_connection():
    db = Database()
    try:
        result = db.fetch_one("SELECT NOW()")
        if result:
            print(f"Connection success. Время сервера: {result['NOW()']}")

            employees = db.fetch_all("SELECT * FROM employees")
            print("\nПервые 3 записи из БД (сотрудники)")
            for i in range(3):
                print(employees[i])
            return True
        else:
            print("Не удалось выполнить тестовый запрос")
            return False
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False

# test_database_connection() # тест подключения к БД

class TestPerson:
    def test_person_creation(self):
        person = Person("John", "Doe", "123456789", "Michael", 1)
        assert person.id == 1
        assert person.get_name() == "John"
        assert person.get_surname() == "Doe"
        assert person.get_patronymic() == "Michael"
        assert person.get_phone_num() == "123456789"

    def test_person_setters(self):
        person = Person("John", "Doe", "123456789")
        person.set_name("Jane")
        person.set_surname("Smith")
        person.set_patronymic("Ann")
        person.set_phone_num("987654321")

        assert person.get_name() == "Jane"
        assert person.get_surname() == "Smith"
        assert person.get_patronymic() == "Ann"
        assert person.get_phone_num() == "987654321"

    def test_person_full_name(self):
        person = Person("John", "Doe", "123456789", "Michael")
        assert person.full_name() == "Doe John Michael"

        person_no_patronymic = Person("John", "Doe", "123456789")
        assert person_no_patronymic.full_name() == "Doe John"


class TestEmployee:
    def test_employee_creation(self):
        employee = Employee(
            "John", "Doe", "Manager", "123456789",
            "john@hotel.com", "2023-01-15", "Michael", 1
        )

        assert employee.id == 1
        assert employee.get_name() == "John"
        assert employee.get_surname() == "Doe"
        assert employee.get_position() == "Manager"
        assert employee.get_phone_num() == "123456789"
        assert employee.get_mail() == "john@hotel.com"
        assert employee.get_date_of_employment() == "2023-01-15"
        assert employee.get_patronymic() == "Michael"

    def test_employee_setters(self):
        employee = Employee("John", "Doe", "Manager", "123456789", "john@hotel.com", "2023-01-15")

        employee.set_position("Director")
        employee.set_mail("john.director@hotel.com")
        employee.set_date_of_employment("2024-01-01")

        assert employee.get_position() == "Director"
        assert employee.get_mail() == "john.director@hotel.com"
        assert employee.get_date_of_employment() == "2024-01-01"


class TestGuest:

    def test_guest_creation(self):
        guest = Guest("Alice", "Smith", "987654321", "AB123456", "Marie", 1)

        assert guest.id == 1
        assert guest.get_name() == "Alice"
        assert guest.get_surname() == "Smith"
        assert guest.get_phone_num() == "987654321"
        assert guest.get_passport_data() == "AB123456"
        assert guest.get_patronymic() == "Marie"

    def test_guest_setters(self):
        guest = Guest("Alice", "Smith", "987654321", "AB123456")

        guest.set_passport_data("CD789012")
        assert guest.get_passport_data() == "CD789012"


class TestHotelRoom:

    def test_hotel_room_creation(self):
        room = HotelRoom("101", 100.0, "Standard", 2, 1, True)

        assert room.id == 1
        assert room.get_number() == "101"
        assert room.get_price() == 100.0
        assert room.get_type() == "Standard"
        assert room.get_capacity() == 2
        assert room.is_free() == True

    def test_hotel_room_setters(self):
        room = HotelRoom("101", 100.0, "Standard", 2)

        room.set_price(150.0)
        room.set_capacity(3)
        room.set_free(False)

        assert room.get_price() == 150.0
        assert room.get_capacity() == 3
        assert room.is_free() == False


class TestBooking:

    def test_booking_creation(self):
        check_in = date(2026, 1, 1)
        check_out = date(2026, 1, 5)
        booking = Booking(1, 101, check_in, check_out, 1, True)

        assert booking.id == 1
        assert booking.get_guest_id() == 1
        assert booking.get_room_id() == 101
        assert booking.get_check_in_date() == check_in
        assert booking.get_check_out_date() == check_out
        assert booking.get_is_active() == True

    def test_booking_setters(self):
        check_in = date(2026, 1, 1)
        check_out = date(2026, 1, 5)
        new_check_in = date(2026, 1, 2)
        new_check_out = date(2026, 1, 6)

        booking = Booking(1, 101, check_in, check_out)

        booking.set_check_in_date(new_check_in)
        booking.set_check_out_date(new_check_out)
        booking.set_is_active(False)

        assert booking.get_check_in_date() == new_check_in
        assert booking.get_check_out_date() == new_check_out
        assert booking.get_is_active() == False

@pytest.mark.parametrize("name,surname,phone,expected_fullname", [
    ("John", "Doe", "123456789", "Doe John"),
    ("Alice", "Smith", "987654321", "Smith Alice"),
    ("Bob", "Johnson", "555555555", "Johnson Bob"),
])
def test_person_fullname_parameterized(name, surname, phone, expected_fullname):
    person = Person(name, surname, phone)
    assert person.full_name() == expected_fullname


@pytest.mark.parametrize("room_id,price,room_type,capacity", [
    ("101", 100.0, "Standard", 2),
    ("201", 200.0, "Deluxe", 3),
    ("301", 300.0, "Suite", 4),
])
def test_hotel_room_parameterized(room_id, price, room_type, capacity):
    room = HotelRoom(room_id, price, room_type, capacity)

    assert room.get_number() == room_id
    assert room.get_price() == price
    assert room.get_type() == room_type
    assert room.get_capacity() == capacity

class TestExceptions:

    def test_room_not_found_error(self):
        with pytest.raises(RoomNotFoundError) as exc_info:
            raise RoomNotFoundError("101")
        assert "Комната 101 не найдена" in str(exc_info.value)

    def test_booking_error(self):
        with pytest.raises(BookingError) as exc_info:
            raise BookingError(f"Ошибка бронирования комнаты {101}", "бронирования")
        assert f"Ошибка бронирования комнаты 101" in str(exc_info.value)

    def test_invalid_data_error(self):
        with pytest.raises(InvalidDataError) as exc_info:
            raise InvalidDataError("отрицательная цена")
        assert "Неверные данные: отрицательная цена" in str(exc_info.value)

    def test_booking_invalid_dates(self):
        # Дата выезда раньше даты заезда
        with pytest.raises(InvalidDataError):
            Booking(1, 101, date(2024, 1, 5), date(2024, 1, 1))

    def test_person_invalid_data(self):
        with pytest.raises(InvalidDataError):
            Person("", "Doe", "123456789")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])