import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { NoteService, Note, NoteCreate, NotesResponse } from '../../services/note.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-notes',
  templateUrl: './notes.component.html',
  styleUrls: ['./notes.component.css']
})
export class NotesComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  notes: Note[] = [];
  newNote: NoteCreate = { 
  titre: '', 
  contenu: '', 
  equipe: '', 
  auteur_id: 0, 
  categorie: '', 
  priorite: '' 
}
  newFiles: File[] = [];

  page: number = 1;
  limit: number = 10;
  total: number = 0;

  searchTerm: string = '';
  selectedAuteur: string = '';
  sort: 'date_asc' | 'date_desc' = 'date_desc';

  currentUser: any = null;

  constructor(private api: NoteService, private auth: AuthService, private router: Router) {}

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
    this.api.getNotes(this.searchTerm, this.selectedAuteur, this.sort, this.page, this.limit)
      .subscribe({
        next: (res: NotesResponse) => {
          // ✅ backend gère déjà pagination et filtrage
          this.notes = res.notes ?? [];
          this.total = res.total ?? 0;
        },
        error: (err: any) => {
          console.error('Erreur lors du chargement des notes', err);
          this.notes = [];
          this.total = 0;
        }
      });
  }

  // ---------------- FICHIERS ----------------
  handleFileInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.newFiles = Array.from(input.files);
    }
  }

  removeFile(index: number): void {
    this.newFiles.splice(index, 1);
  }

    // ---------------- AJOUTER UNE NOTE ----------------
  addNote(): void {
    if (!this.newNote.titre || !this.newNote.contenu || !this.newNote.categorie || !this.newNote.priorite) {
      alert('Veuillez remplir tous les champs obligatoires.');
      return;
    }

    this.api.createNoteWithFiles(this.newNote, this.newFiles).subscribe({
      next: (note: Note) => {
        if (!note.id) {
          console.error('ID manquant dans la note créée', note);
          return;
        }
        this.notes.unshift(note);
        this.newNote = {
          titre: '',
          contenu: '',
          equipe: this.currentUser?.equipe ?? '',
          auteur_id: this.currentUser?.id ?? 0,
          categorie: '',
          priorite: ''
        };
        this.newFiles = [];
        this.total += 1;
        // Redirection vers la page détail de la note
        this.router.navigate(['/notes', note.id]);
      },
      error: (err: any) => console.error('Erreur lors de l’ajout de la note', err)
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
