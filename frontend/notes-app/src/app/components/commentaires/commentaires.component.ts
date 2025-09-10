import { Component, Input, OnInit } from '@angular/core';
import { ApiService, Commentaire } from '../../services/api.service';

@Component({
  selector: 'app-commentaires',
  templateUrl: './commentaires.component.html',
  styleUrls: ['./commentaires.component.css']
})
export class CommentairesComponent implements OnInit {
  @Input() noteId!: number; // vient de NotesComponent
  commentaires: Commentaire[] = [];
  newComment: Commentaire = { contenu: '', auteur_id: 1, note_id: 0 };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadCommentaires();
  }

  // Charger les commentaires de la note
  loadCommentaires(): void {
    if (!this.noteId) return;
    this.api.getCommentaires(this.noteId).subscribe(data => this.commentaires = data);
  }

  // Ajouter un commentaire
  addComment(): void {
    if (!this.newComment.contenu) {
      alert('Veuillez écrire un commentaire.');
      return;
    }

    this.newComment.note_id = this.noteId;
    this.api.createCommentaire(this.noteId, this.newComment).subscribe(c => {
      this.commentaires.push(c);
      this.newComment = { contenu: '', auteur_id: 1, note_id: this.noteId }; // reset
    });
  }
}
