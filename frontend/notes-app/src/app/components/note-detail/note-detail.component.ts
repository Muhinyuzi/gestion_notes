import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService, Note } from '../../services/api.service';

@Component({
  selector: 'app-note-detail',
  templateUrl: './note-detail.component.html',
  styleUrls: ['./note-detail.component.css']
})
export class NoteDetailComponent implements OnInit {
  note?: Note;
  isLoading = true;
  errorMessage = '';

  constructor(private route: ActivatedRoute, private api: ApiService) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.api.getNoteById(id).subscribe({
      next: (data) => {
        this.note = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "Impossible de charger la note.";
        this.isLoading = false;
      }
    });
  }
}