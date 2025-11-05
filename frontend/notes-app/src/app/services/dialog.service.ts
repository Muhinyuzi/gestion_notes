import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../components/shared/confirm-dialog/confirm-dialog.component';

@Injectable({ providedIn: 'root' })
export class DialogService {
  constructor(private dialog: MatDialog) {}

  confirm(title: string, message: string) {
    return this.dialog.open(ConfirmDialogComponent, {
      width: '380px',
      data: { title, message }
    }).afterClosed();
  }
}