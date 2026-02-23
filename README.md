# TratamientoDeDatos

## Integrantes (Grupo 6)
- ANDY FERNANDO MOSQUERA CASAMIN
- BYRON ALEXANDER HERRERA MARTINEZ
- LUIS EDUARDO CHILES QUIÑONEZ

---
## Descripción
API RESTful para gestión de usuarios, desarrollada con Flask, contenerizada con Docker y desplegada en Google Cloud Run. Incluye autenticación JWT, validación de datos, manejo de base de datos (SQLite) y respuestas en formato JSON. El proyecto está modularizado y cuenta con pruebas automatizadas (tests) para verificar el funcionamiento de los endpoints.


---


## Instalación y ejecución local
1. Clona el repositorio:
   ```bash
   git clone https://github.com/alexanderhm95/TratamientoDeDatos.git
   cd TratamientoDeDatos
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Crea un archivo `.env` con la variable `SECRET_KEY` (ya incluido en este repo).
4. Ejecuta la API:
   ```bash
   python app.py
   ```

---

## Uso con Docker
1. Construye y levanta la imagen:
   ```bash
   docker-compose up
   ```


---

## Endpoints principales

- **GET /api/health**  
  Verifica el estado de la API.
- **POST /api/users**  
  Crea un usuario nuevo. Requiere JSON con `username`, `email`, `password`, `role`.
- **GET /api/users**  
  Lista todos los usuarios.
- **POST /api/login**  
  Autenticación de usuario. Devuelve token JWT.

---

## Ejemplos de uso con curl

### 1. Verificar salud de la API
```bash
curl https://apigseis-411677847807.us-central1.run.app/api/health
```

### 2. Crear usuario
```bash
curl -X POST https://apigseis-411677847807.us-central1.run.app/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario1","email":"usuario1@correo.com","password":"123456","role":"user"}'
```

### 3. Listar usuarios
```bash
curl https://apigseis-411677847807.us-central1.run.app/api/users
```

### 4. Login
```bash
curl -X POST https://apigseis-411677847807.us-central1.run.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario1","password":"123456"}'
```

---

## Manejo de errores
- Respuestas de error en formato JSON.
- Ejemplo de error por credenciales inválidas:
  ```json
  {"message": "Invalid credentials"}
  ```
- Ejemplo de error por usuario existente:
  ```json
  {"message": "El nombre de usuario ya existe."}
  ```

---

## Despliegue en Google Cloud Run
1. Autentica y configura Google Cloud SDK.
2. Construye y sube la imagen a Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/mcitd2026/flask_tratamiento_datos
   ```
3. Despliega en Cloud Run:
   ```bash
   gcloud run deploy apigseis --image gcr.io/mcitd2026/flask_tratamiento_datos --platform managed --region us-central1 --allow-unauthenticated
   ```
4. Accede a la API pública:  
   https://apigseis-411677847807.us-central1.run.app/

---

## Evidencia requerida

**Branchs**

<div align="center">
  <img src="evidencia/branch.png" width="800" height="450" alt="Evidencia API">
</div>

**API funcionando localmente**

<div align="center">
  <img src="evidencia/localhost.png" width="800" height="450" alt="Evidencia API">
</div>

**Construcción de imagen Docker**

<div align="center">
  <img src="evidencia/buildDocker.png" width="800" height="400" alt="Evidencia API">
</div>

**Contenedor ejecutándose**

<div align="center">
  <img src="evidencia/docker.png" width="800" height="400" alt="Evidencia API">
</div>

**Prueba curl exitosa**

<div align="center">
  <img src="evidencia/health.png" width="800" height="200" alt="Evidencia API">
</div>
<div align="center">
  <img src="evidencia/listUsers.png" width="800" height="450" alt="Evidencia API">
</div>
<div align="center">
  <img src="evidencia/createUser.png" width="800" height="250" alt="Evidencia API">
</div>
<div align="center">
  <img src="evidencia/login.png" width="800" height="200" alt="Evidencia API">
</div>

**API desplegada en Cloud**

<div align="center">
  <img src="evidencia/cloud.png" width="800" height="300" alt="Evidencia API">
</div>
<div align="center">
  <img src="evidencia/cloud2.png" width="800" height="200" alt="Evidencia API">
</div>