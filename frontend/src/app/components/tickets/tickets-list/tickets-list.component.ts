import { ChangeDetectorRef, Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { TicketService } from '../../../services/ticket.service';
import { Ticket, TicketStatus, User } from '../../../models';
import { AuthService } from '../../../services/auth.service';
import { TicketCreateModalComponent } from '../ticket-create-modal/ticket-create-modal.component';
import { TicketFormComponent } from '../ticket-form/ticket-form.component';

@Component({
  selector: 'app-tickets-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, TicketCreateModalComponent, TicketFormComponent],
  templateUrl: './tickets-list.component.html',
  styleUrls: ['./tickets-list.component.css']
})
export class TicketsListComponent implements OnInit, OnDestroy {
  isModalOpen = false;
  tickets: Ticket[] = [];
  filteredTickets: Ticket[] = [];
  loading = true;
  filterEstado = '';
  filterPrioridad = '';
  filterTipo = '';
  searchTerm = '';
  currentUser: User | null = null;
  editingTicketId: string | null = null;
  
  private destroy$ = new Subject<void>();

  constructor(
    private ticketService: TicketService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    // No solicitar user síncronamente; escuchamos el observable en ngOnInit
  }

  ngOnInit(): void {
    this.authService.currentUser$.pipe(takeUntil(this.destroy$)).subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.loadTickets();
      } else {
        // Si no hay usuario, limpiar lista
        this.tickets = [];
        this.filteredTickets = [];
        this.loading = false;
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  trackById(index: number, ticket: Ticket): string {
    return ticket.id;
  }

  loadTickets(): void {
    this.loading = true;
    this.ticketService.getTickets().pipe(takeUntil(this.destroy$)).subscribe({
      next: (response) => {
        this.tickets = response.items;
        this.applyFilters();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error al cargar tickets:', error);
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    this.loading = true;
    const filterParams = {
      estado: this.filterEstado || undefined,
      prioridad: this.filterPrioridad || undefined,
      tipo: this.filterTipo || undefined,
      busqueda: this.searchTerm || undefined
    };

    this.ticketService.filterTickets(filterParams).subscribe({
      next: (response) => {
        this.filteredTickets = response.items;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (e) => {
        console.error('Error aplicando filtros:', e);
        this.filteredTickets = [];
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  deleteTicket(id: string | undefined): void {
    if (!id) return;
    if (confirm('¿Estás seguro de que deseas eliminar este ticket?')) {
      this.ticketService.deleteTicket(id).subscribe({
        next: () => {
          this.loadTickets();
        },
        error: (error) => {
          alert('Error al eliminar el ticket');
        }
      });
    }
  }

  assignToMe(ticket: Ticket): void {
    if (!ticket.id || !this.currentUser?.id) return;

    this.ticketService.updateTicket(ticket.id, { asignado_a: this.currentUser.id }).subscribe({
      next: () => this.loadTickets(),
      error: () => alert('No fue posible asignar el ticket')
    });
  }

  canEditTicket(ticket: Ticket): boolean {
    if (!this.currentUser) {
      return false;
    }

    if (this.authService.isAdmin()) {
      return true;
    }

    if (this.authService.isAgent()) {
      return ticket.asignado_a === this.currentUser.id;
    }

    return ticket.usuario_id === this.currentUser.id;
  }

  canDeleteTicket(ticket: Ticket): boolean {
    return this.authService.isAdmin();
  }

  canSelfAssign(ticket: Ticket): boolean {
    return !!this.currentUser && this.authService.isAgent() && ticket.asignado_a !== this.currentUser.id;
  }

  editTicket(id: string | undefined): void {
    if (id) {
      this.editingTicketId = id;
    }
  }

  closeEditModal(): void {
    this.editingTicketId = null;
    this.loadTickets(); // refresh list to see changes
  }

  createTicket(): void {
    this.router.navigate(['/tickets/new']);
  }

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isAgent(): boolean {
    return this.authService.isAgent();
  }

  isUser(): boolean {
    return this.authService.isUser();
  }

  isSlaBreached(ticket: Ticket): boolean {
    if (!ticket.fecha_vencimiento_sla || ticket.estado === 'resuelto' || ticket.estado === 'cerrado') {
      return false;
    }
    return new Date() > new Date(ticket.fecha_vencimiento_sla);
  }

  stripHtml(html: string): string {
    if (!html) return '';
    return html.replace(/<[^>]*>?/gm, '');
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

  goToKanban(): void {
    this.router.navigate(['/tickets/kanban']);
  }
}
