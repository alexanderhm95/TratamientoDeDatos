from .models import User, db

def create_user(username, email, password, role='user'):
    """Crea un nuevo usuario en la base de datos."""
    try:
        if User.query.filter_by(username=username).first():
            raise ValueError('El nombre de usuario ya existe.')

        if User.query.filter_by(email=email).first():
            raise ValueError('El correo electrónico ya está registrado.')

        # Verificacion de email
        if email.count('@') != 1 or email.rfind('.') < email.find('@'):
            raise ValueError('El correo electrónico no es válido.')

        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return user

    except Exception as e:
        db.session.rollback()  # Revertir la transacción en caso de error
        raise e


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

    