import { Component, inject, signal } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd, RouterLink } from '@angular/router';
import { NgIf } from '@angular/common';
import { AuthService } from './core/auth.service';
import { ToastComponent } from './shared/toast.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, NgIf, ToastComponent],
  template: `
  <div class="min-h-screen flex flex-col">
    <header class="px-4 py-3 border-b border-white/10 sticky top-0 z-30 bg-black/50 backdrop-blur" *ngIf="!isPublicMenu()">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <a class="flex items-center gap-3" [routerLink]="['/login']">
          <i class="pi pi-qrcode text-[var(--luxury-gold)] text-xl"></i>
          <span class="lux-title">Digital Menu</span>
        </a>
        <nav class="flex items-center gap-3 text-sm">
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/restaurant']" *ngIf="isAdmin()">Restaurants</a>
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/restaurant', managerSlug(), 'edit']" *ngIf="isManager()">My Restaurant</a>
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/login']" *ngIf="!isLogged()">Login</a>
          <button class="text-red-300 hover:text-red-400" *ngIf="isLogged()" (click)="logout()">Logout</button>
        </nav>
      </div>
    </header>
    <main class="flex-1">
      <router-outlet></router-outlet>
    </main>
    <footer class="py-6 text-center text-white/50 text-xs" *ngIf="!isPublicMenu()">© {{year}} Digital Menu</footer>
  </div>
  <app-toast></app-toast>
  `
})
export class AppComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  year = new Date().getFullYear();

  isLogged() { return this.auth.isAuthenticated(); }
  isAdmin() { return this.auth.getPrincipal()?.role === 'admin'; }
  isManager() { return this.auth.getPrincipal()?.role === 'manager'; }
  managerSlug() { return this.auth.getPrincipal()?.restaurant_slug; }
  logout() { this.auth.logout(); }
  isPublicMenu() {
    // Public menu route is any single-segment path like /:slug (not starting with known app routes)
    const url = this.router.url.split('?')[0].split('#')[0];
    const first = url.replace(/^\//, '').split('/')[0];
    const nonPublic = new Set(['', 'login', 'restaurant']);
    return !nonPublic.has(first);
  }
}

