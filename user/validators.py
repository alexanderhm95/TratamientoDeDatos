"""
Funciones de validación para el módulo de usuarios.
"""
import re
from .exceptions import (
    UsernameError, 
    EmailError, 
    PasswordError,
    ValidationError
)

# ==================== CONSTANTES ====================

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128
TEMP_PASSWORD_LENGTH = 12

# Patrón de email válido
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Patrón de username válido (letras, números, guiones, guiones bajos)
USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'


# ==================== VALIDACIONES ====================

def validate_email(email):
    """
    Valida que el email tenga un formato correcto.
    
    Args:
        email: Correo electrónico a validar
        
    Returns:
        email limpio (sin espacios)
        
    Raises:
        EmailError: Si el email es inválido
    """
    email = email.strip() if email else ''
    
    if not email:
        raise EmailError('El correo electrónico es requerido.')
    
    if not re.match(EMAIL_PATTERN, email):
        raise EmailError('El correo electrónico no tiene un formato válido.')
    
    return email


def validate_username(username):
    """
    Valida que el username sea válido.
    
    - Mínimo 3 caracteres
    - Máximo 20 caracteres
    - Solo letras, números, guiones y guiones bajos
    
    Args:
        username: Nombre de usuario a validar
        
    Returns:
        username limpio (sin espacios)
        
    Raises:
        UsernameError: Si el username es inválido
    """
    username = username.strip() if username else ''
    
    if not username:
        raise UsernameError('El nombre de usuario es requerido.')
    
    if len(username) < USERNAME_MIN_LENGTH:
        raise UsernameError(f'El nombre de usuario debe tener al menos {USERNAME_MIN_LENGTH} caracteres.')
    
    if len(username) > USERNAME_MAX_LENGTH:
        raise UsernameError(f'El nombre de usuario no puede exceder {USERNAME_MAX_LENGTH} caracteres.')
    
    if not re.match(USERNAME_PATTERN, username):
        raise UsernameError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.')
    
    return username


def validate_password(password):
    """
    Valida que la contraseña sea segura.
    
    - Mínimo 6 caracteres
    - Máximo 128 caracteres
    
    Args:
        password: Contraseña a validar
        
    Returns:
        password
        
    Raises:
        PasswordError: Si la contraseña es inválida
    """
    if not password:
        raise PasswordError('La contraseña es requerida.')
    
    if len(password) < PASSWORD_MIN_LENGTH:
        raise PasswordError(f'La contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres.')
    
    if len(password) > PASSWORD_MAX_LENGTH:
        raise PasswordError(f'La contraseña no puede exceder {PASSWORD_MAX_LENGTH} caracteres.')
    
    return password


def validate_login_input(username, password):
    """
    Valida los datos de entrada para el login.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        
    Returns:
        Tupla (username, password) validados
        
    Raises:
        ValidationError: Si hay error en la validación
    """
    username = username.strip() if username else ''
    
    if not username:
        raise ValidationError('El nombre de usuario es requerido.')
    
    if not password:
        raise ValidationError('La contraseña es requerida.')
    
    return username, password


def validate_password_match(password, confirm_password):
    """
    Valida que dos contraseñas coincidan.
    
    Args:
        password: Primera contraseña
        confirm_password: Confirmación de contraseña
        
    Returns:
        password si coinciden
        
    Raises:
        PasswordError: Si no coinciden
    """
    if password != confirm_password:
        raise PasswordError('Las contraseñas no coinciden.')
    
    return password


def calculate_password_strength(password):
    """
    Calcula el nivel de fortaleza de una contraseña (0-100).
    
    Args:
        password: Contraseña a evaluar
        
    Returns:
        Puntuación de fortaleza (0-100)
    """
    if not password:
        return 0
    
    strength = 0
    
    # Criterios de fortaleza
    if len(password) >= 6:
        strength += 20
    if len(password) >= 8:
        strength += 15
    if len(password) >= 12:
        strength += 15
    if re.search(r'[a-z]', password):
        strength += 10
    if re.search(r'[A-Z]', password):
        strength += 10
    if re.search(r'[0-9]', password):
        strength += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        strength += 10
    
    return min(strength, 100)
