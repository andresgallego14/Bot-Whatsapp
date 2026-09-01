from playwright.sync_api import sync_playwright
import os

def obtener_ubicacion_satrack(placa, usuario=None, contrasena=None):
    # Si no se envían credenciales, busca en variables de entorno
    usuario = usuario or os.getenv("SATRACK_USER")
    contrasena = contrasena or os.getenv("SATRACK_PASS")

    if not usuario or not contrasena:
        raise ValueError("Error: No se proporcionaron credenciales válidas para Satrack.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        # 1. Login dinámico
        print(f"Iniciando sesión en Satrack con el usuario: {usuario}...")
        page.goto("https://login.satrack.com/login")
        
        page.get_by_role("textbox", name="Usuario").fill(usuario)
        page.get_by_role("textbox", name="Contraseña").fill(contrasena)
        page.get_by_role("button", name="Ingresar").click()
        
        # 2. Esperar carga del dashboard
        print("Esperando que cargue el dashboard...")
        page.wait_for_url("**/portal.satrack.com/**", timeout=30000)
        page.wait_for_timeout(4000)
        
        # 3. Escribir la placa en el buscador
        print(f"Buscando la placa: {placa}...")
        script_buscar = f"""
            const input = document.querySelector('input.filterVehicles') || document.querySelector('input[placeholder*="Buscar"]');
            if (input) {{
                input.focus();
                input.value = '{placa}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        """
        page.evaluate(script_buscar)
        page.wait_for_timeout(1000)
        page.keyboard.press("Enter")
        
        # 4. Seleccionar vehículo en la lista
        print("Seleccionando el vehículo en la lista...")
        page.wait_for_timeout(2000)
        page.get_by_text(placa).first.click()
        page.wait_for_timeout(4000)
        
        # 5. Extraer información
        print("Leyendo información de la ubicación...")
        info_texto = ""
        
        try:
            info_texto = page.locator(".gm-style-iw-d, div[class*='info-window'], div[class*='popup']").first.inner_text(timeout=5000)
        except Exception:
            try:
                info_texto = page.locator(".vehicle-item, mat-list-option, .cdk-drag").first.inner_text(timeout=5000)
            except Exception as e:
                print("No se pudo extraer texto de ninguna fuente:", e)
                return None
        
        return info_texto