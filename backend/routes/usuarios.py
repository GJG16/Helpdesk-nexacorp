from typing import List, Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Header, HTTPException, status

from backend.database import get_database
from backend.models.schemas import User, UserUpdate
from backend.audit import log_deletion
from backend.security import decode_token, hash_password
from backend.dependencies import get_current_user, _serialize_user

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("/perfil/me", response_model=User)
async def get_perfil(current_user=Depends(get_current_user)):
    """Obtener perfil del usuario actual"""
    return current_user


from fastapi import Query

@router.get("/", response_model=dict)
async def get_usuarios(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_database),
    current_user=Depends(get_current_user)
):
    """Obtener todos los usuarios con paginación"""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver todos los usuarios",
        )

    total = await db.usuarios.count_documents({})
    skip = (page - 1) * limit
    usuarios = await db.usuarios.find().sort("fecha_creacion", -1).skip(skip).limit(limit).to_list(limit)
    return {
        "items": [_serialize_user(user) for user in usuarios],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{usuario_id}", response_model=User)
async def get_usuario(usuario_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener usuario por ID"""
    try:
        if current_user.get("rol") != "admin" and current_user.get("id") != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este usuario",
            )

        user = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        return _serialize_user(user)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido",
        )


@router.put("/{usuario_id}", response_model=User)
async def update_usuario(usuario_id: str, user_update: UserUpdate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Actualizar usuario"""
    if current_user.get("rol") != "admin" and current_user.get("id") != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario",
        )

    try:
        update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}

        # Hashear contraseña si se está actualizando
        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        if current_user.get("rol") != "admin":
            update_data.pop("rol", None)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar",
            )

        result = await db.usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        updated_user = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        return _serialize_user(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Eliminar usuario (solo admin)"""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar usuarios",
        )

    try:
        user_to_delete = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        await log_deletion(
            db,
            action="delete_user",
            resource_type="user",
            resource_id=usuario_id,
            actor_admin_id=current_user.get("id"),
        )

        result = await db.usuarios.delete_one({"_id": ObjectId(usuario_id)})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

