from datetime import datetime, timezone
from typing import List, Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.database import get_database
from backend.dependencies import get_current_user
from backend.models.schemas import (
    Ticket,
    TicketCreate,
    TicketComment,
    TicketCommentCreate,
    TicketFilter,
    TicketStatus,
    TicketUpdate,
    Priority,
)
from backend.audit import log_deletion

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _serialize_ticket(ticket_doc: dict) -> dict:
    ticket_doc["id"] = str(ticket_doc.pop("_id"))
    return ticket_doc


def _is_admin(user: dict) -> bool:
    return user.get("rol") == "admin"


def _is_agent(user: dict) -> bool:
    return user.get("rol") == "agent"


def _ticket_scope_query(current_user: dict) -> dict:
    if _is_admin(current_user) or _is_agent(current_user):
        return {}
    return {"usuario_id": current_user.get("id")}


def _is_ticket_owner(ticket: dict, current_user: dict) -> bool:
    return ticket.get("usuario_id") == current_user.get("id")


@router.get("/", response_model=dict)
async def get_tickets(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_database),
    current_user=Depends(get_current_user),
):
    """Obtener tickets paginados."""
    query = _ticket_scope_query(current_user)
    total = await db.tickets.count_documents(query)
    skip = (page - 1) * limit
    tickets = await db.tickets.find(query).sort("fecha_creacion", -1).skip(skip).limit(limit).to_list(limit)
    return {
        "items": [_serialize_ticket(t) for t in tickets],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/stats", response_model=dict)
async def get_ticket_stats(db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener métricas rápidas de tickets según el rol del usuario."""
    query = _ticket_scope_query(current_user)
    
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}}
    ]
    
    results = await db.tickets.aggregate(pipeline).to_list(length=None)
    
    stats = {
        "total": 0,
        "abiertos": 0,
        "en_progreso": 0,
        "resueltos": 0,
        "cerrados": 0
    }
    
    for item in results:
        estado = item["_id"]
        count = item["count"]
        stats["total"] += count
        if estado == "abierto":
            stats["abiertos"] += count
        elif estado == "en_progreso":
            stats["en_progreso"] += count
        elif estado == "resuelto":
            stats["resueltos"] += count
        elif estado == "cerrado":
            stats["cerrados"] += count
            
    return stats


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener ticket por ID."""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )

        if not (_is_admin(current_user) or _is_agent(current_user) or _is_ticket_owner(ticket, current_user)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este ticket",
            )

        return _serialize_ticket(ticket)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de ticket inválido",
        )


