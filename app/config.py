import os
from dotenv import load_dotenv
from datetime import timedelta

from pathlib import Path

# Путь к папке instance (автоматически определяется Flask)

BASE_DIR = Path(__file__).parent  # Папка app/
INSTANCE_PATH = BASE_DIR.parent / "instance"
load_dotenv()

class Config:
    # Основные настройки Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'd3f4u1t-s3cr3t-k3y-!23$%^&*(qwertyUIOP')
    
    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{INSTANCE_PATH}/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Настройки Flask-Login
    REMEMBER_COOKIE_DURATION = 3600  # 1 час в секундах
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    
    # Настройки почты (пример, можно добавить реальные позже)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Показывает SQL-запросы в консоли

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # PostgreSQL для продакшена
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/airline_db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False