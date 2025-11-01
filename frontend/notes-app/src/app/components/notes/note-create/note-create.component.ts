import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NoteService, NoteCreate, Note, Utilisateur } from '../../../services/note.service';
import { AuthService } from '../../../services/auth.service';
import { KENDO_EDITOR } from '@progress/kendo-angular-editor';
import DOMPurify from 'dompurify';

@Component({
  selector: 'app-note-create',
  templateUrl: './note-create.component.html',
  styleUrls: ['./note-create.component.css']
})
export class NoteCreateComponent implements OnInit {

  newNote: NoteCreate = {
    titre: '',
    contenu: '',
    equipe: '',
    auteur_id: 0,
    categorie: '',
    priorite: ''
  };

  newFiles: File[] = [];
  currentUser?: Utilisateur;

  constructor(private api: NoteService, private router: Router, private auth: AuthService) {}

  ngOnInit(): void {
    this.currentUser = this.auth.getUser();
    // ⚡ Important : on initialise l’équipe seulement après avoir chargé currentUser
    this.newNote.equipe = this.currentUser?.equipe ?? '';
    this.newNote.auteur_id = this.currentUser?.id ?? 0;
  }

  /** Gestion des fichiers sélectionnés */
  handleFileInput(event: any) {
    const files: FileList = event.target.files;
    for (let i = 0; i < files.length; i++) {
      this.newFiles.push(files[i]);
    }
  }

  /** Supprimer un fichier sélectionné */
  removeFile(index: number) {
    this.newFiles.splice(index, 1);
  }

  /** Ajouter la note via le service NoteService */
  addNote(): void {
    if (!this.newNote.titre || !this.newNote.contenu || !this.newNote.categorie || !this.newNote.priorite) {
      alert('Veuillez remplir tous les champs obligatoires.');
      return;
    }
    this.newNote.contenu = DOMPurify.sanitize(this.newNote.contenu);

    this.api.createNoteWithFiles(this.newNote, this.newFiles).subscribe({
      next: (note: Note) => {
        alert('Note créée avec succès !');
        this.router.navigate(['/notes', note.id]); // Rediriger vers la page détail de la note
      },
      error: (err) => console.error('Erreur lors de l’ajout de la note', err)
    });
  }
}
