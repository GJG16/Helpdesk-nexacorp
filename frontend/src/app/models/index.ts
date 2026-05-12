export interface User {
  id?: string;
  nombre: string;
  email: string;
  rol: 'admin' | 'agent' | 'user';
  fecha_creacion?: Date;
}

export interface Ticket {
  id?: string;
  titulo: string;
  descripcion: string;
  estado: 'abierto' | 'en_progreso' | 'resuelto' | 'cerrado';
  usuario_id: string;
  fecha_creacion?: Date;
  fecha_actualizacion?: Date;
}

export interface TicketFilter {
  estado?: string;
  usuario_id?: string;
  fecha_desde?: Date;
  fecha_hasta?: Date;
}
