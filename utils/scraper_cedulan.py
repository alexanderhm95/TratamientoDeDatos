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


class CedulaScraper:
    """Scraper para la página de consulta de cédulas de Registro Civil de Ecuador."""
    
    def __init__(self):
        self.url = "https://www.ecuadorlegalonline.com/consultas/registro-civil/buscar-numero-de-cedula-por-nombre/"
        self.results = []
    
    async def scrape_cedula(self, cedula):
        """
        Scrapea la información de una persona por su cédula.
        
        Args:
            cedula: Cédula de la persona (ej: 1720000001)
            
        Returns:
            Diccionario con la información de la persona
        """
        api_base = "https://apps.ecuadorlegalonline.com/modulo/consultar-cedulanombre.php?nombres"

        async with async_playwright() as p:
            # Paso 1: Descargar y lanzar navegador
            print("📱 Paso 1: Lanzando navegador Chromium...")
            browser = await p.chromium.launch(headless=True)  # headless=False para ver el navegador
            page = await browser.new_page()
            
            # Paso 2: Navegar a la página
            print(f"📄 Paso 2: Navegando a {self.url}")
            await page.goto(self.url, wait_until="domcontentloaded", timeout=15000)
           
           # Esperar un poco para asegurarse de que la página esté completamente cargada
            await asyncio.sleep(5)
           
            
            # Paso 3.5: Cerrar el dialog fc-monetization-dialog-container si existe
            print("🗑️  Paso 3.5: Cerrando popup/dialog si existe...")
            try:
                # Intentar encontrar y cerrar el dialog
                dialog = await page.query_selector('.fc-monetization-dialog-container')
                if dialog:
                    # Buscar botón cerrar dentro del dialog
                    close_button = await page.query_selector('.fc-monetization-dialog-container button.fc-button, .fc-monetization-dialog-container [class*="close"], .fc-monetization-dialog-container [aria-label*="close"]')
                    if close_button:
                        await close_button.click()
                        await asyncio.sleep(0.5)
                    else:
                        # Si no hay botón, eliminar el dialog directamente
                        await page.evaluate('() => { const el = document.querySelector(".fc-monetization-dialog-container"); if (el) el.remove(); }')
                else:
                    print("   ℹ️  No hay dialog visible")
            except Exception as e:
                print(f"   ⚠️  No se pudo cerrar el dialog: {e}")
            
            # Pequeña pausa para que se estabilice la página
            await asyncio.sleep(0.5)
            print("✓ Página cargada exitosamente")
            
            # Paso 5: Limpiar y escribir la cédula
            print(f"✏️  Paso 5: Escribiendo cédula: {cedula}")
            await page.get_by_role("textbox", name="Escribe aquí…").click()
            await page.get_by_role("textbox", name="Escribe aquí…").fill(cedula)
            
            print(f"✓ Cédula '{cedula}' ingresada")

            
            # Paso 5.5: Probar ambas APIs y devolver la que funciona
            print("🔍 Paso 5.5: Probando APIs...")
            captured_urls = []
            
            def handle_request(request):
                # Solo capturar los APIs del sitio deseado
                if api_base in request.url:
                    captured_urls.append(request.url)
                    print(f"   📡 API detectado: {request.url}")
            
            # Registrar listener para todas las requests
            page.on("request", handle_request)
            
            # Hacer clic en el botón Consultar
            print("🖱️  Haciendo clic en 'Consultar'...")
            await page.get_by_role("button", name="Consultar").click()
            await asyncio.sleep(1.5)
            
            # Probar los APIs capturados
            working_api = None
            if captured_urls:
                print("🧪 Probando APIs capturados:")
                for api_url in captured_urls:
                    try:
                        print(f"   Intentando: {api_url}")
                        response = await page.request.get(api_url)
                        if response.status == 200:
                            try:
                                # Intentar JSON primero
                                data = await response.json()
                                if data:
                                    print(f"   ✓ API funcionando (JSON): {api_url}")
                                    working_api = {
                                        'url': api_url,
                                        'status': response.status,
                                        'data': data,
                                        'type': 'json'
                                    }
                                    break
                            except:
                                # Si no es JSON, obtener como texto
                                text_data = await response.text()
                                if text_data and len(text_data) > 50:  # Si tiene contenido significativo
                                    print(f"   ✓ API funcionando (HTML/Texto): {api_url}")
                                    working_api = {
                                        'url': api_url,
                                        'status': response.status,
                                        'data': text_data[:200],  # Primeros 200 caracteres
                                        'type': 'html'
                                    }
                                    break
                                else:
                                    print(f"   ✗ Respuesta vacía: {api_url}")
                    except Exception as e:
                        print(f"   ✗ Error en API: {e}")
            
            if working_api:
                print(f"\n✓ API válida encontrada:")
                print(f"   URL: {working_api['url']}")
                print(f"   Tipo: {working_api['type']}")
                print(f"   Status: {working_api['status']}")
                print(f"   Datos: {working_api['data']}")
                
                # Cerrar navegador y devolver el API
                await browser.close()
                return {
                    'nombre_busqueda': cedula,
                    'timestamp': datetime.now().isoformat(),
                    'api_url': working_api['url'],
                    'api_data': working_api['data'],
                    'estado': 'exitoso'
                }
            else:
                print("   ✗ Ningún API funcionó correctamente")
                await browser.close()
                return {
                    'nombre_busqueda': cedula,
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
    scraper = CedulaScraper()
    
    # Nombres de ejemplo a buscar
    nombres = [
        "Herrera Martinez Byron Alexander",
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
