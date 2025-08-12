import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { ToastService } from '../shared/toast.service';

@Component({
  standalone: true,
  selector: 'app-settings',
  imports: [CommonModule, FormsModule],
  template: `
  <section class="max-w-4xl mx-auto p-4">
    <h1 class="lux-title mb-6">Settings</h1>
    <div class="grid md:grid-cols-2 gap-6">
      <div class="lux-card p-4 space-y-3">
        <label class="block">Company Name
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.company_name" />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">Currency 1
            <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.currency_1" />
          </label>
          <label class="block">Currency 2
            <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.currency_2" />
          </label>
        </div>
        <label class="block">Rate
          <input type="number" step="0.01" class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.rate" />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">Primary Color
            <input type="color" class="mt-1 w-full h-10 rounded" [(ngModel)]="model.primary_color" (change)="applyTheme()" />
          </label>
          <label class="block">Background Color
            <input type="color" class="mt-1 w-full h-10 rounded" [(ngModel)]="model.background_color" (change)="applyTheme()" />
          </label>
        </div>
        <label class="block">Barcode URL
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.barcode_url" />
        </label>
        <button class="mt-2 px-4 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="save()">Save</button>
      </div>
      <div class="space-y-6">
        <div class="lux-card p-4">
          <div class="flex items-center justify-between mb-3"><h2 class="font-semibold">Logo</h2>
            <input type="file" (change)="onLogo($event)" />
          </div>
          <img *ngIf="model.logo_path" [src]="model.logo_path" class="max-h-40 mx-auto"/>
        </div>
        <div class="lux-card p-4">
          <div class="flex items-center justify-between mb-3"><h2 class="font-semibold">Barcode Image</h2>
            <input type="file" (change)="onBarcode($event)" />
          </div>
          <img *ngIf="model.barcode_image_path" [src]="model.barcode_image_path" class="max-h-40 mx-auto"/>
        </div>
      </div>
    </div>
  </section>
  `
})
export class SettingsComponent implements OnInit {
  private api = inject(ApiService);
  private toast = inject(ToastService);
  model: any = { company_name: '', currency_1: 'USD', currency_2: 'EUR', rate: 1.0 };

  ngOnInit(): void { this.api.getSettings().subscribe(res => this.model = res); }
  save() { this.api.saveSettings(this.model).subscribe(res => { this.model = res; this.applyTheme(); this.toast.success('Settings saved'); }); }
  onLogo(e: any) { const f = e.target.files?.[0]; if (f) this.api.uploadLogo(f).subscribe(res => { this.model = res; this.toast.success('Logo updated'); }); }
  onBarcode(e: any) { const f = e.target.files?.[0]; if (f) this.api.uploadBarcode(f).subscribe(res => { this.model = res; this.toast.success('Barcode updated'); }); }
  applyTheme(){
    if (this.model?.primary_color) document.documentElement.style.setProperty('--luxury-gold', this.model.primary_color);
    if (this.model?.background_color) document.body.style.background = this.model.background_color;
  }
}