@router.post("/", response_model=Ticket)
async def create_ticket(ticket_data: TicketCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Crear nuevo ticket."""
    if _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los administradores no pueden crear tickets",
        )

    ticket_dict = ticket_data.model_dump()
    ticket_dict["usuario_id"] = current_user.get("id")

    if current_user.get("rol") == "user":
        ticket_dict["prioridad"] = Priority.MEDIA.value

    now = datetime.now(timezone.utc)
    ticket_dict["fecha_creacion"] = now
    ticket_dict["fecha_actualizacion"] = now
    
    # Calculate SLA
    from datetime import timedelta
    sla_hours = {
        Priority.CRITICA.value: 2,
        Priority.ALTA.value: 8,
        Priority.MEDIA.value: 24,
        Priority.BAJA.value: 48,
    }
    prioridad = ticket_dict.get("prioridad", Priority.MEDIA.value)
    if hasattr(prioridad, "value"):
        prioridad = prioridad.value
    ticket_dict["fecha_vencimiento_sla"] = now + timedelta(hours=sla_hours.get(prioridad, 24))
    
    ticket_dict["historial"] = [
        {
            "campo": "creacion",
            "valor_anterior": None,
            "valor_nuevo": "abierto",
            "usuario_id": current_user.get("id"),
            "usuario_nombre": current_user.get("nombre"),
            "fecha": now,
        }
    ]

    result = await db.tickets.insert_one(ticket_dict)
    created_ticket = await db.tickets.find_one({"_id": result.inserted_id})
    serialized_ticket = _serialize_ticket(created_ticket)
    
    # WebSocket notification for agents and admins
    from backend.websockets import manager
    await manager.broadcast({
        "type": "TICKET_CREATED",
        "ticket_id": serialized_ticket["id"],
        "message": f"Nuevo ticket creado: {serialized_ticket['titulo']}"
    })
    
    return serialized_ticket


@router.get("/{ticket_id}/comments", response_model=List[TicketComment])
async def get_ticket_comments(ticket_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener comentarios de un ticket."""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        if not (_is_admin(current_user) or _is_agent(current_user) or _is_ticket_owner(ticket, current_user)):
            raise HTTPException(status_code=403, detail="No tienes permiso para ver estos comentarios")

        comments = await db.comments.find({"ticket_id": ticket_id}).sort("fecha_creacion", 1).to_list(None)
        for c in comments:
            c["id"] = str(c.pop("_id"))
        return comments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{ticket_id}/comments", response_model=TicketComment)
async def create_ticket_comment(ticket_id: str, comment_data: TicketCommentCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Crear un comentario en un ticket."""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        if not (_is_admin(current_user) or _is_agent(current_user) or _is_ticket_owner(ticket, current_user)):
            raise HTTPException(status_code=403, detail="No tienes permiso para comentar en este ticket")

        now = datetime.now(timezone.utc)
        comment_dict = comment_data.model_dump()
        comment_dict["ticket_id"] = ticket_id
        comment_dict["usuario_id"] = current_user.get("id")
        comment_dict["nombre_autor"] = current_user.get("nombre")
        comment_dict["rol_autor"] = current_user.get("rol")
        comment_dict["fecha_creacion"] = now

        result = await db.comments.insert_one(comment_dict)
        await db.tickets.update_one({"_id": ObjectId(ticket_id)}, {"$set": {"fecha_actualizacion": now}})

        created_comment = await db.comments.find_one({"_id": result.inserted_id})
        created_comment["id"] = str(created_comment.pop("_id"))
        
        # WebSocket notification
        from backend.websockets import manager
        
        # Notify the ticket owner if the commenter is an agent/admin
        if ticket.get("usuario_id") != current_user.get("id"):
            await manager.send_personal_message({
                "type": "NEW_COMMENT",
                "ticket_id": ticket_id,
                "message": f"Nuevo comentario en tu ticket: {ticket.get('titulo')}"
            }, ticket.get("usuario_id"))
            
        # Notify the assigned agent if the commenter is the user
        if ticket.get("asignado_a") and ticket.get("asignado_a") != current_user.get("id"):
            await manager.send_personal_message({
                "type": "NEW_COMMENT",
                "ticket_id": ticket_id,
                "message": f"Nuevo comentario en el ticket que tienes asignado: {ticket.get('titulo')}"
            }, ticket.get("asignado_a"))
        
        return created_comment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: str, ticket_update: TicketUpdate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Actualizar ticket con historial de cambios."""
    try:
        existing_ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not existing_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )

        update_data = {k: v for k, v in ticket_update.model_dump().items() if v is not None}

        if _is_admin(current_user):
            pass
        elif _is_agent(current_user):
            allowed_fields = {"estado", "prioridad", "asignado_a"}
            if any(field not in allowed_fields for field in update_data.keys()):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El agente solo puede actualizar estado, prioridad o asignación propia",
                )
            if "asignado_a" in update_data and update_data["asignado_a"] != current_user.get("id"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El agente solo puede asignarse a sí mismo",
                )
            already_assigned = existing_ticket.get("asignado_a") == current_user.get("id")
            self_assigning = update_data.get("asignado_a") == current_user.get("id")
            if not already_assigned and not self_assigning:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El agente debe asignarse el ticket antes de modificarlo",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores o agentes pueden actualizar tickets",
            )

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar",
            )

        now = datetime.now(timezone.utc)
        update_data["fecha_actualizacion"] = now

        # SLA Recalculation if priority changes
        if "prioridad" in update_data and update_data["prioridad"] != existing_ticket.get("prioridad"):
            from datetime import timedelta
            sla_hours = {
                Priority.CRITICA.value: 2,
                Priority.ALTA.value: 8,
                Priority.MEDIA.value: 24,
                Priority.BAJA.value: 48,
            }
            new_prio = update_data["prioridad"]
            if hasattr(new_prio, "value"):
                new_prio = new_prio.value
            
            # Recalculate SLA due date based on creation time or from now?
            # Typically SLA is recalculated based on creation date or when priority changed.
            # Let's say we set the SLA from NOW when priority changes, since we discovered the issue is more urgent.
            update_data["fecha_vencimiento_sla"] = now + timedelta(hours=sla_hours.get(new_prio, 24))


        # Historial de cambios
        history_entries = []
        for field, new_val in update_data.items():
            if field == "fecha_actualizacion":
                continue
            old_val = existing_ticket.get(field)
            if str(old_val) != str(new_val):
                history_entries.append({
                    "campo": field,
                    "valor_anterior": str(old_val) if old_val else None,
                    "valor_nuevo": str(new_val),
                    "usuario_id": current_user.get("id"),
                    "usuario_nombre": current_user.get("nombre"),
                    "fecha": now,
                })

        if ticket_update.estado in (TicketStatus.RESUELTO, TicketStatus.CERRADO):
            if ticket_update.estado == TicketStatus.RESUELTO and _is_agent(current_user):
                comentarios = await db.comments.find({"ticket_id": ticket_id, "usuario_id": current_user.get("id")}).to_list(None)
                if not comentarios:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Debes añadir un comentario o nota de resolución antes de marcar el ticket como resuelto."
                    )
            update_data["fecha_resolucion"] = now

        update_ops = {"$set": update_data}
        if history_entries:
            update_ops["$push"] = {"historial": {"$each": history_entries}}

        await db.tickets.update_one({"_id": ObjectId(ticket_id)}, update_ops)

        updated_ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        
        # WebSocket notification
        from backend.websockets import manager
        if updated_ticket.get("usuario_id") != current_user.get("id"):
            await manager.send_personal_message({
                "type": "TICKET_UPDATED",
                "ticket_id": ticket_id,
                "message": f"Tu ticket '{updated_ticket.get('titulo')}' ha sido actualizado."
            }, updated_ticket.get("usuario_id"))
            
        return _serialize_ticket(updated_ticket)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{ticket_id}/history")
