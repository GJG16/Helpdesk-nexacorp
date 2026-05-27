Generar capturas UI (Playwright)

Este script inicia sesión en la UI por formulario para los tres roles de prueba y guarda capturas en `ui_steps/screenshots/`.

Requisitos:
- Python con Playwright instalado. Si no tienes Playwright instalado, ejecuta:

```bash
python -m pip install playwright
python -m playwright install
```

Ejecutar:

```bash
python ui_steps/capture_ui_screenshots.py
```

Salida:
- `ui_steps/screenshots/` contendrá archivos PNG nombrados `user_tickets.png`, `agent_tickets_kanban.png`, `admin_dashboard.png`, etc.

Notas:
- Asegúrate de que el backend (`http://localhost:8000`) y el frontend (`http://localhost:4200`) estén corriendo antes de ejecutar el script.
- Si el selector del formulario difiere, edita `capture_ui_screenshots.py` para ajustar los selectores de `input` y `button`.
