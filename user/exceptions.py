"""
Excepciones personalizadas para el módulo de usuarios.
"""

class ValidationError(ValueError):
    """Excepción lanzada cuando hay un error de validación."""
    pass


class UsernameError(ValidationError):
    """Excepción lanzada cuando hay un error con el nombre de usuario."""
    pass


class EmailError(ValidationError):
    """Excepción lanzada cuando hay un error con el correo electrónico."""
    pass


class PasswordError(ValidationError):
    """Excepción lanzada cuando hay un error con la contraseña."""
    pass


class UserNotFoundError(ValidationError):
    """Excepción lanzada cuando el usuario no se encuentra."""
    pass


class InvalidCredentialsError(ValidationError):
    """Excepción lanzada cuando las credenciales son inválidas."""
    pass


class UserAlreadyExistsError(ValidationError):
    """Excepción lanzada cuando el usuario ya existe."""
    pass