async def get_ticket_history(ticket_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener historial de cambios de un ticket."""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")
        if not (_is_admin(current_user) or _is_agent(current_user) or _is_ticket_owner(ticket, current_user)):
            raise HTTPException(status_code=403, detail="No tienes permiso")
        return ticket.get("historial", [])
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Eliminar ticket (solo admin)."""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )
        if not _is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden eliminar tickets",
            )

        await log_deletion(db, action="delete_ticket", resource_type="ticket", resource_id=ticket_id, actor_admin_id=current_user.get("id"))
        await db.tickets.delete_one({"_id": ObjectId(ticket_id)})
        # También eliminar comentarios asociados
        await db.comments.delete_many({"ticket_id": ticket_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/filter", response_model=dict)
async def filter_tickets(
    filter_data: TicketFilter,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_database),
    current_user=Depends(get_current_user),
):
    """Filtrar tickets con paginación."""
    query = _ticket_scope_query(current_user)

    if filter_data.estado:
        query["estado"] = filter_data.estado
    if filter_data.usuario_id and _is_admin(current_user):
        query["usuario_id"] = filter_data.usuario_id
    if filter_data.asignado_a and (_is_admin(current_user) or _is_agent(current_user)):
        query["asignado_a"] = filter_data.asignado_a
    if filter_data.prioridad:
        query["prioridad"] = filter_data.prioridad
    if filter_data.tipo:
        query["tipo"] = filter_data.tipo
    if filter_data.busqueda:
        query["$or"] = [
            {"titulo": {"$regex": filter_data.busqueda, "$options": "i"}},
            {"descripcion": {"$regex": filter_data.busqueda, "$options": "i"}}
        ]

    if filter_data.fecha_desde or filter_data.fecha_hasta:
        query["fecha_creacion"] = {}
        if filter_data.fecha_desde:
            query["fecha_creacion"]["$gte"] = filter_data.fecha_desde
        if filter_data.fecha_hasta:
            query["fecha_creacion"]["$lte"] = filter_data.fecha_hasta

    total = await db.tickets.count_documents(query)
    skip = (page - 1) * limit
    tickets = await db.tickets.find(query).sort("fecha_creacion", -1).skip(skip).limit(limit).to_list(limit)
    return {
        "items": [_serialize_ticket(t) for t in tickets],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }

from pydantic import BaseModel, Field

class CSATRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

@router.post("/{ticket_id}/csat", response_model=Ticket)
async def submit_csat(ticket_id: str, csat_data: CSATRequest, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Enviar CSAT para un ticket resuelto o cerrado."""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")
            
        if not _is_ticket_owner(ticket, current_user):
            raise HTTPException(status_code=403, detail="Solo el creador del ticket puede enviar CSAT")
            
        if ticket.get("estado") not in ["resuelto", "cerrado"]:
            raise HTTPException(status_code=400, detail="Solo se puede calificar un ticket resuelto o cerrado")
            
        if ticket.get("csat_rating"):
            raise HTTPException(status_code=400, detail="Ya se ha enviado CSAT para este ticket")

        now = datetime.now(timezone.utc)
        update_data = {
            "csat_rating": csat_data.rating,
            "csat_comment": csat_data.comment,
            "fecha_actualizacion": now
        }
        
        await db.tickets.update_one({"_id": ObjectId(ticket_id)}, {"$set": update_data})
        updated_ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        return _serialize_ticket(updated_ticket)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

import os
from fastapi import UploadFile, File

UPLOAD_DIR = "backend/uploads"

@router.post("/{ticket_id}/adjuntos")
async def upload_attachment(ticket_id: str, file: UploadFile = File(...), db=Depends(get_database), current_user=Depends(get_current_user)):
    """Subir archivo adjunto al ticket"""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")
            
        if not (_is_admin(current_user) or _is_agent(current_user) or _is_ticket_owner(ticket, current_user)):
            raise HTTPException(status_code=403, detail="Sin permisos")

        file_path = os.path.join(UPLOAD_DIR, f"{ticket_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        attachment_data = {
            "filename": file.filename,
            "url": f"/uploads/{ticket_id}_{file.filename}",
            "uploaded_at": datetime.now(timezone.utc),
            "uploaded_by": current_user.get("id")
        }

        await db.tickets.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$push": {"adjuntos": attachment_data}}
        )

        return {"filename": file.filename, "url": attachment_data["url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
