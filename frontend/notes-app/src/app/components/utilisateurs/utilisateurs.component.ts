import { Component, OnInit } from '@angular/core';
import { UtilisateurService, Utilisateur, PaginatedUsers } from '../../services/utilisateur.service';
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

  typesUtilisateurs: string[] = ['admin', 'user', 'dev', 'manager', 'support'];
  equipes: string[] = ['Dev', 'QA', 'Support', 'Design', 'RH', 'Ops'];

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

  // ✅ Pour liaison formulaire
  get formUser(): Utilisateur {
    return this.isEditing ? this.selectedUser : this.newUser;
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.limit);
  }

  // ✅ Sécurisé contre undefined + filtres dynamiques
  get filteredUsers(): Utilisateur[] {
    if (!this.utilisateurs || this.utilisateurs.length === 0) return [];

    return this.utilisateurs.filter(u =>
      u.nom?.toLowerCase().includes(this.filterNom.toLowerCase()) &&
      u.email?.toLowerCase().includes(this.filterEmail.toLowerCase()) &&
      (!this.filterEquipe || u.equipe?.toLowerCase().includes(this.filterEquipe.toLowerCase()))
    );
  }

  // 🔍 Réapplique les filtres
  applyFilters(): void {
    this.page = 1;
  }

  // 📦 Charge la liste des utilisateurs
  loadUsers(): void {
    this.isLoading = true;
    this.api.getUtilisateurs(this.page, this.limit).subscribe({
      next: (res: PaginatedUsers) => {
        this.utilisateurs = res.users ?? [];
        this.total = res.total ?? 0;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "❌ Impossible de charger les utilisateurs.";
        this.isLoading = false;
      }
    });
  }

  // 🔄 Pagination
  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.page = page;
    this.loadUsers();
  }

  // ➕ Ajout utilisateur
  startAdding(): void {
    this.resetForm();
    this.isAdding = true;
    this.isEditing = false;
    this.toast.show("➕ Mode ajout activé");
    // 🧩 Générer automatiquement un mot de passe aléatoire
    this.generatePassword();

    this.toast.show("➕ Mode ajout activé (mot de passe généré automatiquement)");
  }

  cancelForm(): void {
    this.resetForm();
    this.isAdding = false;
    this.isEditing = false;
  }

  addUtilisateur(): void {
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

  // ✏️ Edition utilisateur
  editUtilisateur(user: Utilisateur): void {
    this.selectedUser = { ...user, mot_de_passe: "" };
    this.isEditing = true;
    this.isAdding = false;
    this.toast.show("✏️ Mode édition activé");
  }

  // 💾 Sauvegarde des modifications
  updateUtilisateur(): void {
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

  // 🗑️ Suppression utilisateur
  deleteUtilisateur(user: Utilisateur): void {
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

  // ♻️ Réinitialise les formulaires
  resetForm(): void {
    this.selectedUser = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
    this.newUser = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
  }

  goBack(): void {
    this.location.back();
  }

  generatePassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let pwd = '';
    for (let i = 0; i < 8; i++) {
      pwd += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    this.formUser.mot_de_passe = pwd;
  }
}
