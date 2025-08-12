import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private base = environment.api;

  // Admin restaurants
  listRestaurants() { return this.http.get(`${this.base}/admin/restaurants`); }
  createRestaurant(data: any) { return this.http.post(`${this.base}/admin/restaurants`, data); }
  getRestaurant(idOrSlug: string) { return this.http.get(`${this.base}/admin/restaurants/${idOrSlug}`); }
  updateRestaurant(idOrSlug: string, data: any) { return this.http.put(`${this.base}/admin/restaurants/${idOrSlug}`, data); }
  deleteRestaurant(idOrSlug: string) { return this.http.delete(`${this.base}/admin/restaurants/${idOrSlug}`); }
  toggleRestaurant(idOrSlug: string) { return this.http.post(`${this.base}/admin/restaurants/${idOrSlug}/toggle-active`, {}); }

  // Scoped settings
  getSettings(slug: string) { return this.http.get(`${this.base}/restaurants/${slug}/settings`); }
  saveSettings(slug: string, data: any) { return this.http.post(`${this.base}/restaurants/${slug}/settings`, data); }
  uploadLogo(slug: string, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/restaurants/${slug}/settings/logo`, fd); }
  uploadBarcode(slug: string, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/restaurants/${slug}/settings/barcode_image`, fd); }

  listCategories(slug: string) { return this.http.get(`${this.base}/restaurants/${slug}/categories`); }
  createCategory(slug: string, data: any) { return this.http.post(`${this.base}/restaurants/${slug}/categories`, data); }
  updateCategory(slug: string, id: number, data: any) { return this.http.put(`${this.base}/restaurants/${slug}/categories/${id}`, data); }
  deleteCategory(slug: string, id: number) { return this.http.delete(`${this.base}/restaurants/${slug}/categories/${id}`); }
  uploadCategoryImage(slug: string, id: number, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/restaurants/${slug}/categories/${id}/image`, fd); }

  listIngredients(slug: string) { return this.http.get(`${this.base}/restaurants/${slug}/ingredients`); }
  createIngredient(slug: string, data: any) { return this.http.post(`${this.base}/restaurants/${slug}/ingredients`, data); }
  updateIngredient(slug: string, id: number, data: any) { return this.http.put(`${this.base}/restaurants/${slug}/ingredients/${id}`, data); }
  deleteIngredient(slug: string, id: number) { return this.http.delete(`${this.base}/restaurants/${slug}/ingredients/${id}`); }
  uploadIngredientImage(slug: string, id: number, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/restaurants/${slug}/ingredients/${id}/image`, fd); }

  listProducts(slug: string) { return this.http.get(`${this.base}/restaurants/${slug}/products`); }
  createProduct(slug: string, data: any) { return this.http.post(`${this.base}/restaurants/${slug}/products`, data); }
  updateProduct(slug: string, id: number, data: any) { return this.http.put(`${this.base}/restaurants/${slug}/products/${id}`, data); }
  deleteProduct(slug: string, id: number) { return this.http.delete(`${this.base}/restaurants/${slug}/products/${id}`); }
  uploadProductImage(slug: string, id: number, file: File) { const fd = new FormData(); fd.append('file', file); return this.http.post(`${this.base}/restaurants/${slug}/products/${id}/image`, fd); }

  digitalMenu(slug: string) { return this.http.get(`${this.base}/public/menu/${slug}`); }
}

