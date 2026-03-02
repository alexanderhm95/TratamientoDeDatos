from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import asyncio
import requests
from utils.scraper_cedulan import CedulaScraper

services_bp = Blueprint('services', __name__, url_prefix='/api')


@services_bp.route('/verificar-api-cedula', methods=['GET'])
def verificar_api_cedula():
    """
    Verifica si el API de búsqueda de cédula está disponible.
    No requiere autenticación (es solo verificación de estado).
    """
    try:
        # URL del API SRI que usamos
        api_url = "https://srienlinea.sri.gob.ec/movil-servicios/api/v1.0/deudas/porDenominacion/TEST/?tipoPersona=N&resultados=1"
        
        # Intentar hacer una solicitud al API con timeout corto
        response = requests.get(api_url, timeout=3)
        
        if response.status_code == 200:
            return jsonify({
                'disponible': True,
                'mensaje': 'API disponible',
                'servicio': 'busqueda-cedula'
            }), 200
        else:
            return jsonify({
                'disponible': False,
                'mensaje': 'API no responde correctamente',
                'status_code': response.status_code
            }), 503
            
    except requests.exceptions.Timeout:
        return jsonify({
            'disponible': False,
            'mensaje': 'Timeout al verificar API'
        }), 503
    except Exception as e:
        return jsonify({
            'disponible': False,
            'mensaje': f'Error al verificar API: {str(e)}'
        }), 503


@services_bp.route('/buscar-cedula', methods=['POST'])
def buscar_cedula():
    """
    Búsqueda de cédula por nombre.
    
    Datos esperados:
    {
        "nombre": "Juan Pérez González"
    }
    
    Respuesta exitosa:
    {
        "api_url": "https://srienlinea.sri.gob.ec/...",
        "cedulas": [
            {
                "identificacion": "0123456789",
                "nombreComercial": "JUAN PÉREZ GONZÁLEZ",
                "clase": "PERSONA NATURAL"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({'error': 'El nombre es requerido'}), 400
        
        if len(nombre) < 3:
            return jsonify({'error': 'El nombre debe tener al menos 3 caracteres'}), 400
        
        # Ejecutar el scraper
        scraper = CedulaScraper()
        resultado = asyncio.run(scraper.scrape_cedula(nombre))
        
        if resultado['estado'] == 'exitoso':
            return jsonify({
                'api_url': resultado['api_url'],
                'cedulas': resultado['api_data'],
                'nombre_buscado': nombre,
                'timestamp': resultado['timestamp']
            }), 200
        else:
            return jsonify({
                'error': 'No se pudo procesar la búsqueda',
                'estado': resultado['estado']
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500
