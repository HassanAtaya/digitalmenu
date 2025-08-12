import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'digital_menu', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./pages/login.component').then(m => m.LoginComponent) },
  { path: 'settings', canActivate: [authGuard], loadComponent: () => import('./pages/settings.component').then(m => m.SettingsComponent) },
  { path: 'products', canActivate: [authGuard], loadComponent: () => import('./pages/products.component').then(m => m.ProductsComponent) },
  { path: 'digital_menu', loadComponent: () => import('./pages/digital-menu.component').then(m => m.DigitalMenuComponent) },
  { path: '**', redirectTo: 'digital_menu' }
];

