import os 
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Configuración general de la aplicación
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Configuración de JWT
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de correo SMTP
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))


