from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import datetime
from config import Config
from user.models import User, db, bcrypt
from user.routes import user_bp

# Inicialización de JWTManager
jwt = JWTManager()


def create_app():

    app = Flask(__name__)
    # Configuración de la aplicación Flask utilizando la clase Config
    app.config.from_object(Config)
    # Registro del blueprint de rutas de usuario
    app.register_blueprint(user_bp)


    # Inicialización de la base de datos y JWT
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos

    return app

if __name__ == '__main__':  # Ejecuta la aplicación Flask
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080) # Permite que la aplicación sea accesible desde cualquier IP en el puerto 8080