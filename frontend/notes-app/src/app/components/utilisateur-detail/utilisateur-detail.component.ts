import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService, UtilisateurDetailOut } from '../../services/api.service';
import { ToastComponent } from '../../components/shared/toast/toast.component';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-utilisateur-detail',
  templateUrl: './utilisateur-detail.component.html',
  styleUrls: ['./utilisateur-detail.component.css']
})
export class UtilisateurDetailComponent implements OnInit {
  @ViewChild('toast') toast!: ToastComponent;

  utilisateur?: UtilisateurDetailOut;
  isLoading = true;
  isEditing = false;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private router: Router,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    const id = idParam ? Number(idParam) : null;
    if (!id) {
      this.isLoading = false;
      this.toast.show("ID utilisateur invalide.", "error");
      return;
    }
    this.loadUtilisateur(id);
  }

  loadUtilisateur(id: number) {
    this.api.getUtilisateurDetail(id).subscribe({
      next: (data) => {
        this.utilisateur = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.toast.show("Impossible de charger l'utilisateur.", "error");
      }
    });
  }

  updateUtilisateur() {
    if (!this.utilisateur) return;
    this.api.updateUtilisateur(this.utilisateur.id, this.utilisateur).subscribe({
      next: (updated) => {
        this.utilisateur as UtilisateurDetailOut == updated;
        this.isEditing = false;
        this.toast.show("✅ Utilisateur mis à jour avec succès !", "success");
      },
      error: () => this.toast.show("❌ Erreur lors de la mise à jour", "error")
    });
  }

  deleteUtilisateur(): void {
    if (!this.utilisateur) return;

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '350px',
      data: { message: "Voulez-vous vraiment supprimer cet utilisateur ?" }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.api.deleteUtilisateur(this.utilisateur!.id).subscribe({
          next: () => this.router.navigate(['/utilisateurs']),
          error: () => this.toast.show("❌ Erreur lors de la suppression", "error")
        });
      }
    });
  }
}
