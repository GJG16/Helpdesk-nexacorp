import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TicketService } from '../../services/ticket.service';
import { User, Ticket, TicketStats, TicketPageResponse } from '../../models';
import { catchError } from 'rxjs/operators';
import { forkJoin, of } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  tickets: Ticket[] = [];
  loading = true;
  stats: TicketStats = {
    total: 0,
    abiertos: 0,
    en_progreso: 0,
    resueltos: 0,
    cerrados: 0
  };

  constructor(
    private authService: AuthService,
    private ticketService: TicketService,
    private router: Router
  ) {
    this.currentUser = this.authService.getCurrentUser();
  }

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    forkJoin({
      stats: this.ticketService.getTicketStats().pipe(
        catchError((error) => {
          console.error('Error al cargar estadísticas:', error);
          return of({ total: 0, abiertos: 0, en_progreso: 0, resueltos: 0, cerrados: 0 });
        })
      ),
      recent: this.ticketService.getTicketsPaginated(1, 5).pipe(
        catchError((error) => {
          console.error('Error al cargar tickets recientes:', error);
          return of({ items: [], total: 0, page: 1, page_size: 5, total_pages: 1 } as TicketPageResponse);
        })
      )
    }).subscribe({
      next: ({ stats, recent }) => {
        this.stats = stats;
        this.tickets = recent.items;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar dashboard:', error);
        this.loading = false;
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}
