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

### Status Endpoints

#### GET `/api/status`
Verificar que el servidor está operativo.

**Response:**
```json
{
  "status": "online",
  "service": "Helpdesk API",
  "version": "1.0.0",
  "timestamp": "2024-05-11T10:30:00",
  "message": "Sistema de Gestión de Tickets operativo"
}
```

#### GET `/api/health`
Health check del servidor.

**Response:**
```json
{
  "status": "healthy",
  "service": "Helpdesk API"
}
```

### Tickets Endpoints (Próximos)
- `GET /api/tickets` - Obtener todos los tickets
- `GET /api/tickets/{id}` - Obtener ticket por ID
- `POST /api/tickets` - Crear nuevo ticket
- `PUT /api/tickets/{id}` - Actualizar ticket
- `DELETE /api/tickets/{id}` - Eliminar ticket
- `POST /api/tickets/filter` - Filtrar tickets

---

## 🌿 Gitflow

Este proyecto sigue el flujo **Gitflow**:

```
main (producción)
├── develop (integración)
│   ├── feature/sprint1-setup (desarrollo)
│   ├── feature/user-crud
│   ├── feature/ticket-crud
│   └── [otras features]
└── hotfix/* (parches de emergencia)
```

### Ramas Principales

- **main**: Código en producción, siempre estable
- **develop**: Integración de features, rama de pre-producción
- **feature/***: Ramas temporales para desarrollar nuevas funcionalidades

### Flujo de Trabajo

1. Crear rama de feature desde `develop`:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. Realizar cambios y commits:
   ```bash
   git add .
   git commit -m "feat: descripción de cambios"
   ```

3. Mergear a `develop`:
   ```bash
   git checkout develop
   git merge feature/nueva-funcionalidad
   git push origin develop
   ```

4. Para release a producción:
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

---

## 📝 Esquemas de Datos

### User
```typescript
{
  id?: string;
  nombre: string;
  email: string;
  rol: 'admin' | 'agent' | 'user';
  fecha_creacion?: Date;
}
```

### Ticket
```typescript
{
  id?: string;
  titulo: string;
  descripcion: string;
  estado: 'abierto' | 'en_progreso' | 'resuelto' | 'cerrado';
  usuario_id: string;
  fecha_creacion?: Date;
  fecha_actualizacion?: Date;
}
```

---

## 🔐 Variables de Entorno

Backend (`.env`):
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=helpdesk_db

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False

# CORS Origins
CORS_ORIGINS=["http://localhost:4200", "http://localhost:3000"]
```

---

## 🧪 Pruebas

### Backend - Probar API con cURL
```bash
# Verificar status
curl http://localhost:8000/api/status

# Acceder a documentación interactiva
# Abre en navegador: http://localhost:8000/docs
```

### Frontend - Pruebas Unitarias
```bash
cd frontend
ng test
```

---

## 🐛 Troubleshooting

### MongoDB no se conecta
- Verificar que MongoDB está corriendo: `mongosh mongodb://localhost:27017`
- Confirmar la URL en `.env`: `mongodb://localhost:27017`

### CORS Error en Frontend
- Verificar que CORS está configurado correctamente en `backend/config/settings.py`
- Asegurar que la URL del frontend esté en `CORS_ORIGINS`

### Angular no se compila
```bash
cd frontend
npm install
ng build
```

### Puerto 8000 o 4200 en uso
```bash
# Cambiar puerto en backend (main.py):
uvicorn.run("main:app", host="0.0.0.0", port=8001)

# Cambiar puerto en frontend (angular.json):
"serve": {
  "options": {
    "port": 4201
  }
}
```

---

## 📊 Matriz de Propiedades de Issues

| # | Título del Issue | Tipo | Prioridad | Estado | Sprint | Responsable | Milestone |
|---|---|---|---|---|---|---|---|
| #1 | Configuración de Repositorios y Flujo Gitflow | Tarea | Alta | Done | 1 | @GJG16 | Sprint 1 |
| #2 | Inicializar Backend con FastAPI y Conexión a MongoDB | Historia de usuario | Alta | Done | 1 | @franco27-dev | Sprint 1 |
| #3 | Módulo de Autenticación y Gestión de Roles | Historia de usuario | Alta | Code Review | 2 | @franco27-dev | Sprint 2 |
| #4 | Implementar vista de Creación y Listado de Tickets | Historia de usuario | Alta | Code Review | 3 | @adriano08-xc | Sprint 3 |
| #6 | Configuración de Pipeline CI/CD para Pruebas Automáticas | Tarea | Media | Code Review | 4 | @GJG16 | Sprint 4 |
| #7 | Panel de Control (Dashboard) para Administradores | Historia de usuario | Media | In Progress | 5 | @adriano08-xc | Sprint 5 |
| #8 | Dockerización del Sistema y Despliegue en la Nube | Tarea | Alta | Backlog | 8 | @GJG16 | Sprint 8 |
| #19 | Notificaciones en Tiempo Real (WebSocket) | Historia de usuario | Alta | To Do | 6 | @GJG16 | Sprint 6 |
| #20 | Sistema de Categorías y SLA para Tickets | Historia de usuario | Alta | To Do | 6 | @adriano08-xc | Sprint 6 |
| #21 | Panel de Administración de Usuarios | Historia de usuario | Media | Backlog | 7 | @adriano08-xc | Sprint 7 |
| #22 | Pruebas E2E y Limpieza de Codigo de Debug | Tarea | Media | Backlog | 7 | @franco27-dev | Sprint 7 |
| #23 | Documentación Técnica y Entrega Final | Tarea | Alta | In Progress | 8 | @GJG16 | Sprint 8 |
## 📞 Contacto y Contribución

- **Repositorio**: https://github.com/GJG16/Helpdesk-nexacorp
- **Issues**: Reportar problemas en la sección de Issues de GitHub

---

## 📄 Licencia

Desarrollado para uso corporativo interno / Proyecto de Portfolio.

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

**Última actualización**: 01 de Junio de 2026
**Versión**: 1.0.0-alpha
