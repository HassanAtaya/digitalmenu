import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../core/api.service';
import { ToastService } from '../shared/toast.service';

@Component({
  standalone: true,
  selector: 'app-restaurant-list',
  imports: [CommonModule, FormsModule],
  template: `
  <section class="max-w-6xl mx-auto p-4 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="lux-title">Restaurants</h1>
      <button class="px-4 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="openAdd()">Add Restaurant</button>
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <article class="lux-card p-4 space-y-3" *ngFor="let r of restaurants">
        <div class="flex items-center gap-3">
          <img *ngIf="r.logo_image" [src]="r.logo_image" class="h-10 w-10 rounded object-cover"/>
          <div class="min-w-0">
            <div class="font-semibold truncate">{{r.name}}</div>
            <div class="text-xs text-white/60">/{{r.slug}}</div>
          </div>
          <span class="ml-auto text-xs px-2 py-0.5 rounded-full"
            [ngClass]="{ 'bg-emerald-600/40': r.is_active, 'bg-red-600/40': !r.is_active }">
            {{r.is_active? 'Active':'Inactive'}}
          </span>
        </div>
        <div class="text-xs text-white/60">Username: <span class="text-white">{{r.username || '—'}}</span></div>
        <div class="flex items-center gap-2">
          <button class="px-3 py-1 rounded bg-white/10" (click)="edit(r)">Edit</button>
          <button class="px-3 py-1 rounded bg-white/10" (click)="toggle(r)">{{r.is_active? 'Deactivate':'Activate'}}</button>
          <button class="px-3 py-1 rounded bg-red-600/60" (click)="remove(r)">Delete</button>
          <a class="ml-auto text-sm underline" target="_blank" [href]="publicUrl(r)">Open Menu</a>
          <button class="text-sm underline" (click)="copyUrl(r)">Copy URL</button>
        </div>
      </article>
    </div>

    <div class="lux-card p-4" *ngIf="showAdd">
      <h2 class="font-semibold mb-3">Add Restaurant</h2>
      <div class="grid md:grid-cols-2 gap-3">
        <label class="text-sm">Name
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.name" />
        </label>
        <label class="text-sm">Manager username
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.username" />
        </label>
        <label class="text-sm">Manager password
          <input type="password" class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="model.password" />
        </label>
        <label class="text-sm flex items-center gap-2">Active
          <input type="checkbox" [(ngModel)]="model.is_active" />
        </label>
      </div>
      <div class="mt-3 flex gap-2">
        <button class="px-4 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="create()">Create</button>
        <button class="px-4 py-2 rounded bg-white/10" (click)="showAdd=false">Cancel</button>
      </div>
    </div>
  </section>
  `
})
export class RestaurantListComponent implements OnInit {
  private api = inject(ApiService);
  private toast = inject(ToastService);
  private router = inject(Router);
  restaurants: any[] = [];
  showAdd = false;
  model: any = { name: '', username: '', password: '', is_active: true };

  ngOnInit(): void { this.reload(); }
  reload(){ this.api.listRestaurants().subscribe((r:any)=> this.restaurants = r); }
  openAdd(){ this.showAdd = true; }
  create(){ this.api.createRestaurant(this.model).subscribe({ next: (r:any)=>{ this.toast.success('Restaurant created'); this.showAdd=false; this.model={ name:'', username:'', password:'', is_active:true }; this.reload(); }, error: (e)=> this.toast.error(e.error?.detail||'Failed to create') }); }
  edit(r:any){ this.router.navigate(['/restaurant', r.slug, 'edit']); }
  toggle(r:any){ this.api.toggleRestaurant(r.slug).subscribe(()=> { r.is_active = !r.is_active; }); }
  remove(r:any){ this.api.deleteRestaurant(r.slug).subscribe({ next:()=>{ this.toast.success('Deleted'); this.reload(); }, error:(e)=> this.toast.error(e.error?.detail||'Cannot delete restaurant with existing data') }); }
  publicUrl(r:any){ return `${location.origin}/${r.slug}`; }
  copyUrl(r:any){ navigator.clipboard.writeText(this.publicUrl(r)); this.toast.success('URL copied'); }
}


