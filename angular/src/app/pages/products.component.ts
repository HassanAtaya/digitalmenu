import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { ToastService } from '../shared/toast.service';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';

@Component({
  standalone: true,
  selector: 'app-products',
  imports: [CommonModule, FormsModule, DropdownModule, MultiSelectModule],
  template: `
  <section class="max-w-7xl mx-auto p-4 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="lux-title">Product Management</h1>
      <div class="text-xs text-white/60">Create categories and ingredients, then compose products.</div>
    </div>

    <!-- Product Editor -->
    <div class="lux-card p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="font-semibold">Product Editor</h2>
        <div class="flex gap-2">
          <input type="file" class="text-xs" (change)="onProdImage($event)" [disabled]="!prodModel.id"/>
          <button class="px-4 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveProd()">{{prodModel.id? 'Update Product':'Add Product'}}</button>
          <button class="px-3 py-2 rounded bg-white/10" (click)="prodModel={ name:'', price_currency_1:0, category_ids:[], ingredient_ids:[] }">Reset</button>
        </div>
      </div>
      <div class="grid lg:grid-cols-12 gap-3 items-end">
        <label class="lg:col-span-3 text-sm text-white/70">Name
          <input class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="prodModel.name" name="prodName" placeholder="e.g. Truffle Pasta" (keydown.enter)="saveProd()"/>
        </label>
        <label class="lg:col-span-2 text-sm text-white/70">Price (C1)
          <input type="number" step="0.01" class="mt-1 w-full px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="prodModel.price_currency_1" name="prodPrice" placeholder="49.99" />
        </label>
        <div class="lg:col-span-3 dm-panel">
          <div class="text-sm text-white/70 mb-1">Categories</div>
          <p-multiSelect [options]="categories" defaultLabel="Select categories" optionLabel="name" optionValue="id" [(ngModel)]="prodModel.category_ids" name="prodCats" display="chip" [filter]="true" [showClear]="true" [appendTo]="'body'" panelStyleClass="dm-overlay"></p-multiSelect>
        </div>
        <div class="lg:col-span-4 dm-panel">
          <div class="text-sm text-white/70 mb-1">Ingredients</div>
          <p-multiSelect [options]="ingredients" defaultLabel="Select ingredients" optionLabel="name" optionValue="id" [(ngModel)]="prodModel.ingredient_ids" name="prodIngs" display="chip" [filter]="true" [showClear]="true" [appendTo]="'body'" panelStyleClass="dm-overlay"></p-multiSelect>
        </div>
      </div>
    </div>

    <!-- Product List -->
    <div class="lux-card p-5">
      <div class="flex items-center justify-between mb-3">
        <h2 class="font-semibold">Products</h2>
        <input class="px-3 py-2 rounded bg-black/40 border border-white/10 text-sm" [(ngModel)]="productSearch" placeholder="Search products" />
      </div>
      <div class="overflow-auto">
        <table class="min-w-full text-sm">
          <thead class="text-white/60">
            <tr class="border-b border-white/10">
              <th class="text-left py-2 pr-3">Product</th>
              <th class="text-left py-2 pr-3">Price</th>
              <th class="text-left py-2 pr-3">Categories</th>
              <th class="text-left py-2 pr-3">Ingredients</th>
              <th class="text-right py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let p of filteredProducts" class="border-b border-white/5 hover:bg-white/5">
              <td class="py-3 pr-3">
                <div class="flex items-center gap-3">
                  <img *ngIf="p.image_path" [src]="p.image_path" class="h-9 w-9 rounded object-cover"/>
                  <div class="font-medium">{{p.name}}</div>
                </div>
              </td>
              <td class="py-3 pr-3">{{p.price_currency_1 | number:'1.0-0'}} → {{p.price_currency_2 | number:'1.0-0'}}</td>
              <td class="py-3 pr-3">
                <div class="flex flex-wrap gap-1">
                  <span class="px-2 py-0.5 rounded-full bg-white/10" *ngFor="let cn of mapNames(p.category_ids, categories)">{{cn}}</span>
                </div>
              </td>
              <td class="py-3 pr-3">
                <div class="flex flex-wrap gap-1">
                  <span class="px-2 py-0.5 rounded-full bg-emerald-600/30" *ngFor="let iname of mapNames(p.ingredient_ids, ingredients)">{{iname}}</span>
                </div>
              </td>
              <td class="py-3 text-right space-x-2">
                <button class="text-xs px-2 py-1 bg-white/10 rounded" (click)="editProd(p)">Edit</button>
                <button class="text-xs px-2 py-1 bg-red-600/60 rounded" (click)="delProd(p.id)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Categories -->
    <div class="lux-card p-5 space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="font-semibold">Categories</h2>
        <div class="flex items-center gap-2">
          <input type="file" class="text-xs" (change)="onCatImage($event)" [disabled]="!catModel.id"/>
          <button class="px-3 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveCat()">{{catModel.id? 'Update':'Add'}}</button>
        </div>
      </div>
      <div class="grid sm:grid-cols-2 gap-3">
        <input class="px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="catModel.name" name="catName" placeholder="New category name" (keydown.enter)="saveCat()"/>
      </div>
      <div class="grid grid-cols-1 gap-2 max-h-64 overflow-auto">
        <div *ngFor="let c of filteredCategories" class="flex items-center justify-between border border-white/10 rounded p-2">
          <div class="flex items-center gap-2">
            <img *ngIf="c.image_path" [src]="c.image_path" class="h-8 w-8 rounded object-cover"/>
            <span>{{c.name}}</span>
          </div>
          <div class="space-x-2">
            <button class="text-xs px-2 py-1 bg-white/10 rounded" (click)="editCat(c)">Edit</button>
            <button class="text-xs px-2 py-1 bg-red-600/60 rounded" (click)="delCat(c.id)">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Ingredients -->
    <div class="lux-card p-5 space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="font-semibold">Ingredients</h2>
        <div class="flex items-center gap-2">
          <input type="file" class="text-xs" (change)="onIngImage($event)" [disabled]="!ingModel.id"/>
          <button class="px-3 py-2 rounded bg-[var(--luxury-gold)] text-black" (click)="saveIng()">{{ingModel.id? 'Update':'Add'}}</button>
        </div>
      </div>
      <div class="grid sm:grid-cols-2 gap-3">
        <input class="px-3 py-2 rounded bg-black/40 border border-white/10" [(ngModel)]="ingModel.name" name="ingName" placeholder="New ingredient name" (keydown.enter)="saveIng()"/>
      </div>
      <div class="grid grid-cols-1 gap-2 max-h-64 overflow-auto">
        <div *ngFor="let i of filteredIngredients" class="flex items-center justify-between border border-white/10 rounded p-2">
          <div class="flex items-center gap-2">
            <img *ngIf="i.image_path" [src]="i.image_path" class="h-8 w-8 rounded object-cover"/>
            <span>{{i.name}}</span>
          </div>
          <div class="space-x-2">
            <button class="text-xs px-2 py-1 bg-white/10 rounded" (click)="editIng(i)">Edit</button>
            <button class="text-xs px-2 py-1 bg-red-600/60 rounded" (click)="delIng(i.id)">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </section>
  `
})
export class ProductsComponent implements OnInit {
  private api = inject(ApiService);
  private toast = inject(ToastService);
  categories: any[] = []; ingredients: any[] = []; products: any[] = [];
  catModel: any = { name: '' };
  ingModel: any = { name: '' };
  prodModel: any = { name: '', price_currency_1: 0, category_ids: [], ingredient_ids: [] };
  productSearch = '';

