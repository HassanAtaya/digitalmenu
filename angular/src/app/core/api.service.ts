import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private base = environment.api;

  getSettings() { return this.http.get(`${this.base}/settings`); }
  saveSettings(data: any) { return this.http.post(`${this.base}/settings`, data); }
  uploadLogo(file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/settings/logo`, fd); }
  uploadBarcode(file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/settings/barcode_image`, fd); }

  listCategories() { return this.http.get(`${this.base}/categories`); }
  createCategory(data: any) { return this.http.post(`${this.base}/categories`, data); }
  updateCategory(id: number, data: any) { return this.http.put(`${this.base}/categories/${id}`, data); }
  deleteCategory(id: number) { return this.http.delete(`${this.base}/categories/${id}`); }
  uploadCategoryImage(id: number, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/categories/${id}/image`, fd); }

  listIngredients() { return this.http.get(`${this.base}/ingredients`); }
  createIngredient(data: any) { return this.http.post(`${this.base}/ingredients`, data); }
  updateIngredient(id: number, data: any) { return this.http.put(`${this.base}/ingredients/${id}`, data); }
  deleteIngredient(id: number) { return this.http.delete(`${this.base}/ingredients/${id}`); }
  uploadIngredientImage(id: number, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/ingredients/${id}/image`, fd); }

  listProducts() { return this.http.get(`${this.base}/products`); }
  createProduct(data: any) { return this.http.post(`${this.base}/products`, data); }
  updateProduct(id: number, data: any) { return this.http.put(`${this.base}/products/${id}`, data); }
  deleteProduct(id: number) { return this.http.delete(`${this.base}/products/${id}`); }
  uploadProductImage(id: number, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/products/${id}/image`, fd); }

  digitalMenu() { return this.http.get(`${this.base}/digital_menu`); }
}

