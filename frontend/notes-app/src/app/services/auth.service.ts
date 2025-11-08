// src/app/services/auth.service.ts
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private _isLoggedIn$ = new BehaviorSubject<boolean>(!!this.getToken());
  readonly isLoggedIn$ = this._isLoggedIn$.asObservable();

  private readonly API_URL = 'http://127.0.0.1:8000'; // ton backend FastAPI

  constructor(private router: Router, private http: HttpClient) {}

  /* 🔑 Gestion du token et utilisateur */
  setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    this._isLoggedIn$.next(true);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  setUser(user: any): void {
    localStorage.setItem('auth_user', JSON.stringify(user));
  }

  getUser(): any | null {
    const user = localStorage.getItem('auth_user');
    return user ? JSON.parse(user) : null;
  }

  getUserId(): number | null {
    return this.getUser()?.id ?? null;
  }

  getUserName(): string | null {
    return this.getUser()?.nom ?? null;
  }

  /* 🚪 Login */
  login(email: string, password: string): Observable<any> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    return this.http.post<any>(`${this.API_URL}/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).pipe(
      tap(res => {
        if (res && res.access_token) {
          this.setToken(res.access_token);
          if (res.user) this.setUser(res.user);
        }
      })
    );
  }

  /* 🔁 Renvoi de l'email d’activation */
  resendActivation(email: string) {
    return this.http.post(`${this.API_URL}/auth/resend-activation`, { email });
  }

  /* 🧠 État de connexion */
  isLoggedIn(): boolean {
    return this._isLoggedIn$.value;
  }

  /* 🚪 Déconnexion */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('auth_user');
    this._isLoggedIn$.next(false);
    this.router.navigate(['/login']);
  }

  /* 🔐 Mot de passe oublié / réinitialisation */
  forgotPassword(email: string) {
    return this.http.post(`${this.API_URL}/auth/forgot-password`, { email });
  }

  resetPassword(token: string, newPassword: string) {
    return this.http.post(`${this.API_URL}/auth/reset-password`, {
      token,
      new_password: newPassword
    });
  }

  /* ✅ Activation de compte */
  activateAccount(token: string) {
    return this.http.get(`${this.API_URL}/auth/activate?token=${token}`);
  }

  /* 👤 Changement de mot de passe (utilisateur connecté) */
  changePassword(oldPassword: string, newPassword: string): Observable<any> {
    const token = this.getToken();
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    return this.http.patch(`${this.API_URL}/auth/change-password`, {
      old_password: oldPassword,
      new_password: newPassword
    }, { headers });
  }

  /* 👑 Changement de mot de passe par admin */
  adminChangePassword(userId: number, newPassword: string): Observable<any> {
    const token = this.getToken();
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    return this.http.patch(`${this.API_URL}/auth/admin/change-password/${userId}`, {
      new_password: newPassword
    }, { headers });
  }
  isAdmin(): boolean {
    const user = this.getUser();
    return user && user.type?.toLowerCase() === 'admin';
  }
}
