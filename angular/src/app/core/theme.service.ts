import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private api = inject(ApiService);

  async load(): Promise<void> {
    try {
      const settings: any = await firstValueFrom(this.api.getSettings());
      this.apply(settings);
    } catch {
      // ignore theme load errors
    }
  }

  apply(settings: any) {
    if (settings?.primary_color) {
      document.documentElement.style.setProperty('--luxury-gold', settings.primary_color);
    }
    if (settings?.background_color) {
      document.documentElement.style.setProperty('--luxury-dark', settings.background_color);
      document.body.style.background = settings.background_color;
    }
  }
}

