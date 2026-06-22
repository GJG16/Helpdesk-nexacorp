# 📋 Issues del Proyecto - Helpdesk NexaCorp

### Issue #1 — Configuración de Repositorios y Flujo Gitflow

| Campo | Valor |
|---|---|
| Título | Configuración de Repositorios y Flujo Gitflow |
| Tipo | Tarea tecnica |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 1 |
| Responsable | @franco27-dev |
| Inicio | 2026-03-30 |
| Duración | 5 dias |

**Descripción:**
Inicializar el repositorio principal del Sistema de Gestion de Tickets en GitHub, configurando las ramas base y los permisos segun el modelo Gitflow para asegurar el trabajo colaborativo sin conflictos.

**Checklist:**
- [x] Crear repositorio helpdesk-nexacorp en GitHub
- [x] Crear rama principal main como rama de produccion
- [x] Crear rama de integracion develop a partir de main
- [x] Configurar proteccion de rama para main (requerir Pull Requests)
- [x] Crear archivo .gitignore para entornos Node.js y Python
- [x] Subir README.md inicial con descripcion del proyecto
- [x] Crear archivo CONTRIBUTING.md con guia de contribucion
- [x] Crear archivo CODEOWNERS para asignar revisores automaticos
- [x] Crear plantilla de Pull Request en .github/pull_request_template.md
- [x] Verificar que ningun desarrollador puede hacer push directo a main
- [x] Crear primera rama feature/ de ejemplo para validar el flujo

