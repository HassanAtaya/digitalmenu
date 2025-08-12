import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { ToastService } from '../shared/toast.service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [CommonModule, FormsModule],
  template: `
  <section class="max-w-md mx-auto px-4 pt-16">
    <div class="lux-card p-6">
      <h1 class="lux-title mb-6">Sign In</h1>
      <form (ngSubmit)="submit()" class="space-y-4" (keydown.enter)="submit()">
        <div>
          <label class="block mb-1 text-sm text-white/70">Username</label>
          <input class="w-full px-3 py-2 rounded bg-black/40 border border-white/10 focus:outline-none" [(ngModel)]="username" name="username" />
        </div>
        <div>
          <label class="block mb-1 text-sm text-white/70">Password</label>
          <input type="password" class="w-full px-3 py-2 rounded bg-black/40 border border-white/10 focus:outline-none" [(ngModel)]="password" name="password" />
        </div>
        <button class="w-full py-2 rounded bg-[var(--luxury-gold)] text-black font-semibold hover:opacity-90">Login</button>
      </form>
    </div>
  </section>
  `
})
export class LoginComponent {
  username = '';
  password = '';
  private auth = inject(AuthService);
  private router = inject(Router);
  private toast = inject(ToastService);

  submit() {
    this.auth.login(this.username, this.password).subscribe({
      next: (res) => {
        this.auth.setToken(res.access_token);
        const p = this.auth.getPrincipal();
        this.toast.success('Welcome back');
        if (p?.role === 'admin') {
          this.router.navigate(['/restaurant']);
        } else if (p?.role === 'manager' && p.restaurant_slug) {
          this.router.navigate(['/restaurant', p.restaurant_slug, 'edit']);
        } else {
          this.router.navigate(['/login']);
        }
      },
      error: () => this.toast.error('Invalid credentials')
    });
  }
}

