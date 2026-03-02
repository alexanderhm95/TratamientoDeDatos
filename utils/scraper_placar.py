"""
Script de scraping con Playwright para la página de consulta de vehículos por placa en Ecuador.
URL: https://www.ecuadorlegalonline.com/consultas/agencia-nacional-de-transito/consultar-a-quien-pertenece-un-vehiculo-por-placa-ant/

Este script automatiza el proceso de:
1. Abrir el navegador
2. Navegar a la página
3. Llenar el formulario con una placa
4. Cerrar el popup/dialog si aparece
5. Enviar el formulario
6. Esperar y extraer los resultados
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


class VehicleScraperANT:
    """Scraper para la página de consulta de vehículos por placa de la ANT Ecuador."""
    
    def __init__(self):
        self.url = "https://consultasecuador.com/en-linea/transito/consultar-propietario-vehiculo"
        self.results = []
    
    async def scrape_vehicle(self, placa):
        """
        Scrapea la información de un vehículo por su placa.
        
        Args:
            placa: Placa del vehículo (ej: PIZ-0001)
            
        Returns:
            Diccionario con la información del vehículo
        """
        async with async_playwright() as p:
            # Paso 1: Descargar y lanzar navegador
            print("📱 Paso 1: Lanzando navegador Chromium...")
            browser = await p.chromium.launch(headless=False)  # headless=False para ver el navegador
            page = await browser.new_page()
            
            # Paso 2: Navegar a la página
            print(f"📄 Paso 2: Navegando a {self.url}")
            await page.goto(self.url, wait_until="networkidle")
           
           # Esperar un poco para asegurarse de que la página esté completamente cargada
            await asyncio.sleep(5)
           
            
            # Paso 3.5: Cerrar el dialog fc-monetization-dialog-container si existe
            print("🗑️  Paso 3.5: Cerrando popup/dialog si existe...")
            try:
                # Intentar encontrar y cerrar el dialog
                dialog = await page.query_selector('.fc-monetization-dialog-container')
                if dialog:
                    print("   ✓ Dialog encontrado, intentando cerrarlo...")
                    
                    # Buscar botón cerrar dentro del dialog
                    close_button = await page.query_selector('.fc-monetization-dialog-container button.fc-button, .fc-monetization-dialog-container [class*="close"], .fc-monetization-dialog-container [aria-label*="close"]')
                    
                    if close_button:
                        print("   ✓ Botón cerrar encontrado, haciendo clic...")
                        await close_button.click()
                        await asyncio.sleep(0.5)
                    else:
                        # Si no hay botón, eliminar el dialog directamente
                        print("   ✓ Eliminando dialog del DOM...")
                        await page.evaluate('() => { const el = document.querySelector(".fc-monetization-dialog-container"); if (el) el.remove(); }')
                    
                    print("✓ Dialog cerrado/eliminado exitosamente")
                else:
                    print("   ℹ️  No hay dialog visible")
            except Exception as e:
                print(f"   ⚠️  No se pudo cerrar el dialog: {e}")
            
            # Pequeña pausa para que se estabilice la página
            await asyncio.sleep(0.5)
            await page.pause()  # Pausa para depuración
            
            # Paso 5: Limpiar y escribir la placa
            print(f"✏️  Paso 5: Escribiendo placa: {placa}")
            await page.get_by_role("textbox", name="Registre Placa del vehículo").click()
            await page.get_by_role("textbox", name="Registre Placa del vehículo").fill(placa)
            print(f"✓ Placa '{placa}' ingresada")

            
            # Paso 5.5: Probar ambas APIs y devolver la que funciona
            print("🔍 Paso 5.5: Probando APIs...")
            captured_urls = []
            api_base = "https://www.ecuadorlegalonline.com/modulo/sri/matriculacion/"
            
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
            else:
                print("   ✗ Ningún API funcionó correctamente")
            
            page.remove_listener("request", handle_request)

            
            # Paso 6: Encontrar y hacer clic en el botón enviar
            print("🔍 Paso 6: Buscando botón de envío...")
            submit_button = None
            
            # Intentar múltiples selectores para el botón
            button_selectors = [
                'button[type="submit"]',
                'button:has-text("Consultar")',
                'button:has-text("Enviar")',
                'button:has-text("Buscar")',
                'input[type="submit"]',
                'a[onclick*="consultar"]'
            ]
            
            for selector in button_selectors:
                try:
                    submit_button = await page.query_selector(selector)
                    if submit_button:
                        print(f"✓ Botón encontrado con selector: {selector}")
                        break
                except:
                    pass
            
            if not submit_button:
                print("✗ No se encontró el botón de envío")
                await browser.close()
                return None
            
            # Paso 7: Hacer clic en el botón
            print("🖱️  Paso 7: Haciendo clic en enviar...")
            await submit_button.click()
            print("✓ Botón clicado")
            
            # Paso 8: Esperar los resultados
            print("⏳ Paso 8: Esperando resultados (8 segundos)...")
            await asyncio.sleep(8)  # Esperar a que carguen los resultados
            
            # Paso 9: Extraer los resultados
            print("📊 Paso 9: Extrayendo información...")
            resultado = {
                'placa': placa,
                'timestamp': datetime.now().isoformat(),
                'datos_encontrados': False,
                'informacion': {}
            }
            
            # Intentar extraer información del resultado
            try:
                # Buscar elementos comunes que contienen la información
                selectors_info = {
                    'propietario': ['text=Propietario:', 'text=PROPIETARIO'],
                    'marca': ['text=Marca:', 'text=MARCA'],
                    'modelo': ['text=Modelo:', 'text=MODELO'],
                    'color': ['text=Color:', 'text=COLOR'],
                    'año': ['text=Año:', 'text=AÑO'],
                    'tipo_vehiculo': ['text=Tipo de Vehículo:', 'text=TIPO']
                }
                
                # Obtener todo el contenido de la página
                content = await page.content()
                
                # Buscar si hay información de resultado
                if 'error' not in content.lower() and 'no encontrado' not in content.lower():
                    resultado['datos_encontrados'] = True
                    
                    # Extraer texto visible
                    texto_visible = await page.inner_text('body')
                    resultado['informacion']['texto_completo'] = texto_visible
                
            except Exception as e:
                print(f"⚠️  Error al extraer información: {e}")
            
            # Paso 10: Cerrar el navegador
            print("🔴 Paso 10: Cerrando navegador...")
            await browser.close()
            print("✓ Navegador cerrado")
            
            return resultado
    
    async def scrape_multiple(self, placas):
        """
        Scrapea múltiples vehículos.
        
        Args:
            placas: Lista de placas a buscar
            
        Returns:
            Lista de resultados
        """
        self.results = []
        
        print(f"\n{'='*60}")
        print(f"INICIANDO SCRAPING DE {len(placas)} PLACAS")
        print(f"{'='*60}\n")
        
        for i, placa in enumerate(placas, 1):
            print(f"\n{'─'*60}")
            print(f"VEHÍCULO {i}/{len(placas)}")
            print(f"{'─'*60}")
            
            result = await self.scrape_vehicle(placa)
            if result:
                self.results.append(result)
            
            # Esperar entre búsquedas
            if i < len(placas):
                print("\n⏳ Esperando 3 segundos antes de la siguiente búsqueda...")
                await asyncio.sleep(3)
        
        return self.results
    
    def save_results(self, filename='scraping_results.json'):
        """Guarda los resultados en un archivo JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultados guardados en: {filename}")


# Función principal para ejecutar el scraper
async def main():
    """Función principal."""
    
    # Crear instancia del scraper
    scraper = VehicleScraperANT()
    
    # Placas de ejemplo (reemplazar con placas reales)
    placas_buscar = [
        "PIZ-0001",
        "PIZ-0002",
        "PIZ-0003"
    ]
    
    # Ejecutar scraping
    resultados = await scraper.scrape_multiple(placas_buscar)
    
    # Guardar resultados
    scraper.save_results('vehiculos_scrapidos.json')
    
    # Mostrar resumen
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Total procesado: {len(resultados)}")
    print(f"Con datos encontrados: {sum(1 for r in resultados if r.get('datos_encontrados'))}")
    
    return resultados


if __name__ == "__main__":
    # Ejecutar el scraper
    asyncio.run(main())
