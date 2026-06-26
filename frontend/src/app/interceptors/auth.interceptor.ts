import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError, from } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.authService.getToken();



    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });

    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Evitar intentar refresh sobre la propia ruta de refresh o si ya se intentó
          const isRefreshCall = request.url.includes('/api/auth/refresh');
          const alreadyAttempted = request.headers.has('x-refresh-attempted');


          if (isRefreshCall || alreadyAttempted) {
            this.authService.logout();
            this.router.navigate(['/login']);
            return throwError(() => error);
          }

          // Intentar refresh del token y reintentar la petición una sola vez
          return this.authService.refreshToken().pipe(
            switchMap(() => {
              const newToken = this.authService.getToken();
              if (newToken) {
                const reqWithNewToken = request.clone({
                  setHeaders: { Authorization: `Bearer ${newToken}`, 'x-refresh-attempted': '1' }
                });
                return next.handle(reqWithNewToken);
              }
              // Si no hay token luego del refresh, forzar logout
              this.authService.logout();
              this.router.navigate(['/login']);
              return throwError(() => error);
            }),
            catchError(() => {
              // Refresh falló
              this.authService.logout();
              this.router.navigate(['/login']);
              return throwError(() => error);
            })
          );
        } else if (error.status === 403) {
          // Sin permisos
          this.router.navigate(['/dashboard']);
        }
        return throwError(() => error);
      })
    );
  }
}
