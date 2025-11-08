import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private toastState = new Subject<{ message: string; type: 'success' | 'error' | 'info' }>();

  toastState$ = this.toastState.asObservable();

  show(message: string, type: 'success' | 'error' | 'info' = 'success') {
    this.toastState.next({ message, type });
  }
}