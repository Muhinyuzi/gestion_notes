/*import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private baseUrl = 'http://127.0.0.1:8000'; // ton API FastAPI
  private tokenKey = 'auth_token';

  constructor(private http: HttpClient,private router: Router) {}

  login(email: string, password: string): Observable<any> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    return this.http.post<any>(`${this.baseUrl}/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).pipe(
      tap(response => {
        localStorage.setItem(this.tokenKey, response.access_token);
      })
    );
  }

  logout() {
    localStorage.removeItem('token');  // ❌ On supprime le token
    this.router.navigate(['/login']);  // 🔄 Redirection vers login
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}
*/
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

  isLoggedIn(): boolean {
    return this._isLoggedIn$.value;
  }

  logout(): void {
    console.log('[AuthService] logout() called');
    localStorage.removeItem(this.TOKEN_KEY);
    this._isLoggedIn$.next(false);
    this.router.navigate(['/login']);
  }
/*
  // 👇 Ajout de la méthode login()
  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/login`, { email, password }).pipe(
      tap(res => {
        if (res && res.access_token) {
          this.setToken(res.access_token);
        }
      })
    );
  }
    */
   login(email: string, password: string): Observable<any> {
  const body = new URLSearchParams();
  body.set('username', email);   // ⚡ obligatoire
  body.set('password', password);

  return this.http.post<any>(`${this.API_URL}/login`, body.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }).pipe(
    tap(res => {
      if (res && res.access_token) {
        this.setToken(res.access_token);
      }
    })
  );
}
}