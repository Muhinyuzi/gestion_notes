import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { EleveService, Eleve } from '../../../services/eleve.service';
import { NoteService, Note } from '../../../services/note.service';
import { UtilisateurService } from '../../../services/utilisateur.service';
import { DialogService } from '../../../services/dialog.service';

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
    private utilisateurService: UtilisateurService,
    private dialogService: DialogService,
    private location: Location
  ) {}

  // ===========================================================
  // 🔹 Initialisation
  // ===========================================================
  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadEleve(id);
      this.loadNotes();
      this.loadUsers();
      this.loadHistory(id);
    } else {
      this.errorMessage = 'ID élève non valide.';
    }
  }

  // ===========================================================
  // 🔹 Chargements de données
  // ===========================================================
  loadEleve(id: number): void {
    this.isLoading = true;
    this.eleveService.getEleveById(id).subscribe({
      next: data => {
        this.eleve = data;
        this.isLoading = false;

        if (data.note_id) {
          this.noteService.getNoteById(data.note_id).subscribe({
            next: n => this.note = n,
            error: err => console.error('Erreur chargement note', err)
          });
        }
      },
      error: err => {
        this.errorMessage = "Erreur lors du chargement de l'élève.";
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  loadNotes(): void {
    this.noteService.getNotes().subscribe({
      next: data => this.notes = data.notes || data,
      error: err => console.error('Erreur chargement notes', err)
    });
  }

  loadUsers(): void {
    this.utilisateurService.getUtilisateurs().subscribe({
      next: data => this.users = data.users || data,
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
        console.error(err);
      }
    });
  }

  // ===========================================================
  // 🔹 Helpers
  // ===========================================================
  getUserName(userId: number): string {
    if (!this.users?.length) return 'Utilisateur inconnu';
    const user = this.users.find(u => u.id === userId);
    return user ? `${user.nom} (${user.type})` : `#${userId}`;
  }

  getChangeKeys(changes: any): string[] {
    if (!changes || typeof changes !== 'object') return [];
    return Object.keys(changes);
  }

  // ===========================================================
  // 🔹 Actions principales
  // ===========================================================
  editEleve(): void {
    if (this.eleve?.id)
      this.router.navigate(['/eleves/edit', this.eleve.id]);
  }

  deleteEleve(): void {
    if (!this.eleve?.id) return;

    this.dialogService.confirm(
      "Confirmation de suppression",
      `Voulez-vous vraiment supprimer ${this.eleve.prenom} ${this.eleve.nom} ?`
    ).subscribe(result => {
      if (result) {
        this.eleveService.deleteEleve(this.eleve?.id!).subscribe({
          next: () => this.router.navigate(['/eleves']),
          error: err => {
            this.dialogService.confirm(
              "Erreur",
              "Une erreur est survenue lors de la suppression."
            );
            console.error(err);
          }
        });
      }
    });
  }

  // ===========================================================
  // 🔹 Gestion des modales
  // ===========================================================
  openAssignModal(eleve: Eleve) {
    this.modalEleve = eleve;
    this.modalMode = 'assign';
    this.selectedNoteId = null;
    this.showNoteModal = true;
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
          this.note = this.notes.find(n => n.id === updated.note_id);
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

  goBack(): void {
    this.location.back();
  }
}
