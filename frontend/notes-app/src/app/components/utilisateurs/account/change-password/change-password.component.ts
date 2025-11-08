import { Component, Input, Inject, Optional } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';
import { ToastService } from '../../../../services/toast.service';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent {
  @Input() adminMode = false;
  @Input() userId?: number;

  oldPassword = '';
  newPassword = '';
  confirmPassword = '';
  isLoading = false;
  isDone = false;

  showOld = false;
  showNew = false;
  showConfirm = false;

  strengthLabel = '';
  strengthClass = '';

  constructor(
    private auth: AuthService,
    private toast: ToastService,
    private router: Router,
    @Optional() private dialogRef?: MatDialogRef<ChangePasswordComponent>,
    @Optional() @Inject(MAT_DIALOG_DATA) public data?: any
  ) {
    if (data) {
      this.adminMode = data.adminMode ?? false;
      this.userId = data.userId ?? undefined;
    }
  }

  /** Vérifie la force du mot de passe */
  checkPasswordStrength(): void {
    const pwd = this.newPassword;
    if (!pwd) {
      this.strengthLabel = '';
      this.strengthClass = '';
      return;
    }

    const hasLetters = /[a-zA-Z]/.test(pwd);
    const hasNumbers = /\d/.test(pwd);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);

    if (pwd.length < 8) {
      this.strengthLabel = 'Faible';
      this.strengthClass = 'weak';
    } else if (pwd.length >= 8 && ((hasLetters && hasNumbers) || hasSpecial)) {
      this.strengthLabel = 'Moyen';
      this.strengthClass = 'medium';
    } else if (pwd.length >= 10 && hasLetters && hasNumbers && hasSpecial) {
      this.strengthLabel = 'Fort';
      this.strengthClass = 'strong';
    } else {
      this.strengthLabel = 'Faible';
      this.strengthClass = 'weak';
    }
  }

  /** 🚀 Soumission du formulaire */
  changePassword(): void {
    const mustProvideOld = !this.adminMode || (this.adminMode && !this.userId);

    if (mustProvideOld && !this.oldPassword.trim()) {
      this.toast.show('Veuillez entrer votre ancien mot de passe ⚠️', 'error');
      return;
    }

    if (!this.newPassword.trim() || !this.confirmPassword.trim()) {
      this.toast.show('Veuillez remplir tous les champs ⚠️', 'error');
      return;
    }

    if (this.newPassword.length < 8) {
      this.toast.show('Le mot de passe doit contenir au moins 8 caractères 🔒', 'error');
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.toast.show('Les mots de passe ne correspondent pas ❌', 'error');
      return;
    }

    this.isLoading = true;

    const request$ =
      this.adminMode && this.userId
        ? this.auth.adminChangePassword(this.userId, this.newPassword)
        : this.auth.changePassword(this.oldPassword, this.newPassword);

    request$.subscribe({
      next: () => {
        this.isLoading = false;
        this.isDone = true; // ✅ affiche le message de succès
        this.oldPassword = this.newPassword = this.confirmPassword = '';
        this.strengthLabel = this.strengthClass = '';

        if (this.adminMode && this.userId) {
          // 👑 Admin change un autre utilisateur
          this.toast.show('✅ Mot de passe mis à jour avec succès pour cet utilisateur.', 'success');
          setTimeout(() => this.closeDialog('success'), 2000);
        } else {
          // 👤 Utilisateur normal ou admin change son propre mot de passe
          this.toast.show('✅ Mot de passe changé avec succès. Vous allez être déconnecté.', 'success');
          setTimeout(() => {
            this.closeDialog('success');
            this.auth.logout();
            this.toast.show('Veuillez vous reconnecter avec votre nouveau mot de passe 🔐', 'success');
            this.router.navigate(['/login']);
          }, 2500);
        }
      },
      error: (err) => {
        this.isLoading = false;
        const msg =
          err.error?.detail ||
          (Array.isArray(err.error?.detail) ? err.error.detail[0]?.msg : null) ||
          'Erreur lors du changement de mot de passe ❌';
        this.toast.show(msg, 'error');
      }
    });
  }

  toggleVisibility(field: 'old' | 'new' | 'confirm'): void {
    if (field === 'old') this.showOld = !this.showOld;
    if (field === 'new') this.showNew = !this.showNew;
    if (field === 'confirm') this.showConfirm = !this.showConfirm;
  }

  /** Ferme la modale si elle existe */
  closeDialog(result?: any): void {
    if (this.dialogRef) {
      this.dialogRef.close(result);
    }
  }
}
