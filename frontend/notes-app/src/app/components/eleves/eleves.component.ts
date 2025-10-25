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

  // Variables modale
  showNoteModal = false;
  modalEleve: Eleve | null = null;
  modalMode: 'assign' | 'deassign' = 'assign';
  selectedNoteId: number | null = null;
  selectedNoteTitle: string | null = null;

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
      next: data => {
        this.eleves = data;
        this.isLoading = false;
      },
      error: err => {
        this.errorMessage = 'Erreur lors du chargement des élèves';
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  loadNotes(): void {
    this.noteService.getNotes().subscribe({
      next: data => this.notes = data.notes,
      error: err => console.error('Erreur chargement notes', err)
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
      error: err => {
        alert('Erreur lors de la suppression');
        console.error(err);
      }
    });
  }

  // 🔹 Modale assignation
  openAssignModal(eleve: Eleve) {
    this.modalEleve = eleve;
    this.modalMode = 'assign';
    this.selectedNoteId = null;
    this.showNoteModal = true;
  }

  // 🔹 Modale désassignation
  openDeassignModal(eleve: Eleve) {
    this.modalEleve = eleve;
    this.modalMode = 'deassign';
    const note = this.notes.find(n => n.id === eleve.note_id);
    this.selectedNoteTitle = note ? note.titre : `#${eleve.note_id}`;
    this.showNoteModal = true;
  }

  // Confirmer assignation ou désassignation
  confirmNoteAction() {
    if (!this.modalEleve) return;

    if (this.modalMode === 'assign') {
      if (!this.selectedNoteId) return;
      this.api.assignNoteToEleve(this.modalEleve.id!, this.selectedNoteId).subscribe({
        next: updated => {
          const index = this.eleves.findIndex(e => e.id === updated.id);
          if (index !== -1) this.eleves[index] = updated;
          this.closeNoteModal();
        },
        error: err => console.error('Erreur assignation note', err)
      });
    } else if (this.modalMode === 'deassign') {
      this.api.unassignNoteFromEleve(this.modalEleve.id!).subscribe({
        next: updated => {
          const index = this.eleves.findIndex(e => e.id === updated.id);
          if (index !== -1) this.eleves[index] = updated;
          this.closeNoteModal();
        },
        error: err => console.error('Erreur désassignation note', err)
      });
    }
  }

  closeNoteModal() {
    this.showNoteModal = false;
    this.modalEleve = null;
    this.selectedNoteId = null;
    this.selectedNoteTitle = null;
  }
}
