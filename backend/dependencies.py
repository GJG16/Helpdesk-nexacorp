"""Dependencias compartidas de autenticación para todos los routers."""

from typing import Optional

from bson.objectid import ObjectId
from fastapi import Depends, Header, HTTPException, status

from backend.database import get_database
from backend.security import decode_token


def _extract_token(authorization: Optional[str], token: Optional[str]) -> Optional[str]:
    """Extraer token de Authorization header o query param."""
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return token


def _serialize_user(user: dict) -> dict:
    """Serializar documento de usuario MongoDB a dict con id string."""
    user["id"] = str(user.pop("_id"))
    user.pop("password_hash", None)
    return user


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    token: Optional[str] = None,
    db=Depends(get_database),
):
    """Obtener usuario actual del token JWT."""
    raw_token = _extract_token(authorization, token)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )

    token_data = decode_token(raw_token, expected_type="access")
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

    return _serialize_user(user)


def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependencia que requiere rol de administrador."""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return current_user


def require_agent_or_admin(current_user: dict = Depends(get_current_user)):
    """Dependencia que requiere rol de agente o administrador."""
    if current_user.get("rol") not in ("admin", "agent"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de agente o administrador",
        )
    return current_user
