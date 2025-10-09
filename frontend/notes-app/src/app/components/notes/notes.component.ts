import { Component, OnInit } from '@angular/core';
import { ApiService, Note, NoteCreate, NotesResponse } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-notes',
  templateUrl: './notes.component.html',
  styleUrls: ['./notes.component.css']
})
export class NotesComponent implements OnInit {
  notes: Note[] = [];
  newNote: NoteCreate = { titre: '', contenu: '', equipe: '', auteur_id: 0 };

  // Pagination
  page: number = 1;
  limit: number = 10;
  total: number = 0;

  // Filtres / tri
  searchTerm: string = '';
  selectedAuteur: string = '';
  sort: 'date_asc' | 'date_desc' = 'date_desc';

  // Utilisateur connecté
  currentUser: any;

  constructor(private api: ApiService, private auth: AuthService) {}

  ngOnInit(): void {
    this.currentUser = this.auth.getUser();
    if (this.currentUser) {
      this.newNote.auteur_id = this.currentUser.id;
      this.newNote.equipe = this.currentUser.equipe;
    }
    this.loadNotes();
  }

  // ---------------- CHARGER LES NOTES ----------------
  loadNotes(): void {
    let authorFilter = this.selectedAuteur;
    // Si l'utilisateur n'est pas admin, on filtre automatiquement par son équipe
    if (this.currentUser?.type !== 'admin') {
      authorFilter = ''; // pas de filtre auteur, backend filtre par équipe
    }

    this.api.getNotes(this.searchTerm, authorFilter, this.sort, this.page, this.limit).subscribe({
      next: (res: NotesResponse) => {
        this.notes = res.notes ?? [];
        this.total = res.total ?? this.notes.length;
      },
      error: (err: any) => {
        console.error('Erreur lors du chargement des notes', err);
        this.notes = [];
        this.total = 0;
      }
    });
  }

  // ---------------- AJOUTER UNE NOTE ----------------
  addNote(): void {
    if (!this.newNote.titre || !this.newNote.contenu) {
      alert('Veuillez entrer un titre et un contenu.');
      return;
    }

    this.api.createNote(this.newNote).subscribe({
      next: (note: Note) => {
        this.notes.unshift(note);
        this.total += 1;
        this.newNote.titre = '';
        this.newNote.contenu = '';
      },
      error: (err: any) => {
        console.error('Erreur lors de l’ajout de la note', err);
      }
    });
  }

  // ---------------- PAGINATION ----------------
  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.page = page;
    this.loadNotes();
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.limit);
  }

  // ---------------- FILTRES / TRI ----------------
  applyFilters(): void {
    this.page = 1;
    this.loadNotes();
  }

  changeSort(sort: 'date_asc' | 'date_desc'): void {
    this.sort = sort;
    this.loadNotes();
  }
}
