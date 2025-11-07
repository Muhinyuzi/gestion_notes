import { Injectable } from '@angular/core';
import {
  CanActivate,
  Router,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  UrlTree
} from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): boolean | UrlTree {
    const isLoggedIn = this.auth.isLoggedIn();

    // 🔓 Liste des routes publiques (pas besoin d'être connecté)
    const publicRoutes = [
      '/login',
      '/activate',
      '/forgot-password',
      '/reset-password',
      '/email-sent'
    ];

    // ✅ Si la route actuelle est publique → autoriser sans vérif
    if (publicRoutes.includes(state.url.split('?')[0])) {
      return true;
    }

    // 🔒 Si connecté → OK
    if (isLoggedIn) {
      return true;
    }

    // 🚫 Sinon → redirige vers login
    return this.router.createUrlTree(['/login']);
  }
}
