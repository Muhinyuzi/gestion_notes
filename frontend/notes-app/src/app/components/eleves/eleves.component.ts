import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { EleveService, Eleve } from '../../services/eleve.service';
import { NoteService, Note } from '../../services/note.service';

@Component({
  selector: 'app-eleves',
  templateUrl: './eleves.component.html',
  styleUrls: ['./eleves.component.css']
})
export class ElevesComponent implements OnInit {

  eleves: Eleve[] = [];
  notes: Note[] = [];
  isLoading = false;
  errorMessage: string = '';

  constructor(
    private api: EleveService,
    private noteService: NoteService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadEleves();
    this.loadNotes();
  }

  loadEleves(): void {
  this.isLoading = true;
  this.api.getEleves().subscribe({
    next: (data) => {
      console.log('✅ Données reçues du backend:', data);
      this.eleves = data; // data est déjà une liste
      this.isLoading = false;
    },
    error: (err) => {
      this.errorMessage = 'Erreur lors du chargement des élèves';
      this.isLoading = false;
      console.error('❌ Erreur API:', err);
    }
  });
}

  loadNotes(): void {
    this.noteService.getNotes().subscribe({
      next: (data) => this.notes = data.notes,
      error: (err) => console.error('Erreur chargement notes', err)
    });
  }

  goToDetail(eleve: Eleve) {
    this.router.navigate(['/eleves', eleve.id]);
  }

  addEleve() {
    this.router.navigate(['/eleves/create']);
  }

  editEleve(eleve: Eleve) {
    this.router.navigate(['/eleves/edit', eleve.id]);
  }

  deleteEleve(eleve: Eleve) {
    if (!confirm(`Supprimer l'élève ${eleve.nom} ${eleve.prenom} ?`)) return;

    this.api.deleteEleve(eleve.id!).subscribe({
      next: () => this.eleves = this.eleves.filter(e => e.id !== eleve.id),
      error: (err) => {
        alert('Erreur lors de la suppression');
        console.error(err);
      }
    });
  }

  assignNote(eleve: Eleve, noteId: number) {
    this.api.assignNoteToEleve(eleve.id!, noteId).subscribe({
      next: updated => {
        const index = this.eleves.findIndex(e => e.id === eleve.id);
        if (index !== -1) this.eleves[index] = updated;
      },
      error: err => console.error('Erreur assignation note', err)
    });
  }

  deassignNote(eleve: Eleve) {
    this.api.unassignNoteFromEleve(eleve.id!).subscribe({
      next: updated => {
        const index = this.eleves.findIndex(e => e.id === eleve.id);
        if (index !== -1) this.eleves[index] = updated;
      },
      error: err => console.error('Erreur désassignation note', err)
    });
  }

  onNoteSelect(eleve: Eleve, event: Event) {
  const select = event.target as HTMLSelectElement;
  const noteId = Number(select.value);
  if (!noteId) return;

  this.api.assignNoteToEleve(eleve.id!, noteId).subscribe({
    next: updatedEleve => {
      const index = this.eleves.findIndex(e => e.id === eleve.id);
      if (index !== -1) this.eleves[index] = updatedEleve;
    },
    error: err => console.error(err)
  });
}

}
