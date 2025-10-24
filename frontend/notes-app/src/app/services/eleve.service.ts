import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

// ---------------- TYPES ----------------

export interface Eleve {
  id?: number;
  nom: string;
  prenom: string;
  adresse?: string;
  en_attente?: boolean;
  actif?: boolean;
  ferme?: boolean;
  note_id?: number | null;
  created_by?: number;
  updated_by?: number;
  created_at?: string;
  updated_at?: string;
}

export interface EleveHistory {
  id?: number;
  eleve_id: number;
  edited_by: number;
  edited_at?: string;
  raison_changement?: string;
  changes: Record<string, { old: string | null; new: string | null }>;
}

export interface ElevesResponse {
  total?: number;
  page?: number;
  limit?: number;
  eleves: Eleve[];
}

// ---------------- SERVICE ----------------

@Injectable({
  providedIn: 'root'
})
export class EleveService {
  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) {}

  getBaseUrl(): string {
    return this.baseUrl;
  }

  // ---------------- ÉLÈVES ----------------

  /** Liste paginée et filtrée des élèves */
  getEleves(
  search?: string,
  actif?: boolean,
  en_attente?: boolean,
  page: number = 1,
  limit: number = 10
): Observable<Eleve[]> {
  let params = new HttpParams()
    .set('page', page.toString())
    .set('limit', limit.toString());

  if (search) params = params.set('search', search);
  if (actif !== undefined) params = params.set('actif', actif.toString());
  if (en_attente !== undefined) params = params.set('en_attente', en_attente.toString());

  return this.http.get<Eleve[]>(`${this.baseUrl}eleves/`, { params });
}

  /** Récupère un élève par ID */
  getEleveById(id: number): Observable<Eleve> {
    if (id == null) throw new Error('ID élève manquant');
    return this.http.get<Eleve>(`${this.baseUrl}eleves/${id}/`);
  }

  /** Crée un élève */
  createEleve(eleve: Eleve): Observable<Eleve> {
    return this.http.post<Eleve>(`${this.baseUrl}eleves/`, eleve);
  }

  /** Met à jour un élève */
  updateEleve(id: number, eleve: Partial<Eleve>): Observable<Eleve> {
    if (id == null) throw new Error('ID élève manquant');
    return this.http.put<Eleve>(`${this.baseUrl}eleves/${id}/`, eleve);
  }

  /** Supprime un élève */
  deleteEleve(id: number): Observable<void> {
    if (id == null) throw new Error('ID élève manquant');
    return this.http.delete<void>(`${this.baseUrl}eleves/${id}/`);
  }

  // ---------------- ASSIGNATION NOTE ----------------

  /** Assigner une note à un élève */
  assignNoteToEleve(eleveId: number, noteId: number): Observable<Eleve> {
    if (eleveId == null || noteId == null)
      throw new Error('Élève ou note manquant');
    return this.http.put<Eleve>(`${this.baseUrl}eleves/${eleveId}/assign_note`, { note_id: noteId });
  }

  /** Désassigner une note d’un élève */
  unassignNoteFromEleve(eleveId: number): Observable<Eleve> {
    if (eleveId == null) throw new Error('ID élève manquant');
    return this.http.put<Eleve>(`${this.baseUrl}eleves/${eleveId}/unassign_note`, {});
  }

  // ---------------- HISTORIQUE ----------------

  /** Récupère l’historique des modifications d’un élève */
  getEleveHistory(eleveId: number): Observable<EleveHistory[]> {
    if (eleveId == null) throw new Error('ID élève manquant');
    return this.http.get<EleveHistory[]>(`${this.baseUrl}eleves/${eleveId}/history`);
  }
}
