import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface KBArticle {
  id?: string;
  titulo: string;
  contenido: string;
  categoria: string;
  vistas?: number;
  fecha_creacion?: Date;
  fecha_actualizacion?: Date;
}

@Injectable({
  providedIn: 'root'
})
export class KbService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getArticles(): Observable<KBArticle[]> {
    return this.http.get<KBArticle[]>(`${this.apiUrl}/kb/`);
  }

  getArticle(id: string): Observable<KBArticle> {
    return this.http.get<KBArticle>(`${this.apiUrl}/kb/${id}`);
  }

  createArticle(article: Partial<KBArticle>): Observable<KBArticle> {
    return this.http.post<KBArticle>(`${this.apiUrl}/kb/`, article);
  }

  deleteArticle(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/kb/${id}`);
  }
}
