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


