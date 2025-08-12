import { Injectable, signal } from '@angular/core';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  toasts = signal<ToastItem[]>([]);
  private counter = 0;

  private push(message: string, type: ToastType) {
    const id = ++this.counter;
    const list = this.toasts();
    this.toasts.set([...list, { id, message, type }]);
    setTimeout(() => this.dismiss(id), 3000);
  }

  dismiss(id: number) { this.toasts.update(list => list.filter(t => t.id !== id)); }

  success(msg: string) { this.push(msg, 'success'); }
  error(msg: string) { this.push(msg, 'error'); }
  info(msg: string) { this.push(msg, 'info'); }
}

