import { Injectable } from '@angular/core';
import {
  CanActivate,
  Router,
  UrlTree
} from '@angular/router';
import { AuthService } from '../services/auth.service';
import { ToastService } from '../services/toast.service'; // ⚡ pour message clair

@Injectable({ providedIn: 'root' })
export class AdminGuard implements CanActivate {
  constructor(
    private auth: AuthService,
    private router: Router,
    private toast: ToastService
  ) {}

  canActivate(): boolean | UrlTree {
    const user = this.auth.getUser();

    // 🔒 Vérifie si l'utilisateur est connecté
    if (!user) {
      this.toast.show("🔐 Veuillez d'abord vous connecter", "error");
      return this.router.createUrlTree(['/login']);
    }

    // ✅ Vérifie s’il est admin
    if (user.type === 'admin') {
      return true;
    }

    // 🚫 Sinon → refus d’accès avec message
    this.toast.show("⛔ Accès réservé aux administrateurs", "error");
    return this.router.createUrlTree(['/']);
  }
}
