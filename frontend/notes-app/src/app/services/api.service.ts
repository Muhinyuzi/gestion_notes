import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interfaces pour typer les données
export interface Utilisateur {
  id?: number;
  nom: string;
  email: string;
  mot_de_passe: string;
  equipe: string;
}

export interface UtilisateurDetailOut extends Utilisateur {
   id: number;  // obligatoire
  date: string;
  notes: Note[];
  commentaires: Commentaire[];
}

/*export interface Note {
  id?: number;
  titre: string;
  contenu: string;
  equipe: string;
  auteur_id: number;
}
*/

// ----------- Interfaces -----------

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
  date: string;
  auteur?: {
    id: number;
    nom: string;
    email: string;
    equipe?: string;
  };
  commentaires: Commentaire[];
}

export interface Commentaire {
  id?: number;
  contenu: string;
  auteur_id: number;
  note_id: number;
  date?: string;
    // relation facultative
  auteur?: Utilisateur;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:8000'; // ton backend FastAPI

  constructor(private http: HttpClient) {}

  // ---------------- UTILISATEURS ----------------
  getUtilisateurs(): Observable<Utilisateur[]> {
    return this.http.get<Utilisateur[]>(`${this.baseUrl}/utilisateurs`);
  }

  createUtilisateur(user: Utilisateur): Observable<Utilisateur> {
    return this.http.post<Utilisateur>(`${this.baseUrl}/utilisateurs`, user);
  }

  getUtilisateurDetail(id: number): Observable<UtilisateurDetailOut> {
    return this.http.get<UtilisateurDetailOut>(`${this.baseUrl}/utilisateurs/${id}`);
  }

     // api.service.ts
   // ---------------- UTILISATEURS ----------------

  updateUtilisateur(userId: number, userData: any): Observable<Utilisateur> {
    return this.http.put<Utilisateur>(`${this.baseUrl}/utilisateurs/${userId}`, userData);
  }

  deleteUtilisateur(userId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/utilisateurs/${userId}`);
  }


  // ---------------- NOTES ----------------
  getNotes(): Observable<Note[]> {
    return this.http.get<Note[]>(`${this.baseUrl}/notes`);
  }
  getNoteById(id: number): Observable<Note> {
  return this.http.get<Note>(`${this.baseUrl}/notes/${id}`);
  }

   // Créer une nouvelle note
  createNote(note: NoteCreate): Observable<Note> {
    return this.http.post<Note>(`${this.baseUrl}/notes`, note);
  }

  // ✏️ Mettre à jour une note
updateNote(id: number, note: Partial<Note>): Observable<Note> {
  return this.http.put<Note>(`${this.baseUrl}/notes/${id}`, note);
}

deleteNote(id: number): Observable<void> {
  return this.http.delete<void>(`${this.baseUrl}/notes/${id}`);
}

  // ---------------- COMMENTAIRES ----------------

   // Récupérer les commentaires d'une note
getCommentaires(noteId: number): Observable<Commentaire[]> {
  return this.http.get<Commentaire[]>(`${this.baseUrl}/notes/${noteId}/commentaires`);
}

// Créer un commentaire
createCommentaire(noteId: number, commentaire: Commentaire): Observable<Commentaire> {
  return this.http.post<Commentaire>(`${this.baseUrl}/notes/${noteId}/commentaires`, commentaire);
}
}
