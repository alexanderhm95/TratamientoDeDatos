from flask import jsonify, request
from flask import Blueprint
from .service import create_user, list_users, login_user

user_bp = Blueprint('user', __name__)

"""
Ruta para verificar el estado de la API. Esta ruta responde a solicitudes GET y devuelve un mensaje indicando que la API está saludable.
"""
@max_retries(3)
@user_bp.route('/api/health', methods=['GET']) # Define una ruta para verificar el estado de la API
def health_check():
    return jsonify({'status': 'ok', 'message': 'API is healthy'}) # Devuelve un mensaje indicando que la API está saludable
"""

Ruta para crear un nuevo usuario. Esta ruta responde a solicitudes POST, recibe datos en formato JSON y utiliza la función create_user para agregar un nuevo usuario a la base de datos.
"""
@user_bp.route('/api/users', methods=['POST']) # Define una ruta para crear un nuevo usuario
def create_user_route():
    data = request.get_json() # Obtiene los datos enviados en formato JSON
    username = data.get('username') # Extrae el nombre de usuario del JSON
    email = data.get('email') # Extrae el correo electrónico del JSON
    password = data.get('password') # Extrae la contraseña del JSON
    role = data.get('role', 'user') # Extrae el rol del usuario del JSON, por defecto es 'user'
    
    user = create_user(username, email, password, role) # Llama a la función create_user para crear un nuevo usuario en la base de datos
    return jsonify(user.to_dict()), 201 # Devuelve la información del nuevo usuario en formato JSON con un código de estado 201 (Creado)


"""

Ruta para listar todos los usuarios. Esta ruta responde a solicitudes GET y devuelve una lista de todos los usuarios en la base de datos en formato JSON.
"""
@user_bp.route('/api/users', methods=['GET']) # Define una ruta para listar todos los usuarios
def list_users_route():
    users = list_users() # Llama a la función list_users para obtener una lista de todos los usuarios en la base de datos
    return jsonify([user.to_dict() for user in users]) # Devuelve la lista de usuarios en formato JSON


"""
Ruta para iniciar sesión. Esta ruta responde a solicitudes POST, recibe datos en formato JSON y utiliza la función login_user para verificar las credenciales del usuario y devolver un token JWT si son correctas.
"""
@user_bp.route('/api/login', methods=['POST']) # Define una ruta para iniciar sesión
def login_user_route():
    data = request.get_json() # Obtiene los datos enviados en formato JSON
    username = data.get('username') # Extrae el nombre de usuario del JSON
    password = data.get('password') # Extrae la contraseña del JSON
    
    user = login_user(username, password) # Llama a la función login_user para verificar las credenciales del usuario
    if user:
        token = user.generate_jwt() # Genera un token JWT para el usuario autenticado
        return jsonify({'token': token}) # Devuelve el token JWT en formato JSON
    else:
        return jsonify({'message': 'Invalid credentials'}), 401 # Devuelve un mensaje de error con un código de estado 401 (No autorizado) si las credenciales son inválidas

