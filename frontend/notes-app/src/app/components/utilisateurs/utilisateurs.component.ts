import { Component, OnInit } from '@angular/core';
import { UtilisateurService, Utilisateur, UtilisateursResponse } from '../../services/utilisateur.service';
import { ToastService } from '../../services/toast.service';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../shared/confirm-dialog/confirm-dialog.component';
import { ChangePasswordComponent } from '../utilisateurs/account/change-password/change-password.component';
import { AuthService } from '../../services/auth.service';
import { Location } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-utilisateurs',
  templateUrl: './utilisateurs.component.html',
  styleUrls: ['./utilisateurs.component.css']
})
export class UtilisateursComponent implements OnInit {

  utilisateurs: Utilisateur[] = [];

  newUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
  selectedUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };

  isEditing = false;
  isAdding = false;
  isLoading = false;
  errorMessage = '';

  filterNom = '';
  filterEmail = '';
  filterEquipe = '';

  page = 1;
  limit = 10;
  total = 0;

  constructor(
    private api: UtilisateurService,
    private dialog: MatDialog,
    private location: Location,
    private toast: ToastService,
    private router: Router,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  // ✅ Form bind (important car ton HTML l'utilise)
  get formUser(): Utilisateur {
    return this.isEditing ? this.selectedUser : this.newUser;
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.limit);
  }

  get filteredUsers(): Utilisateur[] {
    return this.utilisateurs.filter(u =>
      u.nom?.toLowerCase().includes(this.filterNom.toLowerCase()) &&
      u.email?.toLowerCase().includes(this.filterEmail.toLowerCase()) &&
      (!this.filterEquipe || u.equipe?.toLowerCase().includes(this.filterEquipe.toLowerCase()))
    );
  }

  applyFilters(): void {}

  loadUsers(): void {
    this.isLoading = true;

    this.api.getUtilisateurs(this.page, this.limit).subscribe({
      next: (res: UtilisateursResponse) => {
        this.utilisateurs = res.users;
        this.total = res.total;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "❌ Impossible de charger les utilisateurs.";
        this.isLoading = false;
      }
    });
  }

  goToPage(page: number) {
    if (page < 1 || page > this.totalPages) return;
    this.page = page;
    this.loadUsers();
  }

  startAdding() {
    this.resetForm();
    this.isAdding = true;
    this.isEditing = false;
    this.toast.show("➕ Mode ajout activé");
  }

  cancelForm() {
    this.resetForm();
    this.isAdding = false;
    this.isEditing = false;
  }

  addUtilisateur() {
    if (!this.newUser.nom || !this.newUser.email || !this.newUser.mot_de_passe) {
      this.toast.show("❗ Nom, email et mot de passe requis", "error");
      return;
    }

    this.api.createUtilisateur(this.newUser).subscribe({
      next: (user) => {
        this.resetForm();
        this.isAdding = false;
        this.toast.show("📧 Email d'activation envoyé !");
        window.location.href = `/email-sent?email=${user.email}`;
      },
      error: () => this.toast.show("❌ Erreur de création", "error")
    });
  }

  editUtilisateur(user: Utilisateur) {
    this.selectedUser = { ...user, mot_de_passe: "" };
    this.isEditing = true;
    this.isAdding = false;
    this.toast.show("✏️ Mode édition activé");
  }

  updateUtilisateur() {
    if (!this.selectedUser.id) return;

    const original = this.utilisateurs.find(u => u.id === this.selectedUser.id);
    if (!original) return;

    const fields: (keyof Utilisateur)[] = ["nom", "email", "equipe", "adresse", "telephone", "type"];
    const noChange = fields.every(field =>
      (original[field] ?? "") === (this.selectedUser[field] ?? "")
    ) && !this.selectedUser.mot_de_passe;

    if (noChange) {
      this.toast.show("ℹ️ Aucun changement détecté.", "info");
      return;
    }

    const updatedData: Partial<Utilisateur> = { ...this.selectedUser };
    if (!updatedData.mot_de_passe) delete updatedData.mot_de_passe;

    this.isLoading = true;

    this.api.updateUtilisateur(this.selectedUser.id, updatedData).subscribe({
      next: (updated) => {
        const index = this.utilisateurs.findIndex(u => u.id === updated.id);
        if (index !== -1) this.utilisateurs[index] = updated;

        this.toast.show("✅ Modifications enregistrées !");
        this.resetForm();
        this.isEditing = false;
        this.isLoading = false;
      },
      error: () => {
        this.toast.show("❌ Erreur lors de la mise à jour", "error");
        this.isLoading = false;
      }
    });
  }

  deleteUtilisateur(user: Utilisateur) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: "350px",
      data: { message: `Supprimer ${user.nom} ?` }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (!result) return;

      this.api.deleteUtilisateur(user.id!).subscribe({
        next: () => {
          this.utilisateurs = this.utilisateurs.filter(u => u.id !== user.id);
          this.total--;
          this.toast.show("🗑️ Utilisateur supprimé !");
        },
        error: () => this.toast.show("❌ Erreur de suppression", "error")
      });
    });
  }

  /** 👤 Vérifie si l’utilisateur affiché = utilisateur connecté */
  isCurrentUser(user: Utilisateur): boolean {
    const current = this.auth.getUser();
    return !!(current && user && current.id === user.id);
  }

  /** 🔐 Ouvre la modale pour changer le mot de passe */
  openChangePasswordDialog(user: Utilisateur): void {
    if (!user.id) return;

    const isSelf = this.isCurrentUser(user);

    const dialogRef = this.dialog.open(ChangePasswordComponent, {
      width: '420px',
      data: { adminMode: !isSelf, userId: user.id },
      panelClass: 'custom-dialog-container'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result === 'success') {
        this.toast.show(
          isSelf
            ? "✅ Votre mot de passe a été changé avec succès."
            : `✅ Mot de passe de ${user.nom} mis à jour.`,
          'success'
        );
      }
    });
  }

  /** 🔑 Ouvre la modale pour changer son propre mot de passe */
  goToChangePassword(): void {
    const dialogRef = this.dialog.open(ChangePasswordComponent, {
      width: '420px',
      data: { adminMode: false },
      panelClass: 'custom-dialog-container'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result === 'success') {
        this.toast.show('✅ Votre mot de passe a été changé avec succès.', 'success');
      }
    });
  }

  resetForm() {
    this.selectedUser = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
    this.newUser = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
  }

  goBack() {
    this.location.back();
  }
}
