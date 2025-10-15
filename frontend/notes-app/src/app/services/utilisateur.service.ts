

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

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
}

export interface UtilisateurDetailOut extends Utilisateur {
  id: number;
  date?: string;
  avatar_url: string;
  notes: Note[];
  commentaires: Commentaire[];
}

export interface UtilisateursResponse {
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
  getUtilisateurs(page: number = 1, limit: number = 10): Observable<UtilisateursResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    return this.http.get<UtilisateursResponse>(`${this.baseUrl}utilisateurs/`, { params });
  }

  createUtilisateur(user: Utilisateur): Observable<Utilisateur> {
    return this.http.post<Utilisateur>(`${this.baseUrl}utilisateurs/`, user);
  }

  getUtilisateurDetail(id: number): Observable<UtilisateurDetailOut> {
    if (id == null) throw new Error('ID utilisateur manquant');
    return this.http.get<UtilisateurDetailOut>(`${this.baseUrl}utilisateurs/${id}/`);
  }

  updateUtilisateur(userId: number, userData: Partial<Utilisateur>): Observable<Utilisateur> {
    if (userId == null) throw new Error('ID utilisateur manquant');
    return this.http.put<Utilisateur>(`${this.baseUrl}utilisateurs/${userId}/`, userData);
  }

  deleteUtilisateur(userId: number): Observable<void> {
    if (userId == null) throw new Error('ID utilisateur manquant');
    return this.http.delete<void>(`${this.baseUrl}utilisateurs/${userId}/`);
  }

  uploadAvatar(userId: number, formData: FormData) {
  return this.http.post(`${this.baseUrl}utilisateurs/${userId}/avatar`, formData);
}
getAvatar(userId: number): Observable<Blob> {
  if (userId == null) throw new Error('ID utilisateur manquant');
  return this.http.get(`${this.baseUrl}utilisateurs/${userId}/avatar`, { responseType: 'blob' });
}

// URL de fallback par défaut côté backend
getDefaultAvatarUrl() {
  return `${this.baseUrl}avatars/default`;
}


}
