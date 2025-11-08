import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = '';
  password = '';
  errorMessage = '';
  sending = false;
  activationSent = false;

  constructor(private auth: AuthService, private router: Router) {}

  login() {
    this.errorMessage = '';
    this.sending = true;

    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        this.sending = false;
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.sending = false;

        const backendMessage = err.error?.detail || err.error?.message;

        if (backendMessage?.includes('pas encore activé')) {
          this.errorMessage = "Votre compte n’est pas activé. Vérifiez vos emails 📩.";
        } else {
          this.errorMessage = "Email ou mot de passe incorrect ❌";
        }
      }
    });
  }

  resendActivation() {
    this.errorMessage = '';
    this.activationSent = false;

    this.auth.resendActivation(this.email).subscribe({
      next: () => {
        this.activationSent = true;
        this.errorMessage = "✅ Email de réactivation envoyé !";
      },
      error: () => {
        this.errorMessage = "❌ Erreur lors de la réactivation";
      }
    });
  }
}
