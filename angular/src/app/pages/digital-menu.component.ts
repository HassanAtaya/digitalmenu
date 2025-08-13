import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../core/api.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-digital-menu',
  imports: [CommonModule],
  template: `
  <section class="w-full p-4 md:p-6 min-h-screen">
    <div *ngIf="unavailable" class="max-w-xl mx-auto text-center py-16">
      <h1 class="lux-title mb-2">Temporarily Unavailable</h1>
      <p class="text-white/70">{{message}}</p>
    </div>
    <ng-container *ngIf="!unavailable">
    <div class="max-w-6xl mx-auto mb-4 border-b border-white/10">
      <div class="grid grid-cols-3 items-center py-3">
        <div class="justify-self-start">
          <img *ngIf="data?.setting?.logo_path" [src]="data?.setting?.logo_path" class="h-10 object-contain"/>
        </div>
        <div class="justify-self-center text-center">
          <div class="lux-title truncate">{{data?.setting?.company_name}}</div>
          <div class="text-xs text-white/70">{{data?.setting?.currency_1}} / {{data?.setting?.currency_2}}</div>
        </div>
        <div class="justify-self-end">
          <img *ngIf="data?.setting?.barcode_image_path" [src]="data?.setting?.barcode_image_path" class="h-12 object-contain"/>
        </div>
      </div>
    </div>

    <div class="overflow-x-auto mb-5">
      <div class="flex gap-3 min-w-max">
        <button class="px-4 py-2 rounded-full border border-white/10" [style.background]="active===0? (data?.setting?.primary_color || '#C9A24B') : 'transparent'" [class.text-black]="active===0" (click)="active=0">All</button>
        <button *ngFor="let c of data?.categories" class="px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2"
          [style.background]="active===c.id? (data?.setting?.primary_color || '#C9A24B') : 'transparent'" [class.text-black]="active===c.id"
          (click)="active=c.id">
          <img *ngIf="c.image_path" [src]="c.image_path" class="h-6 w-6 rounded object-cover"/>
          <span>{{c.name}}</span>
        </button>
      </div>
    </div>

    <div *ngFor="let cat of data?.categories" class="mb-8" [hidden]="active && active!==cat.id && active!==0">
      <div class="flex items-center gap-3 mb-3">
        <img *ngIf="cat.image_path" [src]="cat.image_path" class="h-10 w-10 rounded object-cover"/>
        <h2 class="text-xl font-display" [style.color]="data?.setting?.primary_color || '#C9A24B'">{{cat.name}}</h2>
      </div>
      <div class="overflow-x-auto pb-2">
        <div class="flex gap-3 min-w-max">
          <article *ngFor="let p of cat.products" class="lux-card overflow-hidden w-44 h-56 flex-shrink-0 hover:scale-[1.01] transition">
            <ng-container *ngIf="p.image_path; else placeholderImage">
              <img [src]="p.image_path" class="w-full h-28 object-cover"/>
            </ng-container>
            <ng-template #placeholderImage>
              <div class="w-full h-28 bg-white/5"></div>
            </ng-template>
            <div class="p-3">
              <div class="min-w-0">
                <h3 class="font-semibold text-base truncate">{{p.name}}</h3>
                <div class="text-white/60 text-xs">{{p.price_currency_1 | number:'1.0-0'}} {{data?.setting?.currency_1}} / {{p.price_currency_2 | number:'1.0-0'}} {{data?.setting?.currency_2}}</div>
              </div>
              <div class="mt-1 text-xs text-white/70 overflow-hidden text-ellipsis whitespace-nowrap" *ngIf="p.ingredient_names?.length">Ingredients: {{p.ingredient_names.join(', ')}}</div>
            </div>
          </article>
        </div>
      </div>
    </div>
    </ng-container>
  </section>
  `
})
export class DigitalMenuComponent implements OnInit {
  private api = inject(ApiService);
  private route = inject(ActivatedRoute);
  data: any; active = 0; unavailable = false; message = '';
  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug')!;
    this.api.digitalMenu(slug).subscribe((r: any) => {
      if (r?.unavailable) { this.unavailable = true; this.message = r.message || 'Temporarily unavailable'; }
      this.data = r;
      this.applyTheme();
    });
  }

  applyTheme(){
    const s = this.data?.setting;
    if (s?.primary_color) document.documentElement.style.setProperty('--luxury-gold', s.primary_color);
    if (s?.background_color) { document.documentElement.style.setProperty('--luxury-dark', s.background_color); document.body.style.background = s.background_color; }
  }
}

