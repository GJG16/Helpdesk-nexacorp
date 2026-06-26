import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TicketService } from '../../services/ticket.service';
import { User, Ticket } from '../../models';

import { TicketCreateModalComponent } from '../tickets/ticket-create-modal/ticket-create-modal.component';
import { ButtonComponent } from '../ui/button/button';
import { SkeletonComponent } from '../ui/skeleton/skeleton';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, TicketCreateModalComponent, ButtonComponent, SkeletonComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  isModalOpen = false;
  currentUser: User | null = null;
  tickets: Ticket[] = [];
  loading = true;
  currentRole: User['rol'] | null = null;
  stats = {
    total: 0,
    abiertos: 0,
    en_progreso: 0,
    resueltos: 0,
    cerrados: 0
  };

  constructor(
    private authService: AuthService,
    private ticketService: TicketService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    // Esperar al observable de usuario en ngOnInit para asegurar token cargado
  }

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.currentRole = user?.rol ?? null;
      if (user) {
        this.loadDashboard();
      } else {
        this.tickets = [];
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  loadDashboard(): void {
    this.loading = true;
    
    // Fetch recent tickets
    this.ticketService.getTickets().subscribe({
      next: (response) => {
        this.tickets = response.items.slice(0, 5); // Últimos 5 tickets
        this.cdr.detectChanges();
      },
      error: (error) => console.error('Error al cargar tickets:', error)
    });

    // Fetch real stats
    this.ticketService.getTicketStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error al cargar stats:', error);
        this.loading = false;
        this.cdr.detectChanges();
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

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isAgent(): boolean {
    return this.authService.isAgent();
  }

  isUser(): boolean {
    return this.authService.isUser();
  }
}
