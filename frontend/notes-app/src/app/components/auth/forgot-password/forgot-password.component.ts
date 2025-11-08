import { Component } from '@angular/core';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent {
  email = '';
  sending = false;
  success = false;
  errorMessage = '';

  constructor(private auth: AuthService) {}

  onSubmit() {
    this.errorMessage = '';
    this.sending = true;

    this.auth.forgotPassword(this.email).subscribe({
      next: () => {
        this.sending = false;
        this.success = true;
      },
      error: () => {
        this.sending = false;
        this.errorMessage =
          "❌ Adresse e-mail introuvable ou erreur serveur.";
      }
    });
  }
}
