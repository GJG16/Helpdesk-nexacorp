# 🚀 HDESK - Enterprise Service Management

HDESK es un Sistema de Gestión de Tickets (Helpdesk) de grado empresarial diseñado para ofrecer flujos de trabajo eficientes, gestión de SLAs y una experiencia ágil mediante un Tablero Kanban integrado. 

Construido con una arquitectura moderna que separa el frontend (Angular) del backend (FastAPI + MongoDB), HDESK está optimizado para brindar tiempos de respuesta instantáneos, interfaces colaborativas y escalabilidad corporativa.

---

## ✨ Características Principales (Nivel Enterprise)

1. **Gestión de Identidad y Roles ITIL**: Soporta múltiples roles (Usuarios, Agentes, Administradores) garantizando que cada participante solo interactúe con las vistas, permisos y acciones que le corresponden.
2. **Tablero Kanban Dinámico**: Un *board* visual y reactivo con funcionalidad *drag-and-drop*. Incluye UI optimista (actualización instantánea antes de la confirmación del servidor) para una experiencia de usuario fluida sin bloqueos.
3. **Motor de SLAs (Service Level Agreements)**: HDESK calcula, monitorea y visibiliza de forma proactiva el tiempo de vida de los tickets basado en su prioridad (Crítica, Alta, Media, Baja), mostrando indicadores de vencimiento en tiempo real.
4. **Línea de Tiempo Integral (Audit Trail)**: Cada ticket posee un historial inmutable que registra de manera unificada tanto el cambio de estados, asignaciones, prioridades, como los comentarios y anotaciones de los participantes.
5. **Comentarios Enriquecidos (Rich Text)**: Soporte completo para formato de texto enriquecido (negritas, listas, cursivas) y manejo de múltiples archivos adjuntos por ticket.
6. **Manejo Eficiente de Recursos**: Arquitectura *Lazy Loading* en Angular que reduce el peso inicial de la aplicación, reciclando nodos HTML y previniendo fugas de memoria con suscripciones dinámicas a observables.

---

## 🛠️ Stack Tecnológico

### Frontend
- **Framework**: Angular 18 (Standalone Components)
- **Estilos**: Vanilla CSS con variables de diseño (Glassmorphism & Dark Mode UI)
- **Editor**: Quill.js / ngx-quill
- **Routing**: Angular Router con Guards y optimización Lazy Loading

### Backend
- **Framework**: FastAPI (Python)
- **Base de Datos**: MongoDB (Motor NoSQL)
- **Seguridad**: Autenticación JWT (JSON Web Tokens), Hashing con Passlib y bcrypt. CORS configurado.
- **Validación**: Pydantic v2
- **Logging**: Loguru para auditoría interna a nivel sistema.

---

## 💻 Instalación y Configuración Local

### Prerrequisitos
- [Node.js](https://nodejs.org/es/) (v18 o superior)
- [Python](https://www.python.org/) (v3.10 o superior)
- [MongoDB](https://www.mongodb.com/try/download/community) ejecutándose localmente en el puerto `27017`

### 1. Configuración del Backend

```bash
cd backend
python -m venv .venv

# En Windows
.venv\Scripts\activate
# En Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
*El backend estará disponible en `http://localhost:8000`*

### 2. Configuración del Frontend

```bash
cd frontend
npm install
npm start
```
*El frontend estará disponible en `http://localhost:4200`*

---

## 🔒 Estructura de Roles
- **user**: Puede crear tickets y ver el estado de sus solicitudes.
- **agent**: Tiene acceso al Tablero Kanban, puede asignarse tickets y modificar su estado.
- **admin**: Posee acceso total al sistema, estadísticas (Dashboard), gestión de otros usuarios, y edición maestra de cualquier solicitud.

---

## 🤝 Contribuciones
Este proyecto fue desarrollado bajo estrictas revisiones de auditoría enfocadas en la prevención de fugas de memoria, optimización del DOM y arquitectura orientada a servicios. Se invita a crear *issues* o *pull requests* bajo el mismo estándar de calidad.

## 📝 Licencia
Desarrollado para uso corporativo interno / Proyecto de Portfolio.
