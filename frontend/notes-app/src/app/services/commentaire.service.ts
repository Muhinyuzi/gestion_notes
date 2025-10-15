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
export class CommentaireService {
  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) {}

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

