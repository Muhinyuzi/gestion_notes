import { Component, OnInit } from '@angular/core';
import { ToastService } from '../../../services/toast.service';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css']
})
export class ToastComponent implements OnInit {
  message = '';
  type: 'success' | 'error' | 'info' = 'success';
  isVisible = false;

  constructor(private toastService: ToastService) {}

  ngOnInit(): void {
    this.toastService.toastState$.subscribe(({ message, type }) => {
      this.message = message;
      this.type = type;
      this.isVisible = true;
      setTimeout(() => this.isVisible = false, 3000);
    });
  }
}
