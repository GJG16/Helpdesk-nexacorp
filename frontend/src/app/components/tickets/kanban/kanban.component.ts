import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AuthService } from '../../../services/auth.service';
import { TicketService } from '../../../services/ticket.service';
import { Ticket, User } from '../../../models';
import { TicketFormComponent } from '../ticket-form/ticket-form.component';
import { SkeletonComponent } from '../../ui/skeleton/skeleton';

interface KanbanColumn {
  key: Ticket['estado'];
  label: string;
  tickets: Ticket[];
}

@Component({
  selector: 'app-kanban',
  standalone: true,
  imports: [CommonModule, RouterModule, TicketFormComponent, SkeletonComponent],
  templateUrl: './kanban.component.html',
  styleUrls: ['./kanban.component.css']
})
export class KanbanComponent implements OnInit, OnDestroy {
  currentUser: User | null = null;
  loading = true;
  error = '';
  tickets: Ticket[] = [];
  columns: KanbanColumn[] = [
    { key: 'abierto', label: 'Pendiente', tickets: [] },
    { key: 'en_progreso', label: 'En Proceso', tickets: [] },
    { key: 'resuelto', label: 'Resuelto', tickets: [] },
    { key: 'cerrado', label: 'Cerrado', tickets: [] },
  ];
  editingTicketId: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private ticketService: TicketService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.currentUser = this.authService.getCurrentUser();
  }

  ngOnInit(): void {
    if (!this.authService.isAgent() && !this.authService.isAdmin()) {
      this.router.navigate(['/dashboard']);
      return;
    }

    this.loadTickets();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  trackById(index: number, ticket: Ticket): string {
    return ticket.id || '';
  }

  loadTickets(): void {
    this.loading = true;
    this.ticketService.getTickets().pipe(takeUntil(this.destroy$)).subscribe({
      next: (response: any) => {
        this.tickets = response.items;
        this.groupTickets();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'No fue posible cargar el tablero';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  groupTickets(): void {
    this.columns = this.columns.map((column) => ({
      ...column,
      tickets: this.tickets.filter((ticket) => ticket.estado === column.key),
    }));
  }

  dragStart(event: DragEvent, ticket: Ticket): void {
    // Protección adicional: evitar iniciar drag si no tiene permisos
    if (!this.canDrag(ticket)) {
      event.preventDefault();
      return;
    }
    event.dataTransfer?.setData('text/plain', ticket.id || '');
  }

  allowDrop(event: DragEvent): void {
    event.preventDefault();
  }

  drop(event: DragEvent, targetState: Ticket['estado']): void {
    event.preventDefault();
    const ticketId = event.dataTransfer?.getData('text/plain');
    if (!ticketId) {
      return;
    }

    const ticket = this.tickets.find((item) => item.id === ticketId);
    if (!ticket) {
      return;
    }

    this.moveTicket(ticket, targetState);
  }

  moveTicket(ticket: Ticket, targetState: Ticket['estado']): void {
    if (!ticket.id) {
      return;
    }

    if (this.authService.isAgent() && ticket.asignado_a !== this.currentUser?.id) {
      this.error = 'Primero debes asignarte el ticket antes de moverlo';
      return;
    }

    // Estado original para rollback
    const previousState = ticket.estado;
    
    // Actualización Optimista
    ticket.estado = targetState;
    this.groupTickets();
    this.cdr.detectChanges();

    const payload: Partial<Ticket> = { estado: targetState };

    this.ticketService.updateTicket(ticket.id, payload).subscribe({
      next: () => {
        // En caso de éxito, podríamos recargar para ver la fecha de actualización real
        // pero la UI ya respondió. Solo recargamos en background.
        this.loadTickets();
      },
      error: () => {
        // Rollback
        ticket.estado = previousState;
        this.groupTickets();
        this.cdr.detectChanges();
        this.error = 'No fue posible actualizar el ticket';
      }
    });
  }

  assignToMe(ticket: Ticket): void {
    if (!ticket.id || !this.currentUser?.id) {
      return;
    }

    // Estado original para rollback
    const previousAssignee = ticket.asignado_a;
    
    // Actualización optimista
    ticket.asignado_a = this.currentUser.id;
    this.cdr.detectChanges();

    this.ticketService.updateTicket(ticket.id, { asignado_a: this.currentUser.id }).subscribe({
      next: () => this.loadTickets(),
      error: () => {
        // Rollback
        ticket.asignado_a = previousAssignee;
        this.cdr.detectChanges();
        this.error = 'No fue posible asignar el ticket';
      }
    });
  }

  canDrag(ticket: Ticket): boolean {
    return this.authService.isAdmin() || ticket.asignado_a === this.currentUser?.id;
  }

  canSelfAssign(ticket: Ticket): boolean {
    return this.authService.isAgent() && ticket.asignado_a !== this.currentUser?.id;
  }



  viewTicket(id: string | undefined): void {
    if (id) {
      this.editingTicketId = id;
    }
  }

  closeEditModal(): void {
    this.editingTicketId = null;
    this.loadTickets();
  }

  getAssigneeLabel(ticket: Ticket): string {
    if (!ticket.asignado_a) {
      return 'Sin asignar';
    }

    if (ticket.asignado_a === this.currentUser?.id) {
      return 'Asignado a mí';
    }

    return `Asignado: ${ticket.asignado_a.substring(0, 6)}`;
  }

  getStateLabel(state: Ticket['estado']): string {
    const labels: Record<Ticket['estado'], string> = {
      abierto: 'Pendientes',
      en_progreso: 'En curso',
      resuelto: 'Resueltos',
      cerrado: 'Cerrados',
    };

    return labels[state];
  }

  getPriorityLabel(ticket: Ticket): string {
    const labels: Record<Ticket['prioridad'], string> = {
      baja: 'Baja prioridad',
      media: 'Prioridad media',
      alta: 'Alta prioridad',
      critica: 'Crítica',
    };

    return labels[ticket.prioridad];
  }

  stripHtml(html: string): string {
    if (!html) return '';
    return html.replace(/<[^>]*>?/gm, '');
  }

  isSlaBreached(ticket: Ticket): boolean {
    if (!ticket.fecha_vencimiento_sla || ticket.estado === 'resuelto' || ticket.estado === 'cerrado') {
      return false;
    }
    return new Date() > new Date(ticket.fecha_vencimiento_sla);
  }

  getSlaTimeRemaining(ticket: Ticket): string {
    if (!ticket.fecha_vencimiento_sla || ticket.estado === 'resuelto' || ticket.estado === 'cerrado') {
      return '-';
    }
    const diff = new Date(ticket.fecha_vencimiento_sla).getTime() - new Date().getTime();
    if (diff <= 0) return 'Vencido';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isAgent(): boolean {
    return this.authService.isAgent();
  }
}
