import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent) 
  },
  { 
    path: 'dashboard', 
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent), 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'tickets', 
    loadComponent: () => import('./components/tickets/tickets-list/tickets-list.component').then(m => m.TicketsListComponent), 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'tickets/kanban', 
    loadComponent: () => import('./components/tickets/kanban/kanban.component').then(m => m.KanbanComponent), 
    canActivate: [AuthGuard], 
    data: { roles: ['admin', 'agent'] } 
  },
  { 
    path: 'tickets/new', 
    loadComponent: () => import('./components/tickets/ticket-form/ticket-form.component').then(m => m.TicketFormComponent), 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'tickets/:id/edit', 
    loadComponent: () => import('./components/tickets/ticket-form/ticket-form.component').then(m => m.TicketFormComponent), 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'reports', 
    loadComponent: () => import('./components/reports/reports.component').then(m => m.ReportsComponent), 
    canActivate: [AuthGuard], 
    data: { role: 'admin' } 
  },
  { path: '**', redirectTo: 'login' }
];
