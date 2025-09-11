import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'notes-app';
  /*constructor(public auth: AuthService) {}

  logout() {
    this.auth.logout();  // redirige via le service
  }*/
  constructor(public auth: AuthService) {
    // pour debug rapide dans la console :
    (window as any).authService = auth;
  }

  logout(): void {
    console.log('AppComponent.logout clicked');
    this.auth.logout();
  }
}
