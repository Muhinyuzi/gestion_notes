import { Component, OnInit } from '@angular/core';
import { ApiService, Note, NoteCreate, NotesResponse } from '../../services/api.service';

@Component({
  selector: 'app-notes',
  templateUrl: './notes.component.html',
  styleUrls: ['./notes.component.css']
})
export class NotesComponent implements OnInit {
  notes: Note[] = [];
  newNote: NoteCreate = { titre: '', contenu: '', equipe: '', auteur_id: 1 };

  // Pagination
  page: number = 1;
  limit: number = 10;
  total: number = 0;

  // Filtres / tri
  searchTerm: string = '';
  selectedAuteur: string = '';
  sort: string = 'date_desc';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadNotes();
  }

  // ---------------- CHARGER LES NOTES ----------------
  loadNotes(): void {
    this.api.getNotes().subscribe({
      next: (data: NotesResponse) => {
        let filtered: Note[] = data.notes;

        // ---------------- FILTRAGE ----------------
        if (this.searchTerm) {
          filtered = filtered.filter(n =>
            n.titre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
            n.contenu.toLowerCase().includes(this.searchTerm.toLowerCase())
          );
        }

        if (this.selectedAuteur) {
          filtered = filtered.filter(n =>
            n.auteur?.nom.toLowerCase().includes(this.selectedAuteur.toLowerCase())
          );
        }

        // ---------------- TRI ----------------
        // ---------------- TRI ----------------
  filtered.sort((a, b) => {
    const dateA = new Date(a.updated_at ?? a.created_at).getTime();
    const dateB = new Date(b.updated_at ?? b.created_at).getTime();
    return this.sort === 'date_asc' ? dateA - dateB : dateB - dateA;
  });

        // ---------------- PAGINATION ----------------
        this.total = filtered.length;
        const start = (this.page - 1) * this.limit;
        const end = start + this.limit;
        this.notes = filtered.slice(start, end);
      },
      error: (err: any) => {
        console.error('Erreur lors du chargement des notes', err);
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
        this.notes.unshift(note); // Ajouter en haut
        this.newNote = { titre: '', contenu: '', equipe: '', auteur_id: 1 };
        this.total += 1;
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
    this.page = 1; // Reset page
    this.loadNotes();
  }

  changeSort(sort: string): void {
    this.sort = sort;
    this.loadNotes();
  }
}
