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
    <header class="px-4 py-3 border-b border-white/10 sticky top-0 z-30 bg-black/50 backdrop-blur">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <a class="flex items-center gap-3" [routerLink]="['/digital_menu']">
          <i class="pi pi-qrcode text-[var(--luxury-gold)] text-xl"></i>
          <span class="lux-title">Digital Menu</span>
        </a>
        <nav class="flex items-center gap-3 text-sm">
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/digital_menu']">Menu</a>
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/products']" *ngIf="isLogged()">Products</a>
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/settings']" *ngIf="isLogged()">Settings</a>
          <a class="hover:text-[var(--luxury-gold)]" [routerLink]="['/login']" *ngIf="!isLogged()">Login</a>
          <button class="text-red-300 hover:text-red-400" *ngIf="isLogged()" (click)="logout()">Logout</button>
        </nav>
      </div>
    </header>
    <main class="flex-1">
      <router-outlet></router-outlet>
    </main>
    <footer class="py-6 text-center text-white/50 text-xs">© {{year}} Digital Menu</footer>
  </div>
  <app-toast></app-toast>
  `
})
export class AppComponent {
  private auth = inject(AuthService);
  year = new Date().getFullYear();

  isLogged() { return this.auth.isAuthenticated(); }
  logout() { this.auth.logout(); }
}

