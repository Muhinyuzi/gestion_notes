import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-email-sent',
  templateUrl: './email-sent.component.html',
  styleUrls: ['./email-sent.component.css']
})
export class EmailSentComponent {
  email: string | null = null;

  constructor(private route: ActivatedRoute) {
    this.email = this.route.snapshot.queryParamMap.get('email');
  }
}