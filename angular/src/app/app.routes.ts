import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';
import { roleGuard } from './core/role.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./pages/login.component').then(m => m.LoginComponent) },
  { path: 'restaurant', canActivate: [authGuard, roleGuard('admin')], loadComponent: () => import('./pages/restaurant-list.component').then(m => m.RestaurantListComponent) },
  { path: 'restaurant/:slug/edit', canActivate: [authGuard, roleGuard('any')], loadComponent: () => import('./pages/restaurant-workspace.component').then(m => m.RestaurantWorkspaceComponent) },
  // Legacy routes redirected per spec
  { path: 'settings', redirectTo: 'restaurant', pathMatch: 'full' },
  { path: 'products', redirectTo: 'restaurant', pathMatch: 'full' },
  { path: 'digital_menu', redirectTo: 'restaurant', pathMatch: 'full' },
  // Public digital menu route
  { path: ':slug', loadComponent: () => import('./pages/digital-menu.component').then(m => m.DigitalMenuComponent) },
  { path: '**', redirectTo: 'login' }
];

