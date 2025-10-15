import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UtilisateurService, UtilisateurDetailOut } from '../../services/utilisateur.service';
import { ToastComponent } from '../shared/toast/toast.component';
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
  selectedFile: File | null = null;
  avatarUrl: string = 'http://127.0.0.1:8000/uploads/avatars/default-avatar.png';

  constructor(
    private route: ActivatedRoute,
    private api: UtilisateurService,
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
        this.avatarUrl = data.avatar_url || 'http://127.0.0.1:8000/uploads/avatars/default-avatar.png';
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
        this.utilisateur = updated as UtilisateurDetailOut;
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
      if (result && this.utilisateur) {
        this.api.deleteUtilisateur(this.utilisateur.id).subscribe({
          next: () => this.router.navigate(['/utilisateurs']),
          error: () => this.toast.show("❌ Erreur lors de la suppression", "error")
        });
      }
    });
  }

  onAvatarSelected(event: any) {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      this.selectedFile = file;
      this.avatarUrl = URL.createObjectURL(file); // Preview instantané
    } else {
      this.toast.show("❌ Veuillez sélectionner une image valide", "error");
    }
  }

  uploadAvatar() {
    if (!this.selectedFile || !this.utilisateur?.id) return;

    const formData = new FormData();
    formData.append("file", this.selectedFile);

    this.api.uploadAvatar(this.utilisateur.id, formData).subscribe({
      next: (res: any) => {
        if (this.utilisateur) {
          this.utilisateur.avatar_url = res.avatar_url;
          this.avatarUrl = res.avatar_url;
          this.toast.show("✅ Avatar mis à jour avec succès !", "success");
        }
      },
      error: (err) => {
        console.error(err);
        this.toast.show("❌ Erreur lors de l'upload", "error");
      }
    });
  }

  openFilePicker(input: HTMLInputElement) {
  input.click();
}

}
