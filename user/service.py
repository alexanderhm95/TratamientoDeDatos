from .models import User, db




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
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        else:
            raise ValueError('Credenciales inválidas.')
    except Exception as e:
        raise e

    