  ngOnInit(): void { this.reload(); }
  reload() {
    this.api.listCategories().subscribe((r:any)=> this.categories = r);
    this.api.listIngredients().subscribe((r:any)=> this.ingredients = r);
    this.api.listProducts().subscribe((r:any)=> this.products = r);
  }
  editCat(c:any){ this.catModel = { id: c.id, name: c.name }; }
  saveCat(){ const op = this.catModel.id? this.api.updateCategory(this.catModel.id, {name:this.catModel.name}): this.api.createCategory({name:this.catModel.name}); op.subscribe({ next:()=>{ this.catModel={name:''}; this.reload(); this.toast.success('Category saved'); }, error:()=> this.toast.error('Failed to save category') }); }
  delCat(id:number){ this.api.deleteCategory(id).subscribe({next:()=>{ this.reload(); this.toast.success('Category deleted'); }, error:(e)=> this.toast.error(e.error?.detail||'Cannot delete')}); }
  onCatImage(e:any){ const f=e.target.files?.[0]; if(f && this.catModel.id){ this.api.uploadCategoryImage(this.catModel.id, f).subscribe(()=> this.reload()); } }

  editIng(i:any){ this.ingModel = { id: i.id, name: i.name }; }
  saveIng(){ const op = this.ingModel.id? this.api.updateIngredient(this.ingModel.id, {name:this.ingModel.name}): this.api.createIngredient({name:this.ingModel.name}); op.subscribe({ next:()=>{ this.ingModel={name:''}; this.reload(); this.toast.success('Ingredient saved'); }, error:()=> this.toast.error('Failed to save ingredient') }); }
  delIng(id:number){ this.api.deleteIngredient(id).subscribe({ next:()=>{ this.reload(); this.toast.success('Ingredient deleted'); }, error:()=> this.toast.error('Failed to delete ingredient') }); }
  onIngImage(e:any){ const f=e.target.files?.[0]; if(f && this.ingModel.id){ this.api.uploadIngredientImage(this.ingModel.id, f).subscribe(()=> this.reload()); } }

  editProd(p:any){ this.prodModel = { id:p.id, name:p.name, price_currency_1:p.price_currency_1, category_ids:p.category_ids||[], ingredient_ids:p.ingredient_ids||[] } }
  saveProd(){ const data = { name:this.prodModel.name, price_currency_1:+this.prodModel.price_currency_1, category_ids:this.prodModel.category_ids||[], ingredient_ids:this.prodModel.ingredient_ids||[] };
    const op = this.prodModel.id? this.api.updateProduct(this.prodModel.id, data): this.api.createProduct(data);
    op.subscribe({ next:()=>{ this.prodModel={ name:'', price_currency_1:0, category_ids:[], ingredient_ids:[] }; this.reload(); this.toast.success('Product saved'); }, error:()=> this.toast.error('Failed to save product') }); }
  delProd(id:number){ this.api.deleteProduct(id).subscribe({ next:()=>{ this.reload(); this.toast.success('Product deleted'); }, error:()=> this.toast.error('Failed to delete product') }); }
  mapNames(ids:number[], list:any[]): string[] { const set = new Set(ids||[]); return (list||[]).filter(x=> set.has(x.id)).map(x=> x.name); }

  get filteredProducts(){ const q=(this.productSearch||'').toLowerCase(); return this.products.filter((p:any)=> !q || p.name.toLowerCase().includes(q)); }
  get filteredCategories(){ return this.categories; }
  get filteredIngredients(){ return this.ingredients; }
  onProdImage(e:any){ const f=e.target.files?.[0]; if(f && this.prodModel.id){ this.api.uploadProductImage(this.prodModel.id, f).subscribe(()=> this.reload()); } }
}

