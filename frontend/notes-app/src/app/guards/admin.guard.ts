import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {

  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    const user = this.auth.getUser();

    if (user && user.type === 'admin') {
      // ✅ L'utilisateur est admin, accès autorisé
      return true;
    }

    // 🚫 Accès refusé → redirection selon le cas
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/']); // utilisateur connecté mais non admin
    } else {
      this.router.navigate(['/login']); // utilisateur non connecté
    }

    return false;
  }
}
