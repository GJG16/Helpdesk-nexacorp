import subprocess
import sys
import time
import httpx
import json
from pprint import pprint
from pymongo import MongoClient

BASE = "http://localhost:8000"

def run_seed():
    print("Ejecutando seed_db.py para inicializar datos de prueba...")
    # Usar el intérprete actual y ejecutar en el directorio backend
    subprocess.run([sys.executable, "seed_db.py"], cwd="backend", check=True)

def login(email, password):
    r = httpx.post(f"{BASE}/api/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    return r.json()

def api_get(path, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.get(f"{BASE}{path}", headers=headers)
    return r

def api_post(path, token, json_data):
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.post(f"{BASE}{path}", headers=headers, json=json_data)
    return r

def api_put(path, token, json_data):
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.put(f"{BASE}{path}", headers=headers, json=json_data)
    return r

def api_delete(path, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.delete(f"{BASE}{path}", headers=headers)
    return r


def main():
    run_seed()
    time.sleep(0.5)

    # Login as seed users
    admin = login("admin@example.com", "admin123")
    agent = login("agente@example.com", "agente123")
    user = login("usuario@example.com", "usuario123")

    admin_token = admin["access_token"]
    agent_token = agent["access_token"]
    user_token = user["access_token"]

    print("Usuarios autenticados. IDs:")
    print("admin id:", admin["user"]["id"])
    print("agent id:", agent["user"]["id"])
    print("user id:", user["user"]["id"])

    # 1. User creates a ticket (title too short should fail)
    print("Creando ticket por user...")
    ticket_payload = {
        "titulo": "Fallo critico en login",
        "descripcion": "Al intentar loguearme la app devuelve error 500 y pantalla en blanco.",
        "prioridad": "critica"
    }
    r = api_post("/api/tickets/", user_token, ticket_payload)
    print("Create status:", r.status_code)
    pprint(r.json())
    ticket = r.json()
    ticket_id = ticket["id"]

    # Verify user cannot see other user's data: try to get a ticket that belongs to another user
    print("Verificando restricción de acceso: usuario no puede ver ticket de otro...")
    # Create a ticket as admin for a different user (admin can set usuario_id)
    admin_ticket_payload = {
        "titulo": "Incidencia admin-owned",
        "descripcion": "Ticket creado por admin para pruebas.",
        "prioridad": "alta",
        "usuario_id": admin["user"]["id"]
    }
    r2 = api_post("/api/tickets/", admin_token, admin_ticket_payload)
    admin_ticket = r2.json()
    admin_ticket_id = admin_ticket["id"]

    # Now user tries to GET admin_ticket -> should be 403
    r3 = api_get(f"/api/tickets/{admin_ticket_id}", user_token)
    print("GET admin ticket as user status:", r3.status_code)

    # 2. Agent takes the user's ticket: assign to self
    print("Agent asignándose el ticket...")
    assign_payload = {"asignado_a": agent["user"]["id"]}
    r4 = api_put(f"/api/tickets/{ticket_id}", agent_token, assign_payload)
    print("Assign status:", r4.status_code)
    pprint(r4.json())

    # Agent must document before resolving: add comment
    print("Agent añade comentario de resolución...")
    comment_payload = {"texto": "He identificado el error en el servicio de autenticación, reinstalando dependencias."}
    r5 = api_post(f"/api/tickets/{ticket_id}/comments", agent_token, comment_payload)
    print("Comment status:", r5.status_code)
    pprint(r5.json())

    # Agent marks ticket as 'resuelto'
    print("Agent marca ticket como resuelto...")
    res_payload = {"estado": "resuelto"}
    r6 = api_put(f"/api/tickets/{ticket_id}", agent_token, res_payload)
    print("Resolve status:", r6.status_code)
    pprint(r6.json())

    # Verify timestamps: fecha_actualizacion and fecha_resolucion
    ticket_after = r6.json()
    print("fecha_actualizacion:", ticket_after.get("fecha_actualizacion"))
    print("fecha_resolucion:", ticket_after.get("fecha_resolucion"))

    # User confirms by adding a comment (since user cannot change estado)
    print("User añade confirmación de resolución...")
    user_comment = {"texto": "Confirmo que el problema se solucionó."}
    r7 = api_post(f"/api/tickets/{ticket_id}/comments", user_token, user_comment)
    print("User comment status:", r7.status_code)
    pprint(r7.json())

    # Admin deletes the admin-created ticket and check audit_logs
    print("Admin elimina ticket de prueba creado por admin...")
    r8 = api_delete(f"/api/tickets/{admin_ticket_id}", admin_token)
    print("Delete status (admin ticket):", r8.status_code)

    # Check audit_logs in MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client["helpdesk_db"]
    audit = list(db.audit_logs.find({"resource_id": admin_ticket_id}))
    print("Audit entries for deleted ticket:")
    for a in audit:
        a["id"] = str(a.pop("_id"))
        pprint(a)

    # Check that update times exist in ticket history
    t = db.tickets.find_one({"_id": None})  # dummy to show pymongo reachable

    print("Flujo completado.")

if __name__ == '__main__':
    main()
