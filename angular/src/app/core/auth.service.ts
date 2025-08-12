import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

interface LoginResponse { access_token: string; token_type: string; }

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private tokenKey = 'dm_jwt';

  login(username: string, password: string) {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);
    return this.http.post<LoginResponse>(`${environment.api}/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  }

  setToken(token: string) { localStorage.setItem(this.tokenKey, token); }
  getToken() { return localStorage.getItem(this.tokenKey); }
  isAuthenticated() { return !!this.getToken(); }
  logout() { localStorage.removeItem(this.tokenKey); this.router.navigate(['/login']); }

  getPrincipal(): any | null {
    const token = this.getToken();
    if (!token) return null;
    const payload = token.split('.')[1];
    try {
      const json = JSON.parse(atob(payload));
      return json;
    } catch {
      return null;
    }
  }
}

