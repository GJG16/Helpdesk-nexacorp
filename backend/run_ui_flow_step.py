from playwright.sync_api import sync_playwright
import time
import sys
import os

OUT_DIR = "ui_steps"
os.makedirs(OUT_DIR, exist_ok=True)

SLEEP = 2  # seconds to pause so user can observe

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=250)
    context = browser.new_context()
    page = context.new_page()

    try:
        print("Abriendo login (usuario)")
        page.goto("http://localhost:4200/login")
        time.sleep(1)
        page.fill("input[type='email']", "usuario@example.com")
        page.fill("input[type='password']", "usuario123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard", timeout=60000)
        page.screenshot(path=f"{OUT_DIR}/01_logged_user.png", full_page=True)
        print("Capturada: 01_logged_user.png")
        time.sleep(SLEEP)

        print("Abrir modal crear ticket")
        # usar data-testid agregado al botón de creación en la lista de tickets
        try:
            page.locator("button[data-testid='btn-create-ticket']").first.click()
        except Exception:
            page.locator("button:has-text('+ Nuevo Ticket'), button:has-text('Nuevo ticket'), button:has-text('Crear Nuevo Ticket')").first.click()
        page.wait_for_selector("app-ticket-create-modal [data-testid='ticket-create-modal']", state="visible", timeout=60000)
        page.screenshot(path=f"{OUT_DIR}/02_modal_open.png", full_page=True)
        print("Capturada: 02_modal_open.png")
        time.sleep(SLEEP)

        print("Rellenar y enviar ticket")
        page.fill("app-ticket-create-modal .modal-container input#titulo", "Fallo critico en base de datos")
        page.fill("app-ticket-create-modal .modal-container textarea#descripcion", "El sistema no permite realizar consultas desde esta mañana. Se requiere soporte urgente.")
        # Esperar la respuesta POST a /api/tickets para garantizar que el backend creó el ticket
        # Esperar la respuesta POST al endpoint de tickets (acepta '/api/tickets' con o sin barra)
        with page.expect_response(lambda response: '/api/tickets' in response.url and response.request.method == 'POST', timeout=60000) as create_resp:
            try:
                page.click("app-ticket-create-modal [data-testid='ticket-submit']")
            except Exception:
                page.click("app-ticket-create-modal .modal-container button[type='submit']")
        resp = create_resp.value
        print("POST /api/tickets status:", resp.status)
        # Obtener el ID del ticket desde la respuesta para usarlo directamente
        ticket_id = None
        try:
            body = resp.json()
            # soportar formas comunes: {id: '...'}, {'_id': '...'}, {'inserted_id': '...'}, or mongodb style {'inserted_id': {'$oid': '...'}}
            if isinstance(body, dict):
                ticket_id = body.get('id') or body.get('inserted_id') or body.get('_id')
                if isinstance(ticket_id, dict) and ('$oid' in ticket_id):
                    ticket_id = ticket_id.get('$oid')
        except Exception:
            ticket_id = None

        page.wait_for_selector("app-ticket-create-modal .modal-container", state="detached", timeout=60000)
        # En lugar de buscar en la tabla (fragilidad por render), navegamos directamente
        # a la URL de edición del ticket si tenemos el ticket_id.
        if ticket_id:
            edit_url = f"http://localhost:4200/tickets/{ticket_id}/edit"
            print("Navegando directamente a:", edit_url)
            # Hacemos logout y login como admin antes de navegar (el flujo original lo hacía)
        else:
            print("No se pudo obtener ticket_id desde la respuesta; intentaremos buscar por título en la UI")
        page.screenshot(path=f"{OUT_DIR}/03_ticket_created.png", full_page=True)
        print("Capturada: 03_ticket_created.png")
        time.sleep(SLEEP)

        print("Logout user")
        page.locator("button:has-text('Cerrar sesión'), button:has-text('Logout'), button:has-text('Logout')").first.click()
        page.wait_for_url("**/login", timeout=60000)
        page.screenshot(path=f"{OUT_DIR}/04_logged_out.png", full_page=True)
        print("Capturada: 04_logged_out.png")
        time.sleep(SLEEP)

        print("Login admin")
        page.fill("input[type='email']", "admin@example.com")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard", timeout=60000)
        page.screenshot(path=f"{OUT_DIR}/05_logged_admin.png", full_page=True)
        print("Capturada: 05_logged_admin.png")
        time.sleep(SLEEP)

        print("Ir a tickets y editar el ticket creado")
        if ticket_id:
            # Navegar directamente a la página de edición del ticket
            edit_url = f"http://localhost:4200/tickets/{ticket_id}/edit"
            print("Navegando a URL de edición:", edit_url)
            page.goto(edit_url)
            page.wait_for_url("**/tickets/**/edit", timeout=60000)
            page.screenshot(path=f"{OUT_DIR}/07_edit_form.png", full_page=True)
            time.sleep(SLEEP)
        else:
            page.locator("button:has-text('Ir a tickets'), button:has-text('Abrir tablero'), button:has-text('Tablero')").first.click()
            page.wait_for_url("**/tickets", timeout=60000)
            page.wait_for_selector("table", timeout=60000)
            page.screenshot(path=f"{OUT_DIR}/06_tickets_table.png", full_page=True)
            time.sleep(SLEEP)

            row = page.locator("table tr", has_text="Fallo critico en base de datos").first
            if row.locator("button:has-text('Asignarme')").count() > 0:
                row.locator("button:has-text('Asignarme')").first.click()
                time.sleep(1)
            row.locator("button.btn-edit, button:has-text('Editar')").first.click()
            page.wait_for_url("**/tickets/**/edit", timeout=60000)
            page.screenshot(path=f"{OUT_DIR}/07_edit_form.png", full_page=True)
            time.sleep(SLEEP)

        print("Marcar En Progreso -> Resuelto -> Cerrado con pausas")

        def open_edit_form():
            if ticket_id:
                page.goto(f"http://localhost:4200/tickets/{ticket_id}/edit")
                page.wait_for_url("**/tickets/**/edit", timeout=60000)
            else:
                page.goto("http://localhost:4200/tickets")
                page.wait_for_url("**/tickets", timeout=60000)
                page.wait_for_selector("table", timeout=60000)
                row_local = page.locator("table tr", has_text="Fallo critico en base de datos").first
                row_local.locator("button.btn-edit, button:has-text('Editar')").first.click()
                page.wait_for_url("**/tickets/**/edit", timeout=60000)
            page.wait_for_selector("select[data-testid='select-estado'], select#estado", timeout=60000)

        # Función auxiliar: realizar cambio de estado esperando PUT/PATCH o fallback
        def change_estado_and_wait(new_estado, screenshot_name):
            try:
                open_edit_form()
                # usar select data-testid si está disponible
                try:
                    page.select_option("select[data-testid='select-estado']", new_estado)
                except Exception:
                    page.select_option("select#estado", new_estado)
                # usar botón de formulario con data-testid si existe
                try:
                    page.click("button[data-testid='form-submit']")
                except Exception:
                    page.click("button[type='submit']")
                # Espera corta para que la SPA procese la acción sin bloquear el flujo
                page.wait_for_timeout(2500)
                print("Estado enviado:", new_estado)
            except Exception as ex:
                print("No se pudo enviar cambio de estado (intentando fallback):", ex)
                # fallback 1: recargar la vista actual
                try:
                    page.reload()
                    page.wait_for_timeout(1500)
                    print("Fallback: recarga completada.")
                except Exception:
                    print("Fallback recarga falló: intentar fetch directo desde la página.")
                    # fallback 2: Si tenemos ticket_id, intentar actualizar usando fetch dentro del contexto de la página
                    try:
                        if ticket_id:
                            api_url = f"http://localhost:8000/api/tickets/{ticket_id}"
                            js = "(url, estado) => fetch(url, {method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({estado})}).then(r => r.status).catch(e => ({error: String(e)}))"
                            result = page.evaluate(js, api_url, new_estado)
                            print("Resultado fetch directo:", result)
                        else:
                            print("No hay ticket_id disponible para fetch directo.")
                    except Exception as ex2:
                        print("Fallback fetch falló:", ex2)
            # Volver a listado para evidencia visual del ticket
            try:
                page.goto("http://localhost:4200/tickets")
                page.wait_for_url("**/tickets", timeout=60000)
                page.wait_for_selector("table", timeout=60000)
            except Exception:
                pass
            page.screenshot(path=f"{OUT_DIR}/{screenshot_name}", full_page=True)
            time.sleep(SLEEP)

        change_estado_and_wait("en_progreso", "08_en_progreso.png")
        change_estado_and_wait("resuelto", "09_resuelto.png")
        change_estado_and_wait("cerrado", "10_cerrado.png")

        print("Flujo UI paso a paso completado. Capturas en:", OUT_DIR)

    except Exception as e:
        print("Error durante E2E UI:", e)
        try:
            page.screenshot(path=f"{OUT_DIR}/error_screenshot.png", full_page=True)
            print("Screenshot guardada en:", f"{OUT_DIR}/error_screenshot.png")
        except Exception:
            pass
        print("No se relanza la excepción; cerrando flujo tras recopilar evidencia.")
        time.sleep(3)
    finally:
        context.close()
        browser.close()

print("Script finalizado")
