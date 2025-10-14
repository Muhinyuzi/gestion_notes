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
export class NoteService {
  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) {}


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

    return this.http.get<NotesResponse>(`${this.baseUrl}notes/`, { params });
  }

  getNoteById(id: number): Observable<Note> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.get<Note>(`${this.baseUrl}notes/${id}/`);
  }

  createNote(note: NoteCreate): Observable<Note> {
    return this.http.post<Note>(`${this.baseUrl}notes/`, note);
  }

  createNoteWithFiles(note: NoteCreate, files: File[]): Observable<Note> {
    const formData = new FormData();
    formData.append('titre', note.titre);
    formData.append('contenu', note.contenu);
    formData.append('auteur_id', note.auteur_id.toString());
    if (note.equipe) formData.append('equipe', note.equipe);

    files.forEach(file => formData.append('fichiers', file));

    return this.http.post<Note>(`${this.baseUrl}notes/`, formData);
  }

  updateNote(id: number, note: Partial<Note>): Observable<Note> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.put<Note>(`${this.baseUrl}notes/${id}/`, note);
  }

  deleteNote(id: number): Observable<void> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.delete<void>(`${this.baseUrl}notes/${id}/`);
  }
}
