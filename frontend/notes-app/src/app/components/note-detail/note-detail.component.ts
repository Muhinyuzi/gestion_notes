import { Component, OnInit, ViewChild} from '@angular/core';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { ApiService, Note } from '../../services/api.service';
import { ToastComponent } from '../../components/shared/toast/toast.component';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-note-detail',
  templateUrl: './note-detail.component.html',
  styleUrls: ['./note-detail.component.css']
})
export class NoteDetailComponent implements OnInit {
  @ViewChild('toast') toast!: ToastComponent;

  note?: Note;
  isLoading = true;
  errorMessage = '';
  isEditing = false;

  constructor(private route: ActivatedRoute, private api: ApiService, private router: Router,
  private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.api.getNoteById(id).subscribe({
      next: (data) => {
        this.note = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "Impossible de charger la note.";
        this.isLoading = false;
      }
    });
  }

  updateNote() {
    if (this.note) {
      this.api.updateNote(this.note.id, this.note).subscribe({
        next: () => {
          this.isEditing = false;
          this.toast.show("✅ Note mise à jour avec succès !", "success");
        },
        error: () => {
          this.toast.show("❌ Erreur lors de la mise à jour", "error");
        }
      });
    }
  }

deleteNote(): void {
  if (!this.note) return;

  const dialogRef = this.dialog.open(ConfirmDialogComponent, {
    width: '350px',
    data: { message: "Voulez-vous vraiment supprimer cette note ?" }
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result) { // si l'utilisateur a confirmé
      this.api.deleteNote(this.note!.id).subscribe({
        next: () => this.router.navigate(['/notes']),
        error: () => this.errorMessage = "Erreur lors de la suppression."
      });
    }
  });
}
}