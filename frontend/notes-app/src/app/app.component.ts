import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'notes-app';
  menuOpen = false;
  constructor(public auth: AuthService) {
    // pour debug rapide dans la console :
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
  }
}
