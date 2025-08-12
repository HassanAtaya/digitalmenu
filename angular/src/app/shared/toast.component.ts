import { Component, computed, inject } from '@angular/core';
import { NgFor, NgClass } from '@angular/common';
import { ToastService } from './toast.service';

@Component({
  standalone: true,
  selector: 'app-toast',
  imports: [NgFor, NgClass],
  template: `
  <div class="fixed top-4 right-4 z-[100] space-y-2">
    <div *ngFor="let t of toasts()" [ngClass]="{
        'bg-green-500 text-black': t.type==='success',
        'bg-red-600 text-white': t.type==='error',
        'bg-white text-black': t.type==='info'
      }" class="px-4 py-2 rounded shadow-lg min-w-[220px]">{{t.message}}</div>
  </div>
  `
})
export class ToastComponent {
  private toast = inject(ToastService);
  toasts = this.toast.toasts;
}

