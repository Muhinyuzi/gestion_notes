// src/app/services/auth.service.ts
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private _isLoggedIn$ = new BehaviorSubject<boolean>(!!this.getToken());
  readonly isLoggedIn$ = this._isLoggedIn$.asObservable();

  private readonly API_URL = 'http://127.0.0.1:8000'; // ton backend FastAPI

  constructor(private router: Router, private http: HttpClient) {}

  setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    this._isLoggedIn$.next(true);
    console.log('[AuthService] setToken');
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

getUserName(): number | null {
  return this.getUser()?.name ?? null;
}

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
        if (res.user) {
          this.setUser(res.user); // ⚡ stocker l'utilisateur
        }
      }
    })
  );
}

  isLoggedIn(): boolean {
    return this._isLoggedIn$.value;
  }

  logout(): void {
    console.log('[AuthService] logout() called');
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('auth_user');
    this._isLoggedIn$.next(false);
    this.router.navigate(['/login']);
  }

}