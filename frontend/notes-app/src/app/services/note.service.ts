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

// ---------- Fichier associé ----------
export interface FichierNote {
  id: number;
  nom_fichier: string;
  chemin: string;
}

// ---------- Commentaire ----------
export interface Commentaire {
  id?: number;
  contenu: string;
  auteur_id: number;
  note_id: number;
  date?: string;
  auteur?: Utilisateur;
}

// ---------- Note ----------
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
  fichiers?: FichierNote[];

  // Champs additionnels
  nb_vues?: number;
  likes?: number;
  resume_ia?: string;
  categorie?: string;
  priorite?: string;
}

export interface NoteCreate {
  titre: string;
  contenu: string;
  equipe?: string;
  auteur_id: number;
  priorite?: string;
  categorie?: string;
}

export interface NotesResponse {
  total?: number;
  page?: number;
  limit?: number;
  notes: Note[];
}

// ---------------- SERVICE ----------------

@Injectable({
  providedIn: 'root'
})
export class NoteService {

  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) {}

  getBaseUrl(): string {
    return this.baseUrl;
  }

  // ---------------- NOTES ----------------

  /** Liste paginée et filtrée des notes */
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

  /** Récupère une note par son ID */
  getNoteById(id: number): Observable<Note> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.get<Note>(`${this.baseUrl}notes/${id}/`);
  }

  /** Crée une note sans fichier (cas simple) */
  createNote(note: NoteCreate): Observable<Note> {
    return this.http.post<Note>(`${this.baseUrl}notes/`, note);
  }

  /** Crée une note avec fichiers, catégorie et priorité */
  createNoteWithFiles(note: NoteCreate, files: File[]): Observable<Note> {
    const formData = new FormData();
    formData.append('titre', note.titre);
    formData.append('contenu', note.contenu);
    formData.append('auteur_id', note.auteur_id.toString());
    if (note.equipe) formData.append('equipe', note.equipe);
    if (note.priorite) formData.append('priorite', note.priorite);
    if (note.categorie) formData.append('categorie', note.categorie);

    files.forEach(file => formData.append('fichiers', file));

    return this.http.post<Note>(`${this.baseUrl}notes/`, formData);
  }

  /** Met à jour une note */
  updateNote(id: number, note: Partial<Note>): Observable<Note> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.put<Note>(`${this.baseUrl}notes/${id}/`, note);
  }

  /** Met à jour une note avec fichiers, catégorie et priorité */
updateNoteWithFiles(id: number, note: NoteCreate, files: File[]): Observable<Note> {
  if (id == null) throw new Error('ID note manquant');
  
  const formData = new FormData();
  formData.append('titre', note.titre);
  formData.append('contenu', note.contenu);
  formData.append('auteur_id', note.auteur_id.toString());
  if (note.equipe) formData.append('equipe', note.equipe);
  if (note.priorite) formData.append('priorite', note.priorite);
  if (note.categorie) formData.append('categorie', note.categorie);

  files.forEach(file => formData.append('fichiers', file));

  return this.http.put<Note>(`${this.baseUrl}notes/${id}/`, formData);
}

  /** Supprime une note */
  deleteNote(id: number): Observable<void> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.delete<void>(`${this.baseUrl}notes/${id}/`);
  }

  /** Like une note */
  likeNote(id: number): Observable<{ likes: number }> {
    if (id == null) throw new Error('ID note manquant');
    return this.http.post<{ likes: number }>(`${this.baseUrl}notes/${id}/like`, {});
  }

  // ---------------- COMMENTAIRES ----------------

  getCommentaires(noteId: number): Observable<Commentaire[]> {
    if (noteId == null) throw new Error('ID note manquant');
    return this.http.get<Commentaire[]>(`${this.baseUrl}notes/${noteId}/commentaires`);
  }

  addCommentaire(noteId: number, commentaire: Commentaire): Observable<Commentaire> {
    if (noteId == null) throw new Error('ID note manquant');
    return this.http.post<Commentaire>(`${this.baseUrl}notes/${noteId}/commentaires`, commentaire);
  }

  // ---------------- Fichiers ----------------
  deleteFile(fileId: number): Observable<{ detail: string }> {
    if (fileId == null) throw new Error('ID fichier manquant');
    return this.http.delete<{ detail: string }>(`${this.baseUrl}notes/fichiers/${fileId}`);
  }

}
