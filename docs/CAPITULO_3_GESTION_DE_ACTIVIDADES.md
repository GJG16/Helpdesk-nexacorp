# Capítulo 3: Gestión de Actividades

## 3.1 Características del Proyecto

**Nombre del proyecto:** Helpdesk - Sistema de Gestión de Tickets

**Duración referencial del informe:** 90 días / 16 semanas

**Cronograma operativo aprobado:** 8 sprints exactos de 2 semanas cada uno, equivalentes a 112 días calendario, desde el lunes 30 de marzo de 2026 hasta el domingo 19 de julio de 2026.

**Estructura de trabajo:**
- Sprint 1: 30/03/2026 al 12/04/2026
- Sprint 2: 13/04/2026 al 26/04/2026
- Sprint 3: 27/04/2026 al 10/05/2026
- Sprint 4: 11/05/2026 al 24/05/2026
- Sprint 5: 25/05/2026 al 07/06/2026
- Sprint 6: 08/06/2026 al 21/06/2026
- Sprint 7: 22/06/2026 al 05/07/2026
- Sprint 8: 06/07/2026 al 19/07/2026

**Equipo exclusivo de GitHub y roles técnicos:**

| Usuario | Rol principal | Responsabilidad técnica |
|---|---|---|
| @adriano08-xc | Backend / Base de Datos | API con FastAPI, modelos de datos, MongoDB, seguridad y autenticación |
| @franco27-dev | Frontend / UX Angular | Componentes Angular, navegación, Kanban, formularios y estado visual |
| @tu-usuario | QA / DevOps / E2E | Automatización de pruebas, validación funcional, despliegue y control de calidad |

La distribución de trabajo se organiza para mantener una carga equilibrada y sin sobrecarga diaria entre los tres integrantes, priorizando la secuencia técnica del producto: infraestructura, seguridad, experiencia de usuario, verificación y despliegue.

## 3.2 Componentes del Tablero de Control

El tablero de control del proyecto en GitHub Projects se organiza con las siguientes columnas Kanban:

- Backlog
- To Do
- In Progress
- Code Review
- Done

Estas columnas permiten visualizar el flujo completo de desarrollo, desde la idea inicial hasta la validación final y cierre técnico de cada issue.

## 3.3 Características de la Actividad

Cada Issue del tablero contiene, como mínimo, los siguientes atributos:

- Título
- Descripción
- Responsable
- Prioridad: Alta, Media o Baja
- Tipo: Feature, Bug o Tarea
- Estado
- Sprint asignado
- Fecha de inicio
- Duración estimada

**Ejemplo práctico**

| Campo | Valor |
|---|---|
| Título del Issue | Inicializar Backend con FastAPI y Conexión a MongoDB |
| Responsable | @adriano08-xc |
| Prioridad | Alta |
| Tipo | Feature |
| Estado | To Do |
| Sprint asignado | Sprint 1 |
| Fecha de inicio | 30/03/2026 |
| Duración estimada | 10 días |

**Checklist técnico del issue**

- [ ] Crear la estructura inicial del proyecto FastAPI
- [ ] Configurar la conexión asíncrona con MongoDB
- [ ] Definir la colección base para tickets y usuarios
- [ ] Validar el arranque del servicio con un endpoint de estado
- [ ] Registrar la integración inicial en GitHub Projects

## 3.4 Actividades en el Tablero de Control (Matriz Principal)

La siguiente matriz consolida las actividades críticas de desarrollo para el sistema de gestión de tickets. El orden mantiene la secuencia lógica del producto: configuración de infraestructura, autenticación, desarrollo de la interfaz, métricas, pruebas y despliegue.

| Título del Issue | Tipo | Prioridad | Estado | Sprint | Responsable | Inicio | Duración |
|---|---|---|---|---|---|---|---|
| Inicializar Backend con FastAPI y Conexión a MongoDB | Feature | Alta | In Progress | Sprint 1 | @adriano08-xc | 30/03/2026 | 10 días |
| Modelado de Esquemas Pydantic y Colecciones MongoDB | Tarea | Alta | To Do | Sprint 1 | @adriano08-xc | 03/04/2026 | 7 días |
| Autenticación JWT con Access/Refresh Tokens | Feature | Alta | To Do | Sprint 2 | @adriano08-xc | 13/04/2026 | 10 días |
| Control RBAC en API y Protección de Rutas | Feature | Alta | To Do | Sprint 3 | @adriano08-xc | 27/04/2026 | 8 días |
| Guard de Rutas y Menús por Rol en Angular | Feature | Alta | To Do | Sprint 3 | @franco27-dev | 29/04/2026 | 6 días |
| CRUD de Tickets en Angular y Servicios HTTP | Feature | Alta | To Do | Sprint 4 | @franco27-dev | 11/05/2026 | 10 días |
| Tablero Kanban Drag-and-Drop para Tickets | Feature | Alta | To Do | Sprint 5 | @franco27-dev | 25/05/2026 | 10 días |
| Dashboard de Métricas Operativas | Feature | Media | Backlog | Sprint 6 | @tu-usuario | 08/06/2026 | 7 días |
| Suite de Pruebas E2E con Playwright | Tarea | Alta | Backlog | Sprint 7 | @tu-usuario | 22/06/2026 | 10 días |
| Pipeline de Despliegue y Validación Final | Tarea | Alta | Backlog | Sprint 8 | @tu-usuario | 06/07/2026 | 8 días |

### Flujo lógico de ejecución

1. Configuración de BD y Backend (Sprint 1-2)
2. Módulo de Autenticación y Roles (Sprint 2-3)
3. CRUD de tickets y Tablero Kanban en Angular (Sprint 4-5)
4. Dashboard de métricas (Sprint 6)
5. Pruebas E2E y Despliegue (Sprint 7-8)

## 3.5 Configuración de GitHub

**Labels a crear**

| Label | Categoría | Uso |
|---|---|---|
| feature | Tipo | Nueva funcionalidad de producto |
| bug | Tipo | Corrección de error funcional o visual |
| task | Tipo | Tarea técnica de desarrollo, pruebas o integración |
| priority-high | Prioridad | Trabajo crítico que desbloquea otros componentes |
| priority-medium | Prioridad | Trabajo importante pero no bloqueante |
| priority-low | Prioridad | Ajustes menores o mejoras de apoyo |

**Milestones del proyecto**

| Milestone | Sprint | Inicio | Fin |
|---|---|---|---|
| Sprint 1 | 1 | 30/03/2026 | 12/04/2026 |
| Sprint 2 | 2 | 13/04/2026 | 26/04/2026 |
| Sprint 3 | 3 | 27/04/2026 | 10/05/2026 |
| Sprint 4 | 4 | 11/05/2026 | 24/05/2026 |
| Sprint 5 | 5 | 25/05/2026 | 07/06/2026 |
| Sprint 6 | 6 | 08/06/2026 | 21/06/2026 |
| Sprint 7 | 7 | 22/06/2026 | 05/07/2026 |
| Sprint 8 | 8 | 06/07/2026 | 19/07/2026 |

La configuración anterior permite que GitHub Projects funcione como una herramienta real de control técnico: los labels clasifican el trabajo, los milestones ordenan el calendario y la matriz principal mantiene trazabilidad entre alcance, responsable, sprint y fecha de inicio.