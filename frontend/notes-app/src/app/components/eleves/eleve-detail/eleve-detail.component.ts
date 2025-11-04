import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { EleveService, Eleve } from '../../../services/eleve.service';
import { NoteService, Note } from '../../../services/note.service';
import { UtilisateurService } from '../../../services/utilisateur.service';

@Component({
  selector: 'app-eleve-detail',
  templateUrl: './eleve-detail.component.html',
  styleUrls: ['./eleve-detail.component.css']
})
export class EleveDetailComponent implements OnInit {

  eleve?: Eleve;
  note?: Note;
  notes: Note[] = [];
  users: any[] = [];

  isLoading = false;
  errorMessage = '';

  history: any[] = [];
  loadingHistory = false;
  errorHistory = '';

  // 🔹 Modale
  showNoteModal = false;
  modalEleve: Eleve | null = null;
  modalMode: 'assign' | 'deassign' = 'assign';
  selectedNoteId: number | null = null;
  selectedNoteTitle: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private eleveService: EleveService,
    private noteService: NoteService,
    private utilisateurService: UtilisateurService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadEleve(id);
      this.loadHistory(id);
      this.loadUsers();
      this.loadNotes(); // ✅ même logique que la liste
    } else {
      this.errorMessage = 'ID élève non valide.';
    }
  }

  // ===============================
  // 🔹 Chargements
  // ===============================

  loadEleve(id: number): void {
    this.isLoading = true;
    this.eleveService.getEleveById(id).subscribe({
      next: (data) => {
        this.eleve = data;
        this.isLoading = false;

        // Charger la note associée si présente
        if (data.note_id) {
          this.noteService.getNoteById(data.note_id).subscribe({
            next: (n) => this.note = n,
            error: (err) => console.error('Erreur chargement note', err)
          });
        }
      },
      error: (err) => {
        this.errorMessage = 'Erreur lors du chargement de l’élève.';
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

  loadUsers(): void {
    this.utilisateurService.getUtilisateurs().subscribe({
      next: data => this.users = data.users,
      error: err => console.error('Erreur chargement utilisateurs', err)
    });
  }

  loadHistory(id: number): void {
    this.loadingHistory = true;
    this.eleveService.getEleveHistory(id).subscribe({
      next: data => {
        this.history = data;
        this.loadingHistory = false;
      },
      error: err => {
        this.errorHistory = "Erreur lors du chargement de l’historique.";
        this.loadingHistory = false;
      }
    });
  }

  // ===============================
  // 🔹 Helpers
  // ===============================

  getUserName(userId: number): string {
    const user = this.users.find(u => u.id === userId);
    return user ? `${user.nom} (${user.type})` : `Utilisateur #${userId}`;
  }

  getChangeKeys(changes: any): string[] {
  if (!changes || typeof changes !== 'object') return [];
  return Object.keys(changes);
}

  // ===============================
  // 🔹 Actions élève
  // ===============================

  editEleve(): void {
    if (this.eleve?.id)
      this.router.navigate(['/eleves/edit', this.eleve.id]);
  }

  deleteEleve(): void {
    if (!this.eleve?.id) return;
    if (!confirm(`Supprimer ${this.eleve.prenom} ${this.eleve.nom} ?`)) return;

    this.eleveService.deleteEleve(this.eleve.id).subscribe({
      next: () => this.router.navigate(['/eleves']),
      error: err => {
        alert('Erreur lors de la suppression');
        console.error(err);
      }
    });
  }

  // ===============================
  // 🔹 Modale assignation / désassignation (même logique que la liste)
  // ===============================

openAssignModal(eleve: Eleve) {
  this.modalEleve = eleve;
  this.modalMode = 'assign';
  this.selectedNoteId = null;

  // ⚙️ Charger les notes si elles ne sont pas encore prêtes
  if (this.notes.length === 0) {
    this.noteService.getNotes().subscribe({
      next: data => {
        this.notes = data.notes;  // ou data si ton backend renvoie un tableau simple
        this.showNoteModal = true;
      },
      error: err => console.error('Erreur chargement notes', err)
    });
  } else {
    this.showNoteModal = true;
  }
}

  openDeassignModal(eleve: Eleve) {
    this.modalEleve = eleve;
    this.modalMode = 'deassign';
    const note = this.notes.find(n => n.id === eleve.note_id);
    this.selectedNoteTitle = note ? note.titre : `#${eleve.note_id}`;
    this.showNoteModal = true;
  }

  confirmNoteAction() {
    if (!this.modalEleve) return;

    if (this.modalMode === 'assign') {
      if (!this.selectedNoteId) return;
      this.eleveService.assignNoteToEleve(this.modalEleve.id!, this.selectedNoteId).subscribe({
        next: updated => {
          this.eleve = updated;

          // Rafraîchir la note affichée
          if (updated.note_id) {
            const n = this.notes.find(n => n.id === updated.note_id);
            this.note = n ?? undefined;
          }

          this.closeNoteModal();
        },
        error: err => console.error('Erreur assignation note', err)
      });

    } else if (this.modalMode === 'deassign') {
      this.eleveService.unassignNoteFromEleve(this.modalEleve.id!).subscribe({
        next: updated => {
          this.eleve = updated;
          this.note = undefined;
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
