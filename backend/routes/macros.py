from datetime import datetime, timezone
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from backend.database import get_database
from backend.dependencies import get_current_user
from backend.models.schemas import Macro, MacroCreate

router = APIRouter(prefix="/api/macros", tags=["macros"])

def _serialize_macro(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/", response_model=List[Macro])
async def get_macros(db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener macros (solo agentes/admin)"""
    if current_user.get("rol") not in ["admin", "agent"]:
        raise HTTPException(status_code=403, detail="Sin permisos")
    macros = await db.macros.find().sort("fecha_creacion", -1).to_list(None)
    return [_serialize_macro(m) for m in macros]

@router.post("/", response_model=Macro)
async def create_macro(macro_data: MacroCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Crear macro (solo admin)"""
    if current_user.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede crear macros")

    now = datetime.now(timezone.utc)
    doc = macro_data.model_dump()
    doc["autor_id"] = current_user.get("id")
    doc["fecha_creacion"] = now

    result = await db.macros.insert_one(doc)
    created = await db.macros.find_one({"_id": result.inserted_id})
    return _serialize_macro(created)

@router.delete("/{macro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_macro(macro_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Eliminar macro (solo admin)"""
    if current_user.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede eliminar")
        
    result = await db.macros.delete_one({"_id": ObjectId(macro_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
