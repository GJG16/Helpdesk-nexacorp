from playwright.sync_api import sync_playwright
import time
import sys

def run():
    print("Iniciando automatizacion visual del flujo de UI...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Paso 1: Login como usuario (usuario@example.com)")
            page.goto("http://localhost:4200/login")
            page.fill("input[type='email']", "usuario@example.com")
            page.fill("input[type='password']", "usuario123")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard", timeout=60000)

            print("Paso 2: Crear ticket")
            # Abrir modal de creación de ticket
            page.locator("button:has-text('+ Nuevo Ticket'), button:has-text('Nuevo ticket'), button:has-text('Crear Nuevo Ticket')").first.click()
            # Esperar el modal y completar formulario (esperar el contenedor visible para evitar animaciones ocultas)
            page.wait_for_selector("app-ticket-create-modal .modal-container", state="visible", timeout=60000)
            page.fill("app-ticket-create-modal .modal-container input#titulo", "Fallo critico en base de datos")
            page.fill("app-ticket-create-modal .modal-container textarea#descripcion", "El sistema no permite realizar consultas desde esta mañana. Se requiere soporte urgente.")
            # En el modal el submit muestra una pantalla de éxito en lugar de navegación inmediata
            page.click("app-ticket-create-modal button[type='submit']")
            # Esperar la vista de éxito y que el modal se cierre
            page.wait_for_selector("app-ticket-create-modal .success-view", timeout=60000)
            page.wait_for_selector("app-ticket-create-modal .modal-container", state="detached", timeout=60000)
            # Esperar que la lista de tickets se actualice y muestre el nuevo ticket
            page.wait_for_selector(f"text=Fallo critico en base de datos", timeout=60000)
            print("Ticket creado y visible en la lista.")

            print("Paso 3: Cerrar sesion de usuario")
            page.locator("button:has-text('Cerrar sesión'), button:has-text('Logout')").first.click()
            page.wait_for_url("**/login", timeout=60000)

            print("Paso 4: Login como administrador (admin@example.com)")
            page.fill("input[type='email']", "admin@example.com")
            page.fill("input[type='password']", "admin123")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard", timeout=60000)

            print("Paso 5: Administrador gestiona el ticket")
            page.locator("button:has-text('Ir a tickets'), button:has-text('Abrir tablero'), button:has-text('Tablero')").first.click()
            page.wait_for_url("**/tickets", timeout=60000)

            # Buscar la fila del ticket creado y abrir el editor
            row = page.locator("table tr", has_text="Fallo critico en base de datos").first
            # Si el agente puede asignarse con botón "Asignarme", usarlo (ya fue asignado por API flow)
            if row.locator("button:has-text('Asignarme')").count() > 0:
                row.locator("button:has-text('Asignarme')").first.click()
            # Abrir editor (Editar)
            row.locator("button.btn-edit, button:has-text('Editar')").first.click()
            # Esperar a la página de edición
            page.wait_for_url("**/tickets/**/edit", timeout=60000)

            # Wait for estado selector en el formulario de edición
            page.wait_for_selector("select#estado", timeout=60000)

            print("Cambiando estado a 'En progreso'...")
            page.select_option("select#estado", "en_progreso")
            page.click("button[type='submit']")
            page.wait_for_url("**/tickets", timeout=60000)

            print("Cambiando estado a 'Resuelto'...")
            # Abrir nuevamente el editor para marcar resuelto
            row = page.locator("table tr", has_text="Fallo critico en base de datos").first
            row.locator("button.btn-edit, button:has-text('Editar')").first.click()
            page.wait_for_selector("select#estado", timeout=60000)
            page.select_option("select#estado", "resuelto")
            page.click("button[type='submit']")
            page.wait_for_url("**/tickets", timeout=60000)

            print("Cambiando estado a 'Cerrado'...")
            row = page.locator("table tr", has_text="Fallo critico en base de datos").first
            row.locator("button.btn-edit, button:has-text('Editar')").first.click()
            page.wait_for_selector("select#estado", timeout=60000)
            page.select_option("select#estado", "cerrado")
            page.click("button[type='submit']")
            page.wait_for_url("**/tickets", timeout=60000)
            
            print("Flujo de UI completado exitosamente.")
            time.sleep(3)
        except Exception as e:
            print("Ocurrio un error visualizando el flujo:", e)
            page.screenshot(path="error_screenshot.png")
            print("Screenshot saved to error_screenshot.png")
            sys.exit(1)
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()
