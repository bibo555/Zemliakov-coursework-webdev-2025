import sys
from os.path import abspath, dirname
from datetime import datetime, timedelta

sys.path.insert(0, dirname(abspath(__file__)))
from app import create_app, db
from app.models import User, Airport, Airline, Flight

app = create_app()

def init_test_data():
    """Добавляет тестовые данные, если их нет в БД"""
    if not User.query.first():  # Если нет пользователей
        # Создаём админа
        admin = User(
            username='admin',
            email='admin@example.com',
            fullname='Administrator',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Создаём аэропорты (добавлены новые города и аэропорты)
        airports = [
            Airport(city='Москва', name='Шереметьево', code='SVO', country='Россия'),
            Airport(city='Москва', name='Домодедово', code='DME', country='Россия'),
            Airport(city='Санкт-Петербург', name='Пулково', code='LED', country='Россия'),
            Airport(city='Казань', name='Казань', code='KZN', country='Россия'),
            Airport(city='Екатеринбург', name='Кольцово', code='SVX', country='Россия'),
            Airport(city='Сочи', name='Сочи', code='AER', country='Россия'),
            Airport(city='Краснодар', name='Краснодар', code='KRR', country='Россия'),
            Airport(city='Новосибирск', name='Толмачёво', code='OVB', country='Россия'),
            Airport(city='Владивосток', name='Владивосток', code='VVO', country='Россия'),
            Airport(city='Стамбул', name='Ататюрк', code='IST', country='Турция'),
            Airport(city='Анталья', name='Анталья', code='AYT', country='Турция'),
            Airport(city='Дубай', name='Дубай', code='DXB', country='ОАЭ'),
        ]
        db.session.add_all(airports)

        # Создаём авиакомпании (добавлены новые авиакомпании)
        airlines = [
            Airline(name='Aeroflot', code='SU'),
            Airline(name='S7 Airlines', code='S7'),
            Airline(name='Ural Airlines', code='U6'),
            Airline(name='Pobeda', code='DP'),
            Airline(name='Turkish Airlines', code='TK'),
            Airline(name='Emirates', code='EK'),
            Airline(name='Lufthansa', code='LH'),
            Airline(name='Air France', code='AF'),
        ]
        db.session.add_all(airlines)

        # Создаём тестовые рейсы (добавлены новые рейсы)
        airline_su = Airline.query.filter_by(code='SU').first()
        airline_s7 = Airline.query.filter_by(code='S7').first()
        airline_u6 = Airline.query.filter_by(code='U6').first()
        
        airport_svo = Airport.query.filter_by(code='SVO').first()
        airport_led = Airport.query.filter_by(code='LED').first()
        airport_kzn = Airport.query.filter_by(code='KZN').first()
        airport_ist = Airport.query.filter_by(code='IST').first()

        if all([airline_su, airline_s7, airline_u6, airport_svo, airport_led, airport_kzn, airport_ist]):
            flights = [
                # Рейсы Aeroflot
                Flight(
                    airline_id=airline_su.id,
                    flight_number="SU-100",
                    origin_id=airport_svo.id,
                    destination_id=airport_led.id,
                    departure_time=datetime.strptime("10:00", "%H:%M").time(),
                    arrival_time=datetime.strptime("11:30", "%H:%M").time(),
                    duration=90,
                    price=5000,
                    departure_date=datetime.strptime("2025-04-10", "%Y-%m-%d").date()
                ),
                Flight(
                    airline_id=airline_su.id,
                    flight_number="SU-200",
                    origin_id=airport_svo.id,
                    destination_id=airport_ist.id,
                    departure_time=datetime.strptime("14:00", "%H:%M").time(),
                    arrival_time=datetime.strptime("18:30", "%H:%M").time(),
                    duration=270,
                    price=15000,
                    departure_date=datetime.strptime("2025-04-11", "%Y-%m-%d").date()
                ),
                # Рейсы S7 Airlines
                Flight(
                    airline_id=airline_s7.id,
                    flight_number="S7-300",
                    origin_id=airport_led.id,
                    destination_id=airport_kzn.id,
                    departure_time=datetime.strptime("08:00", "%H:%M").time(),
                    arrival_time=datetime.strptime("10:30", "%H:%M").time(),
                    duration=150,
                    price=7000,
                    departure_date=datetime.strptime("2025-04-12", "%Y-%m-%d").date()
                ),
                # Рейсы Ural Airlines
                Flight(
                    airline_id=airline_u6.id,
                    flight_number="U6-400",
                    origin_id=airport_kzn.id,
                    destination_id=airport_svo.id,
                    departure_time=datetime.strptime("16:00", "%H:%M").time(),
                    arrival_time=datetime.strptime("17:30", "%H:%M").time(),
                    duration=90,
                    price=4500,
                    departure_date=datetime.strptime("2025-04-13", "%Y-%m-%d").date()
                ),
            ]
            db.session.add_all(flights)

        db.session.commit()
        print("Тестовые данные добавлены!")

if __name__ == '__main__':
   
    app.run(debug=True)