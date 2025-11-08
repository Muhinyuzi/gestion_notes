import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-activate-account',
  templateUrl: './activate-account.component.html',
  styleUrls: ['./activate-account.component.css']
})
export class ActivateAccountComponent implements OnInit {
  token = '';
  loading = true;
  success = false;
  errorMessage = '';

  constructor(private route: ActivatedRoute, private auth: AuthService) {}

  ngOnInit() {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';

    if (!this.token) {
      this.loading = false;
      this.errorMessage = 'Lien d’activation invalide.';
      return;
    }

    // Appel API pour activer le compte
    this.auth.activateAccount(this.token).subscribe({
      next: () => {
        this.loading = false;
        this.success = true;
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'Le lien est invalide ou expiré.';
      }
    });
  }
}
