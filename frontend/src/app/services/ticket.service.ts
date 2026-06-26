import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuditLog, Ticket, TicketFilter, TicketReport, TicketComment } from '../models';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TicketService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los tickets
   */
  getTickets(): Observable<{items: Ticket[], total: number, page: number, pages: number}> {
    return this.http.get<{items: Ticket[], total: number, page: number, pages: number}>(`${this.apiUrl}/tickets/`);
  }

  /**
   * Obtener métricas rápidas de tickets
   */
  getTicketStats(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/tickets/stats`);
  }

  /**
   * Obtener un ticket por ID
   */
  getTicket(id: string): Observable<Ticket> {
    return this.http.get<Ticket>(`${this.apiUrl}/tickets/${id}`);
  }

  /**
   * Crear un nuevo ticket
   */
  createTicket(ticket: Omit<Ticket, 'id' | 'fecha_creacion'>): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.apiUrl}/tickets/`, ticket);
  }

  /**
   * Actualizar un ticket
   */
  updateTicket(id: string, ticket: Partial<Ticket>): Observable<Ticket> {
    return this.http.put<Ticket>(`${this.apiUrl}/tickets/${id}`, ticket);
  }

  /**
   * Eliminar un ticket
   */
  deleteTicket(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/tickets/${id}`);
  }

  /**
   * Filtrar tickets
   */
  filterTickets(filter: TicketFilter): Observable<{items: Ticket[], total: number, page: number, pages: number}> {
    return this.http.post<{items: Ticket[], total: number, page: number, pages: number}>(`${this.apiUrl}/tickets/filter`, filter);
  }

  /**
   * Obtener reporte administrativo de tickets
   */
  getTicketReports(): Observable<TicketReport> {
    return this.http.get<TicketReport>(`${this.apiUrl}/reports/tickets`);
  }

  /**
   * Obtener feed reciente de auditoría
   */
  getAuditLogs(limit = 10): Observable<AuditLog[]> {
    return this.http.get<AuditLog[]>(`${this.apiUrl}/reports/audit?limit=${limit}`);
  }

  /**
   * Obtener estado del servidor
   */
  getStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/status`);
  }

  /**
   * Obtener comentarios de un ticket
   */
  getComments(ticketId: string): Observable<TicketComment[]> {
    return this.http.get<TicketComment[]>(`${this.apiUrl}/tickets/${ticketId}/comments`);
  }

  /**
   * Agregar un comentario a un ticket
   */
  addComment(ticketId: string, texto: string): Observable<TicketComment> {
    return this.http.post<TicketComment>(`${this.apiUrl}/tickets/${ticketId}/comments`, { texto });
  }
  /**
   * Subir adjunto a un ticket
   */
  uploadAttachment(ticketId: string, file: File): Observable<{filename: string, url: string}> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{filename: string, url: string}>(`${this.apiUrl}/tickets/${ticketId}/adjuntos`, formData);
  }
}
