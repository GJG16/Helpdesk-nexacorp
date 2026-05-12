from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"

class UserBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    rol: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    rol: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)

class UserInDB(UserBase):
    password_hash: str
    activo: bool = True
    fecha_creacion: Optional[datetime] = None

class User(UserBase):
    id: Optional[str] = None
    activo: bool = True
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User

class Priority(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class TicketStatus(str, Enum):
    ABIERTO = "abierto"
    EN_PROGRESO = "en_progreso"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"

class TicketBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field(..., min_length=10)
    estado: TicketStatus = TicketStatus.ABIERTO
    prioridad: Priority = Priority.MEDIA
    asignado_a: Optional[str] = None

class TicketCreate(TicketBase):
    usuario_id: str

class TicketUpdate(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=5, max_length=200)
    descripcion: Optional[str] = Field(default=None, min_length=10)
    estado: Optional[TicketStatus] = None
    prioridad: Optional[Priority] = None
    asignado_a: Optional[str] = None

class TicketFilter(BaseModel):
    estado: Optional[TicketStatus] = None
    prioridad: Optional[Priority] = None
    usuario_id: Optional[str] = None
    asignado_a: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None

class Ticket(TicketBase):
    id: Optional[str] = None
    usuario_id: str
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    fecha_resolucion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TicketStats(BaseModel):
    total: int
    abiertos: int
    en_progreso: int
    resueltos: int
    cerrados: int


class TicketPageResponse(BaseModel):
    items: List[Ticket]
    total: int
    page: int
    page_size: int
    total_pages: int
