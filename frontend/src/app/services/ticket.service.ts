import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Ticket, TicketFilter, TicketStats, TicketPageResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class TicketService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los tickets
   */
  getTickets(): Observable<Ticket[]> {
    return this.http.get<Ticket[]>(`${this.apiUrl}/tickets`);
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
    return this.http.post<Ticket>(`${this.apiUrl}/tickets`, ticket);
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
  filterTickets(filter: TicketFilter): Observable<Ticket[]> {
    return this.http.post<Ticket[]>(`${this.apiUrl}/tickets/filter`, filter);
  }

  /**
   * Obtener estado del servidor
   */
  getStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/status`);
  }

  /**
   * Obtener estadísticas de tickets
   */
  getTicketStats(): Observable<TicketStats> {
    return this.http.get<TicketStats>(`${this.apiUrl}/tickets/stats`);
  }

  /**
   * Obtener tickets paginados
   */
  getTicketsPaginated(page: number = 1, pageSize: number = 10): Observable<TicketPageResponse> {
    return this.http.get<TicketPageResponse>(
      `${this.apiUrl}/tickets/paginated?page=${page}&page_size=${pageSize}`
    );
  }
}
