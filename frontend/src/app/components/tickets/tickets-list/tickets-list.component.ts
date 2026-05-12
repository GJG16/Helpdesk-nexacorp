import { Component, ChangeDetectorRef, NgZone, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TicketService } from '../../../services/ticket.service';
import { Ticket } from '../../../models';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-tickets-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './tickets-list.component.html',
  styleUrls: ['./tickets-list.component.css']
})
export class TicketsListComponent implements OnInit {
  tickets: Ticket[] = [];
  filteredTickets: Ticket[] = [];
  loading = true;
  filterEstado = '';
  filterPrioridad = '';
  searchTerm = '';
  currentPage = 1;
  pageSize = 8;
  totalTickets = 0;
  totalPages = 1;

  constructor(
    private ticketService: TicketService,
    private authService: AuthService,
    private router: Router,
    private ngZone: NgZone,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadTickets();
  }

  async loadTickets(page: number = this.currentPage): Promise<void> {
    this.loading = true;
    this.currentPage = page;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/tickets/paginated?page=${page}&page_size=${this.pageSize}`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const normalizedTickets = Array.isArray(data)
        ? data
        : Array.isArray(data?.items)
          ? data.items
          : [];

      this.ngZone.run(() => {
        this.tickets = normalizedTickets;
        this.totalTickets = Array.isArray(data) ? normalizedTickets.length : data.total ?? normalizedTickets.length;
        this.currentPage = Array.isArray(data) ? page : data.page;
        this.pageSize = Array.isArray(data) ? this.pageSize : data.page_size;
        this.totalPages = Array.isArray(data)
          ? Math.max(1, Math.ceil(this.totalTickets / this.pageSize))
          : data.total_pages;
        this.applyFilters();
        this.changeDetectorRef.detectChanges();
      });
    } catch (error) {
      console.error('Error inesperado al cargar tickets:', error);
      this.ngZone.run(() => {
        this.tickets = [];
        this.filteredTickets = [];
        this.totalTickets = 0;
        this.totalPages = 1;
        this.changeDetectorRef.detectChanges();
      });
    } finally {
      this.ngZone.run(() => {
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      });
    }
  }

  applyFilters(): void {
    this.filteredTickets = this.tickets.filter(ticket => {
      const matchEstado = !this.filterEstado || ticket.estado === this.filterEstado;
      const matchPrioridad = !this.filterPrioridad || ticket.prioridad === this.filterPrioridad;
      const matchSearch = !this.searchTerm || 
        ticket.titulo.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      return matchEstado && matchPrioridad && matchSearch;
    });
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }

    this.loadTickets(page);
  }

  getPageNumbers(): number[] {
    const total = this.totalPages;
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(total, start + 4);
    const pages: number[] = [];

    for (let page = start; page <= end; page++) {
      pages.push(page);
    }

    return pages;
  }

  deleteTicket(id: string | undefined): void {
    if (!id) return;
    if (confirm('¿Estás seguro de que deseas eliminar este ticket?')) {
      this.ticketService.deleteTicket(id).subscribe({
        next: () => {
          this.loadTickets();
        },
        error: () => {
          alert('Error al eliminar el ticket');
        }
      });
    }
  }

  editTicket(id: string | undefined): void {
    if (id) {
      this.router.navigate(['/tickets', id, 'edit']);
    }
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
}
