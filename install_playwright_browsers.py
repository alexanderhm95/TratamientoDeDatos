"""
Script para descargar los navegadores necesarios de Playwright.
Ejecutar este script una sola vez antes de usar el scraper.
"""

import asyncio
from playwright.async_api import async_playwright


async def install_browsers():
    """Descarga e instala los navegadores de Playwright."""
    print("📥 Descargando navegadores de Playwright...")
    print("   - Chromium")
    print("   - Firefox")
    print("   - WebKit")
    print("\nEsto puede tomar algunos minutos...\n")
    
    try:
        async with async_playwright() as p:
            # Los navegadores se descargarán automáticamente
            await p.chromium.launch()
            await p.firefox.launch()
            await p.webkit.launch()
        
        print("\n✅ ¡Navegadores instalados exitosamente!")
        print("\nAhora puedes ejecutar el scraper:")
        print("  python scraper_placar.py")
        
    except Exception as e:
        print(f"\n❌ Error al instalar navegadores: {e}")
        print("\nIntenta ejecutar manualmente:")
        print("  playwright install")


if __name__ == "__main__":
    asyncio.run(install_browsers())
