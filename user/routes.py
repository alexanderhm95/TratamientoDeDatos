from flask import jsonify, request
from flask import Blueprint
from .service import create_user, list_users, login_user
from .validators import validate_email
from .exceptions import ValidationError, InvalidCredentialsError
from .models import User, db
from flask import render_template, redirect, url_for
from flask_mail import Message
from flask import current_app
import secrets
import string

user_bp = Blueprint('user', __name__)

# Importar limiter y cache desde app
def get_limiter():
    from app import limiter
    return limiter

def get_cache():
    from app import cache
    return cache

"""
Ruta raíz que redirige a login o home según si está autenticado.
"""
@user_bp.route('/', methods=['GET'])
def index():
    # La redirección se maneja en JavaScript del cliente según el token en localStorage
    return redirect(url_for('user.home'))


"""
Ruta para mostrar la página home.
"""
@user_bp.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


"""
Ruta para verificar el estado de la API. Esta ruta responde a solicitudes GET y devuelve un mensaje indicando que la API está saludable.
"""
@user_bp.route('/api/health', methods=['GET']) # Define una ruta para verificar el estado de la API
def health_check():
    return jsonify({'status': 'ok', 'message': 'API is healthy'}) # Devuelve un mensaje indicando que la API está saludable


"""
Ruta para crear un nuevo usuario. Esta ruta responde a solicitudes POST, recibe datos en formato JSON y utiliza la función create_user para agregar un nuevo usuario a la base de datos.
RATE LIMIT: 5 intentos por minuto por IP (prevención de spam)
"""
@user_bp.route('/api/users', methods=['POST'])
@get_limiter().limit("5 per minute")  # Max 5 registros por minuto por IP
def create_user_route():
    try:
        data = request.get_json() # Obtiene los datos enviados en formato JSON
        username = data.get('username') # Extrae el nombre de usuario del JSON
        email = data.get('email') # Extrae el correo electrónico del JSON
        password = data.get('password') # Extrae la contraseña del JSON
        role = data.get('role', 'user') # Extrae el rol del usuario del JSON, por defecto es 'user'
        
        user = create_user(username, email, password, role) # Llama a la función create_user para crear un nuevo usuario en la base de datos
        return jsonify(user.to_dict()), 201 # Devuelve la información del nuevo usuario en formato JSON con un código de estado 201 (Creado)
    except ValidationError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'Error al crear el usuario'}), 500


"""
Ruta para listar todos los usuarios. Esta ruta responde a solicitudes GET y devuelve una lista de todos los usuarios en la base de datos en formato JSON.
CACHE: 5 minutos (mejora de rendimiento)
RATE LIMIT: 30 intentos por hora
"""
@user_bp.route('/api/users', methods=['GET'])
@get_limiter().limit("30 per hour")  # Max 30 solicitudes por hora por IP
def list_users_route():
    # Aplicar cache manualmente en tiempo de ejecución
    cache = get_cache()
    cache_key = 'all_users_list'
    
    # Intentar obtener del cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return jsonify(cached_result)
    
    # Si no está en cache, obtener de la BD
    users = list_users()
    result = [user.to_dict() for user in users]
    
    # Guardar en cache por 5 minutos
    cache.set(cache_key, result, timeout=300)
    
    return jsonify(result)



"""
Ruta para mostrar la página de login (HTML).
"""
@user_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('auth/auth.html')


"""
Ruta para mostrar la página de registro (HTML).
"""
@user_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('auth/register.html')


"""
Ruta para mostrar la página de recuperación de contraseña (HTML).
"""
@user_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    return render_template('auth/forgot-password.html')


"""
Ruta para procesar la solicitud de recuperación de contraseña.
RATE LIMIT: 3 intentos por hora por IP (prevención de spam)
"""
@user_bp.route('/api/forgot-password', methods=['POST'])
@get_limiter().limit("3 per hour")  # Max 3 intentos de recuperación por hora
def forgot_password_route():
    try:
        data = request.get_json()
        email = data.get('email', '').strip() if data.get('email') else ''
        
        # Validar email
        email = validate_email(email)
        
        user = User.query.filter_by(email=email).first()
        if user:
            # Generar contraseña temporal aleatoria
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Actualizar la contraseña del usuario
            user.password = temp_password
            db.session.add(user)
            db.session.commit()
            
            # Enviar correo con la contraseña temporal
            try:
                msg = Message(
                    subject='Tu Contraseña Temporal - Tratamiento de Datos',
                    recipients=[email],
                    html=f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                                <h2 style="color: #0d6efd;">Contraseña Temporal</h2>
                                <p>Hola <strong>{user.username}</strong>,</p>
                                <p>Tu contraseña temporal es:</p>
                                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                                    <p style="font-size: 1.2em; font-weight: bold; font-family: monospace; color: #0d6efd; margin: 0;">
                                        {temp_password}
                                    </p>
                                </div>
                                <p><strong>⚠️ Por seguridad:</strong></p>
                                <ul>
                                    <li>Copia esta contraseña exactamente (sin espacios)</li>
                                    <li>Inicia sesión con tu usuario y esta contraseña</li>
                                    <li>Cambia tu contraseña a una más segura en tu perfil</li>
                                </ul>
                                <p style="color: #666; font-size: 0.9em;">Si no solicitaste esto, contacta al administrador inmediatamente.</p>
                                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                                <p style="color: #999; font-size: 0.8em; text-align: center;">
                                    © 2026 Tratamiento de Datos. Todos los derechos reservados.
                                </p>
                            </div>
                        </body>
                    </html>
                    """
                )
                current_app.extensions['mail'].send(msg)
            except Exception as e:
                pass  # El email no es crítico, continuar sin errores
            
            return jsonify({'message': 'Se ha enviado una contraseña temporal a tu correo electrónico'}), 200
        else:
            return jsonify({'message': 'Si el email existe, recibirás una contraseña temporal'}), 200
    except ValidationError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'Error al procesar la solicitud'}), 500


"""
Ruta para iniciar sesión. Esta ruta responde a solicitudes POST, recibe datos en formato JSON y utiliza la función login_user para verificar las credenciales del usuario y devolver un token JWT si son correctas.
RATE LIMIT: 5 intentos por minuto por IP (prevención de brute force)
"""
@user_bp.route('/api/login', methods=['POST'])
@get_limiter().limit("5 per minute")  # Max 5 intentos de login por minuto por IP
def login_user_route():
    try:
        data = request.get_json() # Obtiene los datos enviados en formato JSON
        username = data.get('username') # Extrae el nombre de usuario del JSON
        password = data.get('password') # Extrae la contraseña del JSON
        
        user = login_user(username, password) # Llama a la función login_user para verificar las credenciales del usuario
        if user:
            token = user.generate_jwt() # Genera un token JWT para el usuario autenticado
            return jsonify({'token': token}) # Devuelve el token JWT en formato JSON
        else:
            return jsonify({'message': 'Credenciales inválidas'}), 401
    except InvalidCredentialsError as e:
        return jsonify({'message': str(e)}), 401
    except ValidationError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'Error al procesar el login'}), 500

