from .models import User, db
from .validators import (
    validate_email,
    validate_username,
    validate_password,
    validate_login_input
)
from .exceptions import (
    ValidationError,
    UsernameError,
    EmailError,
    PasswordError,
    InvalidCredentialsError,
    UserAlreadyExistsError
)


# ==================== FUNCIONES DE AUTENTICACIÓN ====================

def create_user(username, email, password, role='user'):
    """Crea un nuevo usuario en la base de datos."""
    try:
        # Validar todos los campos de entrada
        username = validate_username(username)
        email = validate_email(email)
        password = validate_password(password)
        
        # Verificar que el username no exista
        if User.query.filter_by(username=username).first():
            raise UserAlreadyExistsError('El nombre de usuario ya está en uso.')

        # Verificar que el email no exista
        if User.query.filter_by(email=email).first():
            raise UserAlreadyExistsError('El correo electrónico ya está registrado.')

        # Crear el usuario
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return user

    except (ValidationError, UserAlreadyExistsError):
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError('Error al crear el usuario') from e


def list_users():
    """Devuelve una lista de todos los usuarios en la base de datos."""
    try:
        if User.query.count() == 0:
            raise ValueError('No hay usuarios registrados.')
        return User.query.all()
    except Exception as e:
        raise e
    
    
def login_user(username, password):
    """Verifica las credenciales del usuario y devuelve el usuario si son correctas."""
    try:
        # Validar entrada
        username, password = validate_login_input(username, password)
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            password_valid = user.check_password(password)
            if password_valid:
                return user
            else:
                raise InvalidCredentialsError('Credenciales inválidas.')
        else:
            raise InvalidCredentialsError('Credenciales inválidas.')
    except (ValidationError, InvalidCredentialsError):
        raise
    except Exception as e:
        raise InvalidCredentialsError('Error al verificar credenciales') from e

    