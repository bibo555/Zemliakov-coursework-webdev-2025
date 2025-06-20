from flask_sqlalchemy import SQLAlchemy
from flask_login import  UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from . import db 

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    photo = db.Column(db.String(255))  # Путь к фото профиля
    passport_file = db.Column(db.String(255))
    
    passports = db.relationship('Passport', back_populates='user', uselist=True)
    bookings = db.relationship('Booking', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Passport(db.Model):
    __tablename__ = 'passports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    series = db.Column(db.String(10), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    issued_by = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(255))
    
    user = db.relationship('User', back_populates='passports')

class Airport(db.Model):
    __tablename__ = 'airports'
    
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    country = db.Column(db.String(50), nullable=False)
    
    # Связи
    departure_flights = db.relationship('Flight', foreign_keys='Flight.origin_id', back_populates='origin')
    arrival_flights = db.relationship('Flight', foreign_keys='Flight.destination_id', back_populates='destination')

class Airline(db.Model):
    __tablename__ = 'airlines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True)
    logo = db.Column(db.String(255))
    
    # Связи
    flights = db.relationship('Flight', back_populates='airline')

class Flight(db.Model):
    __tablename__ = 'flights'
    
    id = db.Column(db.Integer, primary_key=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airlines.id'), nullable=False)
    flight_number = db.Column(db.String(20), nullable=False)
    origin_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # в минутах
    price = db.Column(db.Integer, nullable=False)
    departure_date = db.Column(db.Date, nullable=False)  # Добавьте эту строку
    
    # Остальные отношения остаются без изменений
    airline = db.relationship('Airline', back_populates='flights')
    origin = db.relationship('Airport', foreign_keys=[origin_id], back_populates='departure_flights')
    destination = db.relationship('Airport', foreign_keys=[destination_id], back_populates='arrival_flights')
    bookings = db.relationship('Booking', back_populates='flight')

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed')
    price = db.Column(db.Integer, nullable=False)
    
    # Связи
    user = db.relationship('User', back_populates='bookings')
    flight = db.relationship('Flight', back_populates='bookings')
    passengers = db.relationship('Passenger', back_populates='booking')

class Passenger(db.Model):
    __tablename__ = 'passengers'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    passport_series = db.Column(db.String(10), nullable=False)
    passport_number = db.Column(db.String(20), nullable=False)
    
    # Связи
    booking = db.relationship('Booking', back_populates='passengers')