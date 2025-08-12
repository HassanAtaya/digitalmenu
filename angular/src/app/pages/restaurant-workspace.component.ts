import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../core/api.service';
import { ToastService } from '../shared/toast.service';

@Component({
  standalone: true,
  selector: 'app-restaurant-workspace',
  imports: [CommonModule, FormsModule],
  template: `
  <section class="max-w-7xl mx-auto p-4 space-y-6" *ngIf="slug">
    <div class="flex items-center justify-between">
      <h1 class="lux-title">Workspace — {{settings?.company_name || slug}}</h1>
      <div class="flex items-center gap-2">
        <a class="px-3 py-2 rounded bg-white/10" target="_blank" [href]="publicUrl()">Open Menu</a>
        <button class="px-3 py-2 rounded bg-white/10" (click)="copyUrl()">Copy Public URL</button>
      </div>
    </div>

    <div class="lux-card p-4">
      <div class="flex gap-2 text-sm">
        <button class="px-3 py-2 rounded" [ngClass]="{ 'bg-white/10': tab==='settings' }" (click)="tab='settings'">Settings</button>
        <button class="px-3 py-2 rounded" [ngClass]="{ 'bg-white/10': tab==='categories' }" (click)="tab='categories'">Categories</button>
        <button class="px-3 py-2 rounded" [ngClass]="{ 'bg-white/10': tab==='products' }" (click)="tab='products'">Products</button>
        <button class="px-3 py-2 rounded" [ngClass]="{ 'bg-white/10': tab==='ingredients' }" (click)="tab='ingredients'">Ingredients</button>
      </div>
    </div>

    <!-- Settings -->
    <div class="lux-card p-4" *ngIf="tab==='settings'">
      <div class="grid md:grid-cols-2 gap-4">
        <label class="text-sm">Company Name
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.company_name" />
        </label>
        <label class="text-sm">Currency 1
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.currency_1" />
        </label>
        <label class="text-sm">Currency 2
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.currency_2" />
        </label>
        <label class="text-sm">Rate (1→2)
          <input type="number" step="0.01" class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.rate" />
        </label>
        <label class="text-sm">Primary Color
          <input type="color" class="mt-1 w-full h-10 rounded" [(ngModel)]="settings.primary_color" />
        </label>
        <label class="text-sm">Background Color
          <input type="color" class="mt-1 w-full h-10 rounded" [(ngModel)]="settings.background_color" />
        </label>
        <label class="text-sm">Barcode URL
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.barcode_url" />
        </label>
        <div class="grid md:grid-cols-2 gap-4">
          <label class="text-sm">Manager Username
            <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.manager_username" />
          </label>
          <label class="text-sm">Manager Password
            <input type="password" class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="settings.manager_password" />
          </label>
        </div>
      </div>
      <div class="grid md:grid-cols-2 gap-4 mt-3">
        <div>
          <div class="mb-2 font-medium">Logo</div>
          <input type="file" (change)="onLogo($event)"/>
          <img *ngIf="settings.logo_path" [src]="settings.logo_path" class="max-h-36 mt-2"/>
        </div>
        <div>
          <div class="mb-2 font-medium">Barcode Image</div>
          <input type="file" (change)="onBarcode($event)"/>
          <img *ngIf="settings.barcode_image_path" [src]="settings.barcode_image_path" class="max-h-36 mt-2"/>
        </div>
      </div>
      <button class="mt-3 px-4 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveSettings()">Save</button>
    </div>

    <!-- Categories -->
    <div class="lux-card p-4 space-y-3" *ngIf="tab==='categories'">
      <div class="flex items-center gap-2">
        <input class="px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="catModel.name" placeholder="Category name"/>
        <button class="px-3 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveCategory()">{{catModel.id? 'Update':'Add'}}</button>
        <input type="file" (change)="onCategoryImage($event)" [disabled]="!catModel.id"/>
      </div>
      <div class="grid md:grid-cols-2 gap-2">
        <div class="flex items-center justify-between border border-white/10 rounded p-2" *ngFor="let c of categories">
          <div class="flex items-center gap-2">
            <img *ngIf="c.image_path" [src]="c.image_path" class="h-8 w-8 rounded object-cover"/>
            <span>{{c.name}}</span>
          </div>
          <div class="space-x-2">
            <button class="text-xs px-2 py-1 bg-white/10 rounded" (click)="catModel={id:c.id,name:c.name}">Edit</button>
            <button class="text-xs px-2 py-1 bg-red-600/60 rounded" (click)="deleteCategory(c)">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Products -->
    <div class="lux-card p-4 space-y-3" *ngIf="tab==='products'">
      <div class="grid lg:grid-cols-12 gap-3 items-end">
        <label class="lg:col-span-3 text-sm">Name
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="prodModel.name"/>
        </label>
        <label class="lg:col-span-3 text-sm">Price (C1)
          <input type="number" step="0.01" class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="prodModel.price_currency_1"/>
        </label>
        <label class="lg:col-span-3 text-sm">Categories
          <select class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="prodModel.category_ids" multiple>
            <option *ngFor="let c of categories" [value]="c.id">{{c.name}}</option>
          </select>
        </label>
        <label class="lg:col-span-3 text-sm">Ingredients
          <select class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="prodModel.ingredient_ids" multiple>
            <option *ngFor="let i of ingredients" [value]="i.id">{{i.name}}</option>
          </select>
        </label>
      </div>
      <div class="flex items-center gap-2">
        <button class="px-3 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveProduct()">{{prodModel.id? 'Update':'Add'}} product</button>
        <input type="file" (change)="onProductImage($event)" [disabled]="!prodModel.id"/>
      </div>
      <div class="overflow-auto">
        <table class="min-w-full text-sm">
          <thead class="text-white/60">
            <tr class="border-b border-white/10"><th class="text-left py-2 pr-3">Product</th><th class="text-left py-2 pr-3">Price</th><th class="text-left py-2 pr-3">Categories</th><th></th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let p of products" class="border-b border-white/5">
              <td class="py-2 pr-3 flex items-center gap-2"><img *ngIf="p.image_path" [src]="p.image_path" class="h-8 w-8 rounded object-cover"/>{{p.name}}</td>
              <td class="py-2 pr-3">{{p.price_currency_1 | number:'1.0-2'}}</td>
              <td class="py-2 pr-3">{{mapNames(p.category_ids, categories).join(', ')}}</td>
              <td class="py-2 text-right space-x-2"><button class="text-xs px-2 py-1 bg-white/10 rounded" (click)="editProduct(p)">Edit</button><button class="text-xs px-2 py-1 bg-red-600/60 rounded" (click)="deleteProduct(p)">Delete</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Ingredients -->
    <div class="lux-card p-4 space-y-3" *ngIf="tab==='ingredients'">
      <div class="flex items-center gap-2">
        <input class="px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="ingModel.name" placeholder="Ingredient name"/>
        <button class="px-3 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveIngredient()">{{ingModel.id? 'Update':'Add'}}</button>
        <input type="file" (change)="onIngredientImage($event)" [disabled]="!ingModel.id"/>
      </div>
      <div class="grid md:grid-cols-2 gap-2">
        <div class="flex items-center justify-between border border-white/10 rounded p-2" *ngFor="let i of ingredients">
          <div class="flex items-center gap-2"><img *ngIf="i.image_path" [src]="i.image_path" class="h-8 w-8 rounded object-cover"/>{{i.name}}</div>
          <div class="space-x-2"><button class="text-xs px-2 py-1 bg-white/10 rounded" (click)="ingModel={id:i.id,name:i.name}">Edit</button><button class="text-xs px-2 py-1 bg-red-600/60 rounded" (click)="deleteIngredient(i)">Delete</button></div>
        </div>
      </div>
    </div>

  </section>
  `
})
export class RestaurantWorkspaceComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private api = inject(ApiService);
  private toast = inject(ToastService);
  slug!: string;
  tab: 'settings'|'categories'|'products'|'ingredients' = 'settings';
  settings: any = { company_name: '', currency_1: 'USD', currency_2: 'EUR', rate: 1.0 };
  categories: any[] = [];
  ingredients: any[] = [];
  products: any[] = [];
  catModel: any = { name: '' };
  ingModel: any = { name: '' };
  prodModel: any = { name: '', price_currency_1: 0, category_ids: [], ingredient_ids: [] };

  ngOnInit(): void { this.slug = this.route.snapshot.paramMap.get('slug')!; this.reloadAll(); }
  reloadAll(){ this.api.getSettings(this.slug).subscribe((r:any)=> this.settings=r); this.reloadTaxonomies(); this.reloadProducts(); }
  reloadTaxonomies(){ this.api.listCategories(this.slug).subscribe((r:any)=> this.categories=r); this.api.listIngredients(this.slug).subscribe((r:any)=> this.ingredients=r); }
  reloadProducts(){ this.api.listProducts(this.slug).subscribe((r:any)=> this.products=r); }

  // Settings
  saveSettings(){ this.api.saveSettings(this.slug, this.settings).subscribe((r:any)=>{ this.settings=r; this.toast.success('Settings saved'); }); }
  onLogo(e:any){ const f=e.target.files?.[0]; if(f) this.api.uploadLogo(this.slug, f).subscribe((r:any)=>{ this.settings=r; this.toast.success('Logo updated'); }); }
  onBarcode(e:any){ const f=e.target.files?.[0]; if(f) this.api.uploadBarcode(this.slug, f).subscribe((r:any)=>{ this.settings=r; this.toast.success('Barcode updated'); }); }

  // Categories
  saveCategory(){ const op = this.catModel.id? this.api.updateCategory(this.slug, this.catModel.id, {name:this.catModel.name}): this.api.createCategory(this.slug, {name:this.catModel.name}); op.subscribe({ next:()=>{ this.catModel={name:''}; this.reloadTaxonomies(); this.toast.success('Category saved'); }, error:(e)=> this.toast.error(e.error?.detail||'Failed') }); }
  deleteCategory(c:any){ this.api.deleteCategory(this.slug, c.id).subscribe({ next:()=>{ this.reloadTaxonomies(); this.toast.success('Category deleted'); }, error:(e)=> this.toast.error(e.error?.detail||'Cannot delete category with products') }); }
  onCategoryImage(e:any){ const f=e.target.files?.[0]; if(f && this.catModel.id) this.api.uploadCategoryImage(this.slug, this.catModel.id, f).subscribe(()=> this.reloadTaxonomies()); }

  // Ingredients
  saveIngredient(){ const op = this.ingModel.id? this.api.updateIngredient(this.slug, this.ingModel.id, {name:this.ingModel.name}): this.api.createIngredient(this.slug, {name:this.ingModel.name}); op.subscribe({ next:()=>{ this.ingModel={name:''}; this.reloadTaxonomies(); this.toast.success('Ingredient saved'); }, error:()=> this.toast.error('Failed') }); }
  deleteIngredient(i:any){ this.api.deleteIngredient(this.slug, i.id).subscribe({ next:()=>{ this.reloadTaxonomies(); this.toast.success('Ingredient deleted'); }, error:()=> this.toast.error('Failed') }); }
  onIngredientImage(e:any){ const f=e.target.files?.[0]; if(f && this.ingModel.id) this.api.uploadIngredientImage(this.slug, this.ingModel.id, f).subscribe(()=> this.reloadTaxonomies()); }

  // Products
  editProduct(p:any){ this.prodModel = { id:p.id, name:p.name, price_currency_1:p.price_currency_1, category_ids:p.category_ids||[], ingredient_ids:p.ingredient_ids||[] }; }
  saveProduct(){ const data = { name:this.prodModel.name, price_currency_1:+this.prodModel.price_currency_1, category_ids:this.prodModel.category_ids||[], ingredient_ids:this.prodModel.ingredient_ids||[] };
    const op = this.prodModel.id? this.api.updateProduct(this.slug, this.prodModel.id, data): this.api.createProduct(this.slug, data);
    op.subscribe({ next:()=>{ this.prodModel={ name:'', price_currency_1:0, category_ids:[], ingredient_ids:[] }; this.reloadProducts(); this.toast.success('Product saved'); }, error:()=> this.toast.error('Failed') }); }
  deleteProduct(p:any){ this.api.deleteProduct(this.slug, p.id).subscribe({ next:()=>{ this.reloadProducts(); this.toast.success('Product deleted'); }, error:()=> this.toast.error('Failed') }); }
  onProductImage(e:any){ const f=e.target.files?.[0]; if(f && this.prodModel.id) this.api.uploadProductImage(this.slug, this.prodModel.id, f).subscribe(()=> this.reloadProducts()); }

  mapNames(ids:number[], list:any[]): string[] { const set = new Set(ids||[]); return (list||[]).filter(x=> set.has(x.id)).map(x=> x.name); }
  publicUrl(){ return `${location.origin}/${this.slug}`; }
  copyUrl(){ navigator.clipboard.writeText(this.publicUrl()); this.toast.success('URL copied'); }
}


