import requests

def test_health_check():
    response = requests.get('http://localhost:8000/api/health') # Realiza una solicitud GET a la ruta de verificación de salud
    assert response.status_code == 200 # Verifica que el código de estado sea 200 (OK)
    data = response.json() # Convierte la respuesta a formato JSON
    assert data['status'] == 'ok' # Verifica que el estado en la respuesta sea 'ok'
    assert data['message'] == 'API is healthy' # Verifica que el mensaje en la respuesta sea 'API is healthy'


def test_create_user():
    user_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword',
        'role': 'user'
    }
    response = requests.post('http://localhost:8000/api/users', json=user_data)
    print(response.status_code) # Imprime el código de estado de la respuesta
    assert response.status_code == 201 # Verifica que el código de estado sea 201 (Creado)
    data = response.json() # Convierte la respuesta a formato JSON
    assert data['username'] == user_data['username'] # Verifica que el nombre de usuario en la respuesta sea el mismo que el enviado
    assert data['email'] == user_data['email'] # Verifica que el correo electrónico en la respuesta sea el mismo que el enviado

def test_list_users():
    response = requests.get('http://localhost:8000/api/users') # Realiza una solicitud GET a la ruta de listado de usuarios
    print(response.status_code) # Imprime el código de estado de la respuesta
    print(response.json()) # Imprime el contenido de la respuesta en formato JSON
    assert response.status_code == 200 # Verifica que el código de estado sea 200 (OK)
    data = response.json() # Convierte la respuesta a formato JSON
    assert isinstance(data, list) # Verifica que la respuesta sea una lista
    assert len(data) > 0 # Verifica que la lista de usuarios no esté vacía


if __name__ == '__main__':
    test_health_check() # Ejecuta la función de prueba para verificar la salud de la API
    test_list_users() # Ejecuta la función de prueba para listar los usuarios
    #test_create_user() # Ejecuta la función de prueba para crear un usuario
