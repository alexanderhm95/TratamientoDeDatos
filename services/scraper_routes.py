from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import asyncio
import requests
from utils.scraper_cedulan import CedulaScraper
from utils.scraper_vehiculo import VehiculoScraper

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

@services_bp.route('/buscar-vehiculo', methods=['POST'])
def buscar_vehiculo():
    """
    Búsqueda de información de vehículo por placa.
    
    Datos esperados:
    {
        "placa": "PSE0881"
    }
    
    Respuesta exitosa:
    {
        "api_url": "https://servicios.axiscloud.ec/...",
        "vehiculo": {...datos completos...},
        "placa_buscada": "PSE0881",
        "timestamp": "..."
    }
    """
    try:
        data = request.get_json()
        placa = data.get('placa', '').strip().upper()
        
        if not placa:
            return jsonify({'error': 'La placa es requerida'}), 400
        
        if len(placa) < 3:
            return jsonify({'error': 'La placa debe tener al menos 3 caracteres'}), 400
        
        # Ejecutar el scraper vehicular
        scraper = VehiculoScraper()
        resultado = asyncio.run(scraper.scrape_cedula(placa))
        
        if resultado['estado'] == 'exitoso':
            # Procesar la respuesta
            api_data = resultado['api_data']
            
            # Si es string (HTML), intentar parsear como JSON
            if isinstance(api_data, str):
                import re
                # Buscar JSON en la respuesta
                json_match = re.search(r'\{.*\}', api_data, re.DOTALL)
                if json_match:
                    try:
                        import json as jsonlib
                        api_data = jsonlib.loads(json_match.group())
                    except:
                        pass
            
            return jsonify({
                'api_url': resultado['api_url'],
                'vehiculo': api_data,
                'placa_buscada': placa,
                'timestamp': resultado['timestamp'],
                'estado': 'exitoso'
            }), 200
        else:
            return jsonify({
                'error': 'No se pudo procesar la búsqueda del vehículo',
                'estado': resultado['estado']
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500