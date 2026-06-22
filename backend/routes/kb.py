from datetime import datetime, timezone
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.database import get_database
from backend.dependencies import get_current_user
from backend.models.schemas import KBArticle, KBArticleCreate

router = APIRouter(prefix="/api/kb", tags=["knowledge_base"])

def _serialize_kb(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/", response_model=List[KBArticle])
async def get_articles(db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener todos los artículos de KB"""
    articles = await db.kb.find().sort("fecha_creacion", -1).to_list(None)
    return [_serialize_kb(a) for a in articles]

@router.get("/{article_id}", response_model=KBArticle)
async def get_article(article_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Obtener un artículo y sumar vista"""
    article = await db.kb.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
        
    await db.kb.update_one({"_id": ObjectId(article_id)}, {"$inc": {"vistas": 1}})
    article["vistas"] += 1
    return _serialize_kb(article)

@router.post("/", response_model=KBArticle)
async def create_article(article_data: KBArticleCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Crear artículo de KB (solo admin/agent)"""
    if current_user.get("rol") not in ["admin", "agent"]:
        raise HTTPException(status_code=403, detail="No tienes permisos")

    now = datetime.now(timezone.utc)
    doc = article_data.model_dump()
    doc["autor_id"] = current_user.get("id")
    doc["vistas"] = 0
    doc["fecha_creacion"] = now
    doc["fecha_actualizacion"] = now

    result = await db.kb.insert_one(doc)
    created = await db.kb.find_one({"_id": result.inserted_id})
    return _serialize_kb(created)

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    """Eliminar artículo (solo admin)"""
    if current_user.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede eliminar")
        
    result = await db.kb.delete_one({"_id": ObjectId(article_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
