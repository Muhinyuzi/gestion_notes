import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

// ---------------- TYPES ----------------

export interface Utilisateur {
  id?: number;
  nom: string;
  email: string;
  mot_de_passe: string;
  equipe: string;
  type?: string;
}

export interface UtilisateurDetailOut extends Utilisateur {
  id: number;
  date?: string;
  notes: Note[];
  commentaires: Commentaire[];
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
export class ApiService {
  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) {}

  // ---------------- UTILISATEURS ----------------
  getUtilisateurs(): Observable<Utilisateur[]> {
    return this.http.get<Utilisateur[]>(`${this.baseUrl}utilisateurs/`);
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

  // ---------------- NOTES ----------------
  getNotes(
    search?: string,
    author?: string,
    sort: 'date_asc' | 'date_desc' = 'date_desc',
    page: number = 1,
    limit: number = 10
  ): Observable<NotesResponse> {
    let params = new HttpParams()
      .set('sort', sort)
      .set('page', page.toString())
      .set('limit', limit.toString());

    if (search) params = params.set('search', search);
    if (author) params = params.set('author', author);

    // 🔹 Le backend filtre automatiquement par équipe ou admin
    return this.http.get<NotesResponse>(`${this.baseUrl}notes/`, { params });
  }

  getNoteById(id: number): Observable<Note> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.get<Note>(`${this.baseUrl}notes/${id}/`);
  }

  createNote(note: NoteCreate): Observable<Note> {
    return this.http.post<Note>(`${this.baseUrl}notes/`, note);
  }

  updateNote(id: number, note: Partial<Note>): Observable<Note> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.put<Note>(`${this.baseUrl}notes/${id}/`, note);
  }

  deleteNote(id: number): Observable<void> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.delete<void>(`${this.baseUrl}notes/${id}/`);
  }

  // ---------------- COMMENTAIRES ----------------
  getCommentaires(noteId: number): Observable<Commentaire[]> {
    if (noteId == null) throw new Error('ID note manquant pour récupérer les commentaires');
    return this.http.get<Commentaire[]>(`${this.baseUrl}notes/${noteId}/commentaires/`);
  }

  createCommentaire(noteId: number, commentaire: Commentaire): Observable<Commentaire> {
    if (noteId == null) throw new Error('ID note manquant pour créer un commentaire');
    return this.http.post<Commentaire>(`${this.baseUrl}notes/${noteId}/commentaires/`, commentaire);
  }
}
