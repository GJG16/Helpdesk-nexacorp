from playwright.sync_api import sync_playwright
import os

CREDS = [
    {"role": "user", "email": "usuario@example.com", "password": "usuario123"},
    {"role": "agent", "email": "agente@example.com", "password": "agente123"},
    {"role": "admin", "email": "admin@example.com", "password": "admin123"},
]
PAGES = ['/tickets', '/tickets/kanban', '/dashboard']
OUT_DIR = os.path.join(os.getcwd(), 'ui_steps', 'screenshots')

os.makedirs(OUT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for cred in CREDS:
        role = cred['role']
        try:
            page.goto('http://localhost:4200/login', wait_until='networkidle')

            # fill inputs with fallbacks
            try:
                page.fill('input[type="email"]', cred['email'])
            except Exception:
                try:
                    page.fill('input[placeholder="nombre@empresa.com"]', cred['email'])
                except Exception:
                    pass
            try:
                page.fill('input[type="password"]', cred['password'])
            except Exception:
                try:
                    page.fill('input[name="password"]', cred['password'])
                except Exception:
                    pass

            # click submit (try multiple selectors, match actual UI text)
            try:
                page.click('button:has-text("Entrar al sistema")')
            except Exception:
                try:
                    page.click('button:has-text("Iniciar sesión")')
                except Exception:
                    try:
                        page.click('button[type="submit"]')
                    except Exception:
                        pass

            # wait for success indicator
            try:
                page.wait_for_selector('button:has-text("Cerrar sesión")', timeout=5000)
                logged = True
            except Exception:
                # try other success marker
                logged = (page.locator('text=Bienvenido').count() > 0)

            if not logged:
                # save diagnostic artifacts
                diag_png = os.path.join(OUT_DIR, f"failed_login_{role}.png")
                diag_html = os.path.join(OUT_DIR, f"failed_login_{role}.html")
                diag_log = os.path.join(OUT_DIR, f"failed_login_{role}.log")
                page.screenshot(path=diag_png, full_page=True)
                with open(diag_html, 'w', encoding='utf-8') as f:
                    f.write(page.content())
                # try to collect console messages (sync API doesn't expose them after the fact), write placeholder
                with open(diag_log, 'w', encoding='utf-8') as f:
                    f.write('Login appears to have failed; see HTML and screenshot for details.')
                print(f"Login failed for {role}; artifacts: {diag_png}, {diag_html}")
            else:
                # capture target pages
                for pth in PAGES:
                    page.goto('http://localhost:4200' + pth, wait_until='networkidle')
                    page.wait_for_timeout(700)
                    safe_name = pth.strip('/').replace('/', '_') or 'root'
                    filename = os.path.join(OUT_DIR, f"{role}_{safe_name}.png")
                    page.screenshot(path=filename, full_page=True)
                    print(f"Saved: {filename}")

                # logout if possible
                try:
                    page.click('button:has-text("Cerrar sesión")')
                    page.wait_for_timeout(300)
                except Exception:
                    pass

        except Exception as e:
            print(f"Error for {role}: {e}")

    browser.close()
