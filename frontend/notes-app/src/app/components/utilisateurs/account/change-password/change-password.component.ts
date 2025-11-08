import { Component } from '@angular/core';
import { AuthService } from '../../../../services/auth.service';
import { ToastService } from '../../../../services/toast.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent {
  oldPassword = '';
  newPassword = '';
  confirmPassword = '';
  isLoading = false;

  showOld = false;
  showNew = false;
  showConfirm = false;

  strengthLabel = '';
  strengthClass = '';

  constructor(
    private auth: AuthService,
    private toast: ToastService,
    private router: Router
  ) {}

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
  /** Soumission du formulaire */
  changePassword() {
    if (!this.oldPassword.trim() || !this.newPassword.trim()) {
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
    this.auth.changePassword(this.oldPassword, this.newPassword).subscribe({
      next: (res) => {
        this.isLoading = false;
        const currentUser = this.auth.getUser();
        const isAdmin = currentUser?.type === 'admin';

        if (!isAdmin) {
          this.toast.show('✅ Mot de passe changé avec succès. Vous allez être déconnecté.', 'success');
          setTimeout(() => {
            this.auth.logout();
            this.toast.show('Veuillez vous reconnecter avec votre nouveau mot de passe 🔐', 'success');
            this.router.navigate(['/login']);
          }, 1800);
        } else {
          this.toast.show('✅ Mot de passe mis à jour avec succès pour cet utilisateur.', 'success');
          setTimeout(() => this.router.navigate(['/utilisateurs']), 1500);
        }

        this.oldPassword = this.newPassword = this.confirmPassword = '';
        this.strengthLabel = this.strengthClass = '';
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

  toggleVisibility(field: 'old' | 'new' | 'confirm') {
    if (field === 'old') this.showOld = !this.showOld;
    if (field === 'new') this.showNew = !this.showNew;
    if (field === 'confirm') this.showConfirm = !this.showConfirm;
  }
}
