// src/app/services/utilisateur.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';

// ---------------- TYPES ----------------

export interface Utilisateur {
  id?: number;
  nom: string;
  email: string;
  mot_de_passe?: string;
  equipe?: string;
  type?: string;
  poste?: string;
  telephone?: string;
  adresse?: string;
  date_embauche?: string;
  is_active?: boolean;
  avatar_url?: string;
}

export interface UtilisateurDetailOut extends Utilisateur {
  date?: string;
  notes?: Note[];
  commentaires?: Commentaire[];
}

export interface PaginatedUsers {
  total: number;
  page: number;
  limit: number;
  users: Utilisateur[];
}

// Pour créer une note
export interface NoteCreate {
  titre: string;
  contenu: string;
  equipe?: string;
  auteur_id: number;
}

// Pour lire une note
export interface Note {
  id: number;
  titre: string;
  contenu: string;
  equipe?: string;
  created_at: string;
  updated_at?: string;
  auteur_id: number;
  auteur?: Utilisateur;
  commentaires: Commentaire[];
  fichiers?: any[];
}

export interface NotesResponse {
  total?: number;
  page?: number;
  limit?: number;
  notes: Note[];
}

export interface Commentaire {
  id?: number;
  contenu: string;
  auteur_id: number;
  note_id: number;
  date?: string;
  auteur?: Utilisateur;
}

// ---------------- SERVICE ----------------

@Injectable({
  providedIn: 'root'
})
export class UtilisateurService {
  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) {}

  // ---------------- UTILISATEURS ----------------

  getUtilisateurs(page: number = 1, limit: number = 10): Observable<PaginatedUsers> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    // ✅ Le backend renvoie {"status": "success", "data": {...}}
    return this.http.get<{ status: string; data: PaginatedUsers }>(`${this.baseUrl}utilisateurs/`, { params })
      .pipe(map(res => res.data));
  }

  createUtilisateur(user: Utilisateur): Observable<Utilisateur> {
    return this.http.post<{ status: string; data: Utilisateur }>(`${this.baseUrl}utilisateurs/`, user)
      .pipe(map(res => res.data));
  }

  getUtilisateurDetail(id: number): Observable<UtilisateurDetailOut> {
    return this.http.get<{ status: string; data: UtilisateurDetailOut }>(`${this.baseUrl}utilisateurs/${id}`)
      .pipe(map(res => res.data));
  }

  updateUtilisateur(userId: number, userData: Partial<Utilisateur>): Observable<Utilisateur> {
    return this.http.put<{ status: string; data: Utilisateur }>(`${this.baseUrl}utilisateurs/${userId}`, userData)
      .pipe(map(res => res.data));
  }

  deleteUtilisateur(userId: number): Observable<string> {
    return this.http.delete<{ status: string; data: { message: string } }>(`${this.baseUrl}utilisateurs/${userId}`)
      .pipe(map(res => res.data.message));
  }

  // ---------------- AVATARS ----------------

  uploadAvatar(userId: number, formData: FormData) {
    return this.http.post<{ status: string; data: any }>(`${this.baseUrl}utilisateurs/${userId}/avatar`, formData)
      .pipe(map(res => res.data));
  }

  getAvatar(userId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}utilisateurs/${userId}/avatar`, { responseType: 'blob' });
  }

  // URL de fallback par défaut
  getDefaultAvatarUrl() {
    return `${this.baseUrl}avatars/default`;
  }
}
