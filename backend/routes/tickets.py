import math
from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from database import get_database
from models.schemas import (
    Ticket,
    TicketCreate,
    TicketFilter,
    TicketPageResponse,
    TicketStats,
    TicketStatus,
    TicketUpdate,
)
from realtime import realtime_manager
from security import decode_token

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

def _extract_token(authorization: Optional[str], token: Optional[str]) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return token


def _serialize_ticket(ticket_doc: dict) -> dict:
    ticket_doc["id"] = str(ticket_doc.pop("_id"))
    return ticket_doc


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    token: Optional[str] = None,
    db=Depends(get_database),
):
    """Obtener usuario actual desde Bearer token o query token."""
    raw_token = _extract_token(authorization, token)

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )

    token_data = decode_token(raw_token)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    user = await db.usuarios.find_one({"_id": ObjectId(token_data.user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    user["id"] = str(user.pop("_id"))
    user.pop("password_hash", None)
    return user


@router.get("/stats", response_model=TicketStats)
async def get_ticket_stats(db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener métricas de tickets para dashboard."""
    total = await db.tickets.count_documents({})
    abiertos = await db.tickets.count_documents({"estado": TicketStatus.ABIERTO})
    en_progreso = await db.tickets.count_documents({"estado": TicketStatus.EN_PROGRESO})
    resueltos = await db.tickets.count_documents({"estado": TicketStatus.RESUELTO})
    cerrados = await db.tickets.count_documents({"estado": TicketStatus.CERRADO})

    return TicketStats(
        total=total,
        abiertos=abiertos,
        en_progreso=en_progreso,
        resueltos=resueltos,
        cerrados=cerrados,
    )


@router.get("/paginated", response_model=TicketPageResponse)
async def get_tickets_paginated(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db=Depends(get_database),
    current_user=Depends(get_current_user),
):
    """Obtener tickets paginados para listados grandes."""
    total = await db.tickets.count_documents({})
    skip = (page - 1) * page_size

    cursor = db.tickets.find().sort("fecha_creacion", -1).skip(skip).limit(page_size)
    tickets = await cursor.to_list(length=page_size)

    return TicketPageResponse(
        items=[_serialize_ticket(ticket) for ticket in tickets],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)) if page_size else 1,
    )


@router.get("/", response_model=List[Ticket])
async def get_tickets(db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener todos los tickets"""
    tickets = await db.tickets.find().sort("fecha_creacion", -1).to_list(None)
    return [_serialize_ticket(ticket) for ticket in tickets]


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener ticket por ID"""
    try:
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )

        return _serialize_ticket(ticket)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de ticket inválido",
        )


@router.post("/", response_model=Ticket)
async def create_ticket(ticket_data: TicketCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Crear nuevo ticket"""
    ticket_dict = ticket_data.model_dump()
    ticket_dict["fecha_creacion"] = datetime.utcnow()
    ticket_dict["fecha_actualizacion"] = datetime.utcnow()

    result = await db.tickets.insert_one(ticket_dict)

    created_ticket = await db.tickets.find_one({"_id": result.inserted_id})
    created_ticket = _serialize_ticket(created_ticket)

    await realtime_manager.broadcast_json(
        {
            "event": "ticket_created",
            "ticket_id": created_ticket["id"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return created_ticket


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: str, ticket_update: TicketUpdate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Actualizar ticket"""
    try:
        update_data = {k: v for k, v in ticket_update.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar",
            )

        update_data["fecha_actualizacion"] = datetime.utcnow()

        # Si se cierra, agregar fecha de resolución
        if ticket_update.estado in (TicketStatus.RESUELTO, TicketStatus.CERRADO):
            update_data["fecha_resolucion"] = datetime.utcnow()

        result = await db.tickets.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )

        updated_ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        updated_ticket = _serialize_ticket(updated_ticket)

        await realtime_manager.broadcast_json(
            {
                "event": "ticket_updated",
                "ticket_id": updated_ticket["id"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return updated_ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Eliminar ticket"""
    try:
        # Solo admin o quien creó el ticket puede eliminarlo
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )

        if current_user.get("rol") != "admin" and ticket.get("usuario_id") != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar este ticket",
            )

        result = await db.tickets.delete_one({"_id": ObjectId(ticket_id)})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado",
            )

        await realtime_manager.broadcast_json(
            {
                "event": "ticket_deleted",
                "ticket_id": ticket_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/filter", response_model=List[Ticket])
async def filter_tickets(filter_data: TicketFilter, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Filtrar tickets"""
    query = {}

    if filter_data.estado:
        query["estado"] = filter_data.estado
    if filter_data.usuario_id:
        query["usuario_id"] = filter_data.usuario_id
    if filter_data.asignado_a:
        query["asignado_a"] = filter_data.asignado_a
    if filter_data.prioridad:
        query["prioridad"] = filter_data.prioridad
    
    # Filtro de fechas
    if filter_data.fecha_desde or filter_data.fecha_hasta:
        query["fecha_creacion"] = {}
        if filter_data.fecha_desde:
            query["fecha_creacion"]["$gte"] = filter_data.fecha_desde
        if filter_data.fecha_hasta:
            query["fecha_creacion"]["$lte"] = filter_data.fecha_hasta

    tickets = await db.tickets.find(query).sort("fecha_creacion", -1).to_list(None)
    return [_serialize_ticket(ticket) for ticket in tickets]
