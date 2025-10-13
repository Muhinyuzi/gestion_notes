import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'notes-app';
  menuOpen = false;

  constructor(public auth: AuthService, private router: Router) {
    // Debug rapide
    (window as any).authService = auth;
  }

  toggleMenu() {
    this.menuOpen = !this.menuOpen;
  }

  closeMenu() {
    this.menuOpen = false;
  }

  logout(): void {
    console.log('AppComponent.logout clicked');
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  /** 🔹 Retourne true si l'utilisateur connecté est admin */
  isAdmin(): boolean {
    const user = this.auth.getUser();
    return user && user.type === 'admin';
  }

  /** 🔹 Retourne l'id de l'utilisateur connecté */
  getUserId(): number | null {
    return this.auth.getUser()?.id ?? null;
  }

  /** 🔹 Retourne true si l'utilisateur est connecté */
  isLoggedIn(): boolean {
    return this.auth.isLoggedIn();
  }

  /** 🔹 Retourne le rôle actuel (utile pour affichage ou debug) */
  getUserRole(): string {
    const user = this.auth.getUser();
    return user ? user.type : '';
  }
}