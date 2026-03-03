"""
Script de scraping con Playwright para la página de consulta de cédulas de Registro Civil de Ecuador.
URL: https://www.ecuadorlegalonline.com/consultas/registro-civil/buscar-numero-de-cedula-por-nombre/

Este script automatiza el proceso de:
1. Abrir el navegador
2. Navegar a la página
3. Llenar el formulario con una cédula
4. Cerrar el popup/dialog si aparece
5. Enviar el formulario
6. Esperar y extraer los resultados
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


class VehiculoScraper:
    """Scraper para la página de consulta de vehículos del Registro Civil de Ecuador."""
    
    def __init__(self):
        self.url = "https://servicios.axiscloud.ec/CRV/?ps_empresa=05"
        self.results = []
    
    async def scrape_cedula(self, placa):
        """
        Scrapea la información de un vehículo por su placa.
        
        Args:
            placa: Placa del vehículo (ej: PSE0881)
            
        Returns:
            Diccionario con la información del vehículo
        """
        api_base = "https://servicios.axiscloud.ec/CRV/paginas/datosVehiculo.jsp"

        async with async_playwright() as p:
            # Paso 1: Descargar y lanzar navegador
            print("📱 Paso 1: Lanzando navegador Chromium...")
            browser = await p.chromium.launch(headless=True)  # headless=False para ver el navegador
            page = await browser.new_page()
            
            # Paso 2: Navegar a la página
            print(f"📄 Paso 2: Navegando a {self.url}")
            await page.goto(self.url, wait_until="domcontentloaded", timeout=15000)
           
           # Esperar hasta que "Consulta de Vehículo" esté visible
            await page.wait_for_selector("text=Consulta de Vehículo", timeout=10000)

            # Damos click sobre el input de placa y llenamos el formulario
            await page.get_by_role("textbox", name="Placa/VIN (Chasís)/Motor:").click()
            await page.get_by_role("textbox", name="Placa/VIN (Chasís)/Motor:").fill(placa)

            # Capturar respuestas de APIs (con cookies y headers del navegador)
            captured_response = {}
            
            def handle_response(response):
                # Capturar solo el API que nos interesa
                if api_base in response.url:
                    captured_response['url'] = response.url
                    captured_response['status'] = response.status
                    captured_response['response'] = response
                    print(f"   📡 API detectado: {response.url}")

            # Registrar listener ANTES de hacer click
            page.on("response", handle_response)
            
            await page.get_by_role("button", name="Buscar").click()

            # Esperar hasta que Consultando se oculte
            await page.wait_for_selector("text=Consultando", state="hidden", timeout=10000)

            # Esperar un poco extra para asegurar que la respuesta se ha capturado
            await asyncio.sleep(1)
            
            # Procesar la respuesta capturada
            working_api = None
            if captured_response:
                print("🧪 Procesando respuesta capturada:")
                try:
                    response = captured_response['response']
                    print(f"   Intentando: {captured_response['url']}")
                    
                    if captured_response['status'] == 200:
                        try:
                            # Intentar JSON primero
                            data = await response.json()
                            if data:
                                print(f"   ✓ API funcionando (JSON): {captured_response['url']}")
                                working_api = {
                                    'url': captured_response['url'],
                                    'status': captured_response['status'],
                                    'data': data,
                                    'type': 'json'
                                }
                        except:
                            # Si no es JSON, obtener como texto con manejo de encoding
                            try:
                                # Intentar Latin-1 primero (encoding común en servidores ecuatorianos)
                                body = await response.body()
                                text_data = body.decode('latin-1', errors='replace')
                            except:
                                # Si falla, intentar UTF-8
                                text_data = await response.text()
                            
                            if text_data and len(text_data) > 10:  # Si tiene contenido significativo
                                print(f"   ✓ API funcionando (HTML/Texto): {captured_response['url']}")
                                working_api = {
                                    'url': captured_response['url'],
                                    'status': captured_response['status'],
                                    'data': text_data,
                                    'type': 'html'
                                }
                            else:
                                print(f"   ✗ Respuesta vacía: {captured_response['url']}")
                except Exception as e:
                    print(f"   ✗ Error procesando respuesta: {e}")
            
            if working_api:
                print(f"\n✓ API válida encontrada:")
                print(f"   URL: {working_api['url']}")
                print(f"   Tipo: {working_api['type']}")
                print(f"   Status: {working_api['status']}")
                print(f"   Datos: {working_api['data']}")
                
                # Cerrar navegador y devolver el API
                await browser.close()
                return {
                    'nombre_busqueda': placa,
                    'timestamp': datetime.now().isoformat(),
                    'api_url': working_api['url'],
                    'api_data': working_api['data'],
                    'estado': 'exitoso'
                }
            else:
                print("   ✗ Ningún API funcionó correctamente")
                await browser.close()
                return {
                    'nombre_busqueda': placa,
                    'timestamp': datetime.now().isoformat(),
                    'api_url': None,
                    'api_data': None,
                    'estado': 'error'
                }

    def save_results(self, filename='scraping_results.json'):
        """Guarda los resultados en un archivo JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultados guardados en: {filename}")


# Función principal para ejecutar el scraper
async def main():
    """Función principal."""
    
    # Crear instancia del scraper
    scraper = VehiculoScraper()
    
    # Nombres de ejemplo a buscar
    nombres = [
        "PSE0881",
    ]
    
    # Ejecutar scraping
    resultado = await scraper.scrape_cedula(nombres[0])
    
    # Guardar resultado
    print(f"\n{'='*60}")
    print(f"RESULTADO DEL SCRAPING")
    print(f"{'='*60}")
    
    if resultado['estado'] == 'exitoso':
        print(f"✓ Búsqueda exitosa")
        print(f"  Nombre: {resultado['nombre_busqueda']}")
        print(f"  API URL: {resultado['api_url']}")
        print(f"  Cédulas encontradas: {len(resultado['api_data'])}")
        
        # Guardar resultado en JSON
        with open('cedulas_scrapidas.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultado guardado en: cedulas_scrapidas.json")
    else:
        print(f"✗ Error en la búsqueda")
    
    return resultado


if __name__ == "__main__":
    # Ejecutar el scraper
    asyncio.run(main())
