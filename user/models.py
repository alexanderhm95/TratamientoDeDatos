import jwt
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from datetime import datetime
from time import time
from flask import current_app

#Inicialización de la base de datos  para la aplicación Flask
db = SQLAlchemy()
#Inicialización de Bcrypt para el manejo de contraseñas
bcrypt = Bcrypt()


"""
Modelo de Usuario para la aplicación Flask. Este modelo define la estructura de la tabla de usuarios en la base de datos y proporciona métodos para manejar la autenticación y generación de tokens JWT.
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # Rol del usuario (e.g., 'user', 'admin')
    is_active = db.Column(db.Boolean, default=True)  # Indica si el usuario está activo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username, email, password, role='user'):
        self.username = username.strip() if username else username
        self.email = email.strip() if email else email
        self.password = password  # Usar el setter correctamente
        self.role = role

    @property
    def password(self):
        raise AttributeError('La contraseña no es un atributo legible.')

    @password.setter
    def password(self, password):
        """Genera un hash de la contraseña y lo almacena en el campo password_hash."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_jwt(self):
        """Genera un token JWT para el usuario."""
        payload = {
            'user_id': self.id,
            'exp': time() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }
        token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        return token
    
    def to_dict(self):
        """Convierte el objeto User a un diccionario, excluyendo la contraseña."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }