import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User, UserUpdate } from '../models';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UsuariosService {
  private apiUrl = `${environment.apiUrl}/usuarios`;

  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los usuarios
   */
  getUsuarios(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  /**
   * Obtener usuario por ID
   */
  getUsuario(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  /**
   * Obtener perfil del usuario actual
   */
  getPerfil(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/perfil/me`);
  }

  /**
   * Actualizar usuario
   */
  updateUsuario(id: string, usuario: Partial<User>): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${id}`, usuario);
  }

  /**
   * Eliminar usuario
   */
  deleteUsuario(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
