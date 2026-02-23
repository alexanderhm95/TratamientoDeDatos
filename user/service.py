from .models import User, db




def list_users():
    """Devuelve una lista de todos los usuarios en la base de datos."""
    try:
        if User.query.count() == 0:
            raise ValueError('No hay usuarios registrados.')
        return User.query.all()
    except Exception as e:
        raise e
    
