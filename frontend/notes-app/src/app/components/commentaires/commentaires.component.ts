import { Component, Input, OnInit } from '@angular/core';
import { CommentaireService, Commentaire } from '../../services/commentaire.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-commentaires',
  templateUrl: './commentaires.component.html',
  styleUrls: ['./commentaires.component.css']
})
export class CommentairesComponent implements OnInit {
  @Input() noteId!: number;
  commentaires: Commentaire[] = [];
  newComment: { contenu: string } = { contenu: '' };
  errorMessage = '';

  constructor(private api: CommentaireService, private auth: AuthService) {}

  ngOnInit(): void {
    this.loadCommentaires();
  }

  // Charger les commentaires depuis le backend
  loadCommentaires(): void {
    if (!this.noteId) return;
    this.api.getCommentaires(this.noteId).subscribe({
      next: data => this.commentaires = data,
      error: err => console.error('Erreur chargement commentaires:', err)
    });
  }

  // Ajouter un commentaire
  addComment(): void {
    this.errorMessage = '';

    // Vérifier le contenu
    if (!this.newComment.contenu.trim()) {
      this.errorMessage = 'Veuillez écrire un commentaire.';
      return;
    }

    // Vérifier que l'utilisateur est connecté
    const userId = this.auth.getUserId();
    if (!userId) {
      this.errorMessage = 'Vous devez être connecté pour commenter.';
      return;
    }

    // Préparer le payload TS-safe
    const payload: Commentaire = {
      contenu: this.newComment.contenu,
      auteur_id: userId,
      note_id: this.noteId
    };

    // Envoyer au backend
    this.api.createCommentaire(this.noteId, payload).subscribe({
      next: c => {
        this.commentaires.push(c);  // ajouter à la liste
        this.newComment.contenu = ''; // reset champ
      },
      error: err => {
        console.error(err);
        this.errorMessage = 'Impossible de poster le commentaire.';
      }
    });
  }
}
