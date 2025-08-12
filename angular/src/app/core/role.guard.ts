import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';

export function roleGuard(required: 'admin' | 'manager' | 'any'): CanActivateFn {
  return (route, state) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const principal = auth.getPrincipal();
    if (!principal) { router.navigate(['/login']); return false; }
    if (required === 'any') {
      // Managers can only access their own slug workspace
      if (principal.role === 'manager') {
        const requestedSlug = route.params?.['slug'];
        if (requestedSlug && principal.restaurant_slug === requestedSlug) return true;
        router.navigate(['/restaurant']);
        return false;
      }
      return true;
    }
    if (principal.role !== required) { router.navigate(['/restaurant']); return false; }
    return true;
  };
}


