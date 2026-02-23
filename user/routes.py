from flask import jsonify, request
from flask import Blueprint
from .service import create_user, list_users, login_user

user_bp = Blueprint('user', __name__)

"""
Ruta para verificar el estado de la API. Esta ruta responde a solicitudes GET y devuelve un mensaje indicando que la API está saludable.
"""
@user_bp.route('/api/health', methods=['GET']) # Define una ruta para verificar el estado de la API
def health_check():
    return jsonify({'status': 'ok', 'message': 'API is healthy'}) # Devuelve un mensaje indicando que la API está saludable



"""
Ruta para listar todos los usuarios. Esta ruta responde a solicitudes GET y devuelve una lista de todos los usuarios en la base de datos en formato JSON.
"""
@user_bp.route('/api/users', methods=['GET']) # Define una ruta para listar todos los usuarios
def list_users_route():
    users = list_users() # Llama a la función list_users para obtener una lista de todos los usuarios en la base de datos
    return jsonify([user.to_dict() for user in users]) # Devuelve la lista de usuarios en formato JSON


