import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css']
})
export class ToastComponent {
  @Input() message = '';
  @Input() type: 'success' | 'error' = 'success';
  isVisible = false;

  show(message: string, type: 'success' | 'error' = 'success') {
    this.message = message;
    this.type = type;
    this.isVisible = true;
    setTimeout(() => this.isVisible = false, 3000); // disparaît après 3s
  }
}