**Criterios de aceptación:**
- [x] El repositorio cuenta con la estructura base de ramas (main, develop, feature/*)
- [x] Ningun desarrollador puede hacer push directo a la rama main
- [x] Las plantillas de PR y CODEOWNERS estan configuradas

---

### Issue #2 — Inicializar Backend con FastAPI y Conexión a MongoDB

| Campo | Valor |
|---|---|
| Título | Inicializar Backend con FastAPI y Conexión a MongoDB |
| Tipo | Historia de usuario |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 1 |
| Responsable | @GJG16 |
| Inicio | 2026-04-03 |
| Duración | 8 dias |

**Descripción:**
Crear la estructura del servidor backend en Python utilizando FastAPI y establecer la conexion exitosa hacia la base de datos documental MongoDB, incluyendo endpoints de prueba y configuracion de middlewares.

**Checklist:**
- [x] Crear entorno virtual (venv) e instalar dependencias (FastAPI, Uvicorn, Motor)
- [x] Crear archivo requirements.txt con todas las dependencias
- [x] Crear archivo de configuracion config/settings.py con variables del entorno
- [x] Crear archivo .env con credenciales de MongoDB y configuracion del servidor
- [x] Implementar clase Database en database.py con Motor (async MongoDB)
- [x] Configurar indices de MongoDB para email, estado, tickets y audit_logs
- [x] Crear funciones connect_db() y close_db() con lifecycle events
- [x] Crear endpoint GET /api/status que retorne estado del servidor
- [x] Crear endpoint GET /api/health para health check
- [x] Configurar middleware CORS con origenes permitidos desde settings
- [x] Crear ruta raiz GET / con mensaje de bienvenida y link a /docs
- [x] Verificar que el servidor ejecuta en localhost:8000 sin errores
- [x] Verificar que Swagger UI (/docs) muestra los endpoints correctamente

**Criterios de aceptación:**
- [x] El servidor ejecuta en localhost:8000 sin errores
- [x] El endpoint /api/status devuelve JSON con estado 200 OK
- [x] La conexion a MongoDB se establece al iniciar la aplicacion
- [x] CORS esta configurado para permitir peticiones del frontend

---

### Issue #3 — Módulo de Autenticación y Gestión de Roles

| Campo | Valor |
|---|---|
| Título | Módulo de Autenticación y Gestión de Roles |
| Tipo | Historia de usuario |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 2 |
| Responsable | @GJG16 |
| Inicio | 2026-04-13 |
| Duración | 14 dias |

**Descripción:**
Implementar el sistema completo de autenticacion con JWT (access + refresh tokens), registro de usuarios con hash bcrypt, y control de acceso basado en tres roles: admin, agent y user.

**Checklist:**
- [x] Crear modelos Pydantic para UserBase, UserCreate, UserUpdate y User en schemas.py
- [x] Crear enum UserRole con valores admin, agent, user
- [x] Implementar hash_password() con bcrypt via passlib en security.py
- [x] Implementar create_access_token() con JWT (python-jose) y expiracion configurable
- [x] Implementar create_refresh_token() con tipo "refresh" en el payload
- [x] Implementar decode_token() con validacion de tipo (access/refresh)
- [x] Crear endpoint POST /api/auth/register para registro de nuevos usuarios
- [x] Validar email unico en registro (indice unique en MongoDB)
- [x] Crear endpoint POST /api/auth/login con verificacion de credenciales
- [x] Retornar access_token, refresh_token y datos del usuario en login exitoso
- [x] Crear endpoint POST /api/auth/refresh para renovar tokens expirados
- [x] Crear dependencia get_current_user() que extrae y valida el token del header
- [x] Crear AuthGuard en Angular para proteger rutas autenticadas
- [x] Implementar AuthInterceptor en Angular para adjuntar Bearer token automaticamente
- [x] Implementar auto-refresh de token en interceptor cuando recibe 401
- [x] Crear AuthService en Angular con login(), register(), logout(), refreshToken()
- [x] Almacenar tokens y usuario en localStorage
- [x] Crear seed_db.py con 3 usuarios de prueba (admin, agent, user)

**Criterios de aceptación:**
- [x] Un usuario puede registrarse y hacer login recibiendo tokens JWT
- [x] Las rutas protegidas rechazan peticiones sin token valido (401)
- [x] El sistema distingue entre los 3 roles para control de acceso
- [x] El refresh token permite renovar sesiones sin re-login

---

### Issue #4 — Implementar vista de Creación y Listado de Tickets (Frontend)

| Campo | Valor |
|---|---|
| Título | Implementar vista de Creación y Listado de Tickets (Frontend) |
| Tipo | Historia de usuario |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 3 |
| Responsable | @GJG16 |
| Inicio | 2026-04-27 |
| Duración | 14 dias |

**Descripción:**
Disenar y programar los componentes en Angular para que el usuario final pueda crear tickets, ver el listado con filtros, editar tickets existentes, agregar comentarios, y gestionar el flujo desde un tablero Kanban con drag and drop.

**Checklist:**
- [x] Crear modelo Ticket en frontend con interfaces TypeScript (Ticket, TicketFilter, TicketComment)
- [x] Crear TicketService con metodos getTickets(), createTicket(), updateTicket(), deleteTicket()
- [x] Implementar metodo filterTickets() con filtros por estado, prioridad, fecha
- [x] Implementar metodos getComments() y addComment() en TicketService
- [x] Crear componente TicketCreateModal con formulario rapido (titulo, descripcion)
- [x] Forzar prioridad "media" por defecto para usuarios finales
- [x] Crear componente TicketForm para edicion con campos titulo, descripcion, estado, prioridad
- [x] Agregar selector de solicitante visible solo para admin en TicketForm
- [x] Agregar seccion de comentarios/historial de conversacion en TicketForm
- [x] Crear componente TicketsList con tabla dinamica y filtros por estado
- [x] Agregar boton "Eliminar" visible solo para admin con confirmacion
- [x] Agregar data-testid en todos los elementos interactivos para pruebas E2E
- [x] Crear componente KanbanBoard con 4 columnas (Pendiente, En Proceso, Resuelto, Cerrado)
- [x] Implementar drag and drop para mover tickets entre columnas
- [x] Implementar boton "Tomar ticket" para auto-asignacion de agentes
- [x] Validar que agente debe asignarse antes de mover un ticket
- [x] Aplicar estilos responsive para movil, tablet y escritorio
- [x] Validar que campos obligatorios no se envien vacios (min 5 chars titulo, 10 chars descripcion)

**Criterios de aceptación:**
- [x] Al crear un ticket, la tabla de listado se actualiza automaticamente
- [x] El Kanban permite mover tickets con drag and drop respetando permisos RBAC
- [x] Los comentarios se muestran en orden cronologico con autor y rol
- [x] El diseno es responsivo y se visualiza correctamente en pantallas de laptop

---

### Issue #6 — Configuración de Pipeline CI/CD para Pruebas Automáticas

| Campo | Valor |
|---|---|
| Título | Configuración de Pipeline CI/CD para Pruebas Automáticas |
| Tipo | Tarea tecnica |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 4 |
| Responsable | @franco27-dev |
| Inicio | 2026-05-11 |
| Duración | 14 dias |

**Descripción:**
Configurar un pipeline de integracion continua en GitHub Actions que ejecute automaticamente pruebas del backend (pytest) y validacion del frontend (npm build) en cada Pull Request hacia la rama develop.

**Checklist:**
- [x] Crear archivo .github/workflows/ci.yml con trigger en PR a develop
- [x] Configurar job de backend con Python 3.11 en ubuntu-latest
- [x] Instalar dependencias del backend desde requirements.txt
- [x] Ejecutar suite de pytest con 7 tests (5 auth + 2 status)
- [x] Configurar job de frontend con Node.js
- [x] Instalar dependencias del frontend con npm ci
- [x] Ejecutar npm run build para validar compilacion de Angular
- [x] Configurar variables de entorno necesarias para los tests
- [x] Verificar que el pipeline falla correctamente si un test no pasa
- [x] Verificar que el badge de CI aparece en el repositorio
- [x] Documentar en CONTRIBUTING.md como ejecutar tests localmente

**Criterios de aceptación:**
- [x] El pipeline se ejecuta automaticamente en cada PR a develop
- [x] Si un test falla, el PR se marca como fallido y bloquea el merge
- [x] Los tests de backend (pytest) y frontend (npm build) corren en paralelo

---

### Issue #7 — Panel de Control (Dashboard) para Administradores

| Campo | Valor |
|---|---|
| Título | Panel de Control (Dashboard) para Administradores |
| Tipo | Historia de usuario |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 5 |
| Responsable | @GJG16 |
| Inicio | 2026-05-25 |
| Duración | 14 dias |

**Descripción:**
Crear el panel de control para administradores que muestre estadisticas globales de tickets, reportes por estado y por agente, feed de auditoria de acciones sensibles, y acciones rapidas diferenciadas por rol.

**Checklist:**
- [x] Crear DashboardComponent con layout de sidebar + workspace principal
- [x] Mostrar tarjeta de usuario con nombre, email y pill de rol (admin/agent/user)
- [x] Implementar seccion de estadisticas con 5 tarjetas: Total, Abiertos, En Progreso, Resueltos, Cerrados
- [x] Calcular estadisticas dinamicamente desde la API con calculateStats()
- [x] Mostrar tabla de "Tickets recientes" con los ultimos 5 tickets
- [x] Crear seccion "Acciones rapidas" con botones diferenciados por rol
- [x] Mostrar info-block "Modo administrador" solo para admin
- [x] Mostrar info-block "Modo agente" solo para agent
- [x] Agregar boton "Nuevo ticket" visible para agent y user
- [x] Agregar boton "Reportes y auditoria" visible solo para admin
- [x] Crear ReportsComponent con endpoint GET /api/reports/tickets
- [x] Mostrar reporte de tickets agrupados por estado (grafico/tabla)
- [x] Mostrar reporte de tickets agrupados por agente asignado
- [x] Crear endpoint GET /api/reports/audit para feed de auditoria
- [x] Mostrar eventos recientes de auditoria (eliminaciones de tickets y usuarios)
- [x] Implementar boton "Descargar JSON" para exportar reporte completo
- [x] Implementar log_deletion() en audit.py para registrar acciones sensibles
- [x] Verificar que solo admin puede acceder a /reports (RBAC)

**Criterios de aceptación:**
- [x] El admin ve estadisticas globales de todos los tickets del sistema
- [x] Los reportes muestran datos agrupados por estado y por agente
- [x] El feed de auditoria registra eliminaciones de tickets y usuarios
- [x] Usuarios no-admin son redirigidos al dashboard si intentan acceder a /reports

---

### Issue #8 — Dockerización del Sistema y Despliegue en la Nube

| Campo | Valor |
|---|---|
| Título | Dockerización del Sistema y Despliegue en la Nube |
| Tipo | Tarea tecnica |
| Prioridad | Alta |
| Estado | Backlog |
| Sprint | Sprint 8 |
| Responsable | @franco27-dev |
| Inicio | 2026-07-06 |
| Duración | 14 dias |

**Descripción:**
Empaquetar el frontend y backend en contenedores Docker independientes y crear un docker-compose para levantar todo el sistema (backend + frontend + MongoDB) con un solo comando para entornos de desarrollo y produccion.

**Checklist:**
- [ ] Crear backend/Dockerfile con imagen base Python 3.11-slim
- [ ] Configurar WORKDIR, COPY requirements.txt e instalar dependencias
- [ ] Configurar CMD para ejecutar uvicorn con host 0.0.0.0
- [ ] Crear frontend/Dockerfile multistage: Node para build + Nginx para servir
- [ ] Configurar nginx.conf para servir Angular con SPA fallback
- [ ] Crear docker-compose.yml con 3 servicios: backend, frontend, mongodb
- [ ] Configurar red interna entre contenedores
- [ ] Mapear volumenes persistentes para datos de MongoDB
- [ ] Crear archivo .env.docker con variables de entorno para contenedores
- [ ] Reemplazar http://localhost:8000 en servicios Angular por variable de entorno
- [ ] Crear script seed en docker-compose para inicializar datos de prueba
- [ ] Probar levantamiento completo con docker-compose up --build
- [ ] Verificar que la aplicacion responde en localhost:4200 y localhost:8000
- [ ] Documentar instrucciones de uso en README.md

**Criterios de aceptación:**
- [ ] docker-compose up levanta los 3 servicios sin errores
- [ ] La aplicacion es accesible en localhost:4200 (frontend) y localhost:8000 (backend)
- [ ] El sistema corre integramente sobre contenedores sin dependencias locales
- [ ] La base de datos persiste datos entre reinicios de contenedores

---

### Issue #19 — Notificaciones en Tiempo Real (WebSocket)

| Campo | Valor |
|---|---|
| Título | Notificaciones en Tiempo Real (WebSocket) |
| Tipo | Historia de usuario |
| Prioridad | Alta |
| Estado | To Do |
| Sprint | Sprint 6 |
| Responsable | @GJG16 |
| Inicio | 2026-06-08 |
| Duración | 14 dias |

**Descripción:**
Conectar el ConnectionManager existente en realtime.py al flujo de tickets para que los agentes reciban notificaciones push cuando se cree un nuevo ticket y los usuarios vean actualizaciones de estado en tiempo real via WebSocket.

**Checklist:**
- [ ] Importar realtime_manager en main.py y registrar ruta WebSocket
- [ ] Crear endpoint WebSocket /ws/notifications con autenticacion por token
- [ ] Validar token JWT en la conexion WebSocket antes de aceptarla
- [ ] Emitir broadcast_json() al crear un ticket nuevo en routes/tickets.py
- [ ] Emitir broadcast_json() al actualizar estado de un ticket
- [ ] Incluir tipo de evento en el mensaje (ticket_created, ticket_updated)
- [ ] Crear NotificationService en Angular con WebSocket client nativo
- [ ] Conectar WebSocket al hacer login y desconectar al hacer logout
- [ ] Implementar reconexion automatica con backoff exponencial
- [ ] Crear componente ToastNotification para mostrar alertas visuales
- [ ] Mostrar badge con contador de notificaciones no leidas en el sidebar
- [ ] Reproducir sonido sutil al recibir notificacion (opcional, configurable)
- [ ] Agregar test unitario para verificar que broadcast se emite al crear ticket

**Criterios de aceptación:**
- [ ] Al crear un ticket, los agentes conectados reciben notificacion instantanea
- [ ] Al cambiar estado de un ticket, el usuario creador ve la actualizacion
- [ ] La conexion WebSocket se reconecta automaticamente si se pierde
- [ ] Las notificaciones se muestran como toast visual en la interfaz

---

### Issue #20 — Sistema de Categorias y SLA para Tickets

| Campo | Valor |
|---|---|
| Título | Sistema de Categorias y SLA para Tickets |
| Tipo | Historia de usuario |
| Prioridad | Media |
| Estado | To Do |
| Sprint | Sprint 6 |
| Responsable | @AdrianoCuevas |
| Inicio | 2026-06-08 |
| Duración | 14 dias |

**Descripción:**
Agregar sistema de categorias para clasificar tickets por tipo de incidencia y calculo automatico de SLA (Service Level Agreement) segun prioridad, permitiendo medir tiempos de respuesta y cumplimiento.

**Checklist:**
- [ ] Crear enum TicketCategory en schemas.py (hardware, software, red, accesos, otro)
- [ ] Agregar campo categoria: TicketCategory al modelo TicketBase
- [ ] Agregar campo sla_horas: int al modelo Ticket (calculado segun prioridad)
- [ ] Implementar logica de calculo SLA: critica=4h, alta=8h, media=24h, baja=48h
- [ ] Calcular sla_horas automaticamente al crear ticket en routes/tickets.py
- [ ] Agregar campo fecha_primera_respuesta al modelo Ticket
- [ ] Registrar fecha_primera_respuesta al agregar primer comentario de agente
- [ ] Agregar selector de categoria en ticket-create-modal.component
- [ ] Agregar selector de categoria en ticket-form.component.html
- [ ] Mostrar badge de categoria en tickets-list con colores diferenciados
- [ ] Calcular y mostrar indicador SLA (a tiempo / vencido / proximo a vencer)
- [ ] Mostrar indicador SLA en tarjetas del Kanban board
- [ ] Agregar seccion "Cumplimiento SLA" en ReportsComponent
- [ ] Migrar tickets existentes con categoria "otro" y sla_horas segun su prioridad

**Criterios de aceptación:**
- [ ] Al crear un ticket se debe seleccionar una categoria obligatoriamente
- [ ] El sistema muestra visualmente si un ticket esta dentro o fuera del SLA
- [ ] Los reportes incluyen porcentaje de cumplimiento SLA por agente
- [ ] Los tickets existentes se migran correctamente con valores por defecto

---

### Issue #21 — Panel de Administracion de Usuarios

| Campo | Valor |
|---|---|
| Título | Panel de Administracion de Usuarios |
| Tipo | Historia de usuario |
| Prioridad | Alta |
| Estado | Backlog |
| Sprint | Sprint 7 |
| Responsable | @AdrianoCuevas |
| Inicio | 2026-06-22 |
| Duración | 14 dias |

**Descripción:**
Crear vista completa en el frontend para que el administrador pueda gestionar usuarios del sistema: ver listado, cambiar roles, activar/desactivar cuentas y eliminar usuarios con registro de auditoria.

**Checklist:**
- [ ] Crear carpeta frontend/src/app/components/admin/user-management/
- [ ] Crear UserManagementComponent con tabla de usuarios
- [ ] Consumir UsuariosService.getUsuarios() para cargar lista de usuarios
- [ ] Mostrar columnas: nombre, email, rol, activo, fecha de creacion
- [ ] Agregar dropdown para cambiar rol (user / agent / admin) en cada fila
- [ ] Llamar UsuariosService.updateUsuario() al cambiar rol
- [ ] Agregar toggle o boton para activar/desactivar usuario
- [ ] Agregar boton "Eliminar" con dialogo de confirmacion
- [ ] Llamar UsuariosService.deleteUsuario() al confirmar eliminacion
- [ ] Mostrar toast de exito o error despues de cada accion
- [ ] Agregar ruta /admin/users en app.routes.ts con AuthGuard (role: admin)
- [ ] Agregar boton "Gestionar Usuarios" en sidebar del DashboardComponent para admin
- [ ] Aplicar estilos consistentes con el resto de la aplicacion
- [ ] Agregar data-testid en elementos para futuras pruebas E2E
- [ ] Verificar que usuarios no-admin son redirigidos si intentan acceder

**Criterios de aceptación:**
- [ ] El admin puede ver la lista completa de usuarios registrados
- [ ] El admin puede cambiar el rol de cualquier usuario desde la interfaz
- [ ] El admin puede desactivar o eliminar usuarios con registro en auditoria
- [ ] Usuarios sin rol admin no pueden acceder a la ruta /admin/users

---

### Issue #22 — Pruebas E2E y Limpieza de Codigo de Debug

| Campo | Valor |
|---|---|
| Título | Pruebas E2E y Limpieza de Codigo de Debug |
| Tipo | Tarea tecnica |
| Prioridad | Alta |
| Estado | Done |
| Sprint | Sprint 7 |
| Responsable | @franco27-dev |
| Inicio | 2026-06-22 |
| Duración | 14 dias |

**Descripción:**
Ejecutar y validar la suite completa de pruebas E2E con Playwright que cubre el ciclo de vida del ticket a traves de los 3 roles, y eliminar todo el codigo de debug que expone informacion sensible en produccion.

**Checklist:**
- [x] Instalar dependencias de Playwright con npx playwright install
- [x] Ejecutar seed_db.py para inicializar datos de prueba
- [x] Levantar backend en localhost:8000 y frontend en localhost:4200
- [x] Ejecutar Fase 1 E2E: Login como usuario y crear ticket (4 tests)
- [x] Ejecutar Fase 2 E2E: Login como agente, tomar ticket, comentar, cambiar prioridad (4 tests)
- [x] Ejecutar Fase 3 E2E: Login como admin, verificar dashboard, eliminar ticket (4 tests)
- [x] Documentar resultado de los 12 tests con capturas de pantalla
- [x] Eliminar console.debug linea 23 de auth.interceptor.ts (log de URL y token)
- [x] Eliminar console.debug linea 27 de auth.interceptor.ts (preview de token)
- [x] Eliminar console.debug linea 37 de auth.interceptor.ts (Authorization header)
- [x] Eliminar console.debug linea 46 de auth.interceptor.ts (401 detected)
- [x] Buscar y eliminar console.log de debug en kanban.component.ts
- [x] Buscar y eliminar middleware de debug en backend (X-Request-ID logger)
- [x] Verificar que CI pipeline pasa sin errores despues de la limpieza
- [ ] Crear PR con titulo "fix: limpiar codigo de debug y validar E2E"

**Criterios de aceptación:**
- [x] Los 12 tests E2E pasan sin errores en ejecucion local
- [x] No hay console.debug ni console.log de debug en codigo de produccion
- [ ] El pipeline CI ejecuta exitosamente despues de los cambios
- [ ] Los resultados de las pruebas estan documentados en el PR

---

### Issue #23 — Documentacion Tecnica y Entrega Final

| Campo | Valor |
|---|---|
| Título | Documentacion Tecnica y Entrega Final |
| Tipo | Tarea tecnica |
| Prioridad | Media |
| Estado | Backlog |
| Sprint | Sprint 8 |
| Responsable | @GJG16 |
| Inicio | 2026-07-06 |
| Duración | 14 dias |

**Descripción:**
Documentar la arquitectura completa del sistema, configurar environments de produccion en Angular para eliminar URLs hardcoded, generar documentacion de la API y preparar el proyecto para entrega final.

**Checklist:**
- [ ] Crear archivo frontend/src/environments/environment.ts con apiUrl: http://localhost:8000/api
- [ ] Crear archivo frontend/src/environments/environment.prod.ts con apiUrl de produccion
- [ ] Reemplazar http://localhost:8000/api en auth.service.ts por environment.apiUrl
- [ ] Reemplazar http://localhost:8000/api en ticket.service.ts por environment.apiUrl
- [ ] Reemplazar http://localhost:8000/api en usuarios.service.ts por environment.apiUrl
- [ ] Verificar que ng build --configuration=production usa environment.prod.ts
- [ ] Actualizar README.md con diagrama de arquitectura (backend + frontend + MongoDB)
- [ ] Documentar stack tecnologico: FastAPI, Angular 19, MongoDB, Motor, JWT
- [ ] Agregar seccion de instalacion paso a paso en README.md
- [ ] Agregar seccion de ejecucion con Docker en README.md
- [ ] Verificar que Swagger UI (/docs) muestra todos los endpoints documentados
- [ ] Exportar coleccion de endpoints como archivo OpenAPI JSON
- [ ] Crear archivo CHANGELOG.md con historial de versiones
- [ ] Revisar y limpiar dependencias no utilizadas en requirements.txt y package.json
- [ ] Realizar despliegue de prueba en plataforma cloud (Render, Railway o AWS)

**Criterios de aceptación:**
- [ ] La aplicacion funciona correctamente con URLs configurables por environment
- [ ] El README.md contiene instrucciones claras de instalacion, ejecucion y despliegue
- [ ] La documentacion de API esta accesible y completa en /docs
- [ ] El proyecto compila sin warnings en modo produccion

---

