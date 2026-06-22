import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

export interface AppNotification {
  id: number;
  type: string;
  message: string;
  ticket_id?: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private socket: WebSocket | null = null;
  private notificationSubject = new Subject<AppNotification>();
  public notifications$ = this.notificationSubject.asObservable();
  
  private counter = 0;

  constructor(private authService: AuthService) {
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.connect();
      } else {
        this.disconnect();
      }
    });
  }

  private connect(): void {
    if (this.socket) {
      this.socket.close();
    }
    
    const token = this.authService.getToken();
    if (!token) return;

    const wsUrl = environment.apiUrl.replace('http://', 'ws://').replace('https://', 'wss://') + `/ws?token=${token}`;
    
    this.socket = new WebSocket(wsUrl);

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.notificationSubject.next({
          id: ++this.counter,
          type: data.type,
          message: data.message,
          ticket_id: data.ticket_id
        });
      } catch (e) {
        console.error('Error parsing notification', e);
      }
    };

    this.socket.onclose = () => {
      // Intentar reconectar después de 5 segundos si sigue logueado
      setTimeout(() => {
        if (this.authService.isAuthenticated()) {
          this.connect();
        }
      }, 5000);
    };
  }

  private disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
