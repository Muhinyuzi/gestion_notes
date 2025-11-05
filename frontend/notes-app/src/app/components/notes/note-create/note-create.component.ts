import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NoteService, NoteCreate, Note, Utilisateur } from '../../../services/note.service';
import { AuthService } from '../../../services/auth.service';
import DOMPurify from 'dompurify';
import { ToastService } from '../../../services/toast.service';
import { Location } from '@angular/common';

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
  isSubmitting = false;

  constructor(
    private api: NoteService, 
    private router: Router,
    private auth: AuthService,
    private toast: ToastService, 
    private location: Location
  ) {}

  ngOnInit(): void {
    this.currentUser = this.auth.getUser();

    if (!this.currentUser) {
      this.toast.show("⚠️ Session expirée, veuillez vous reconnecter.", "error");
      this.router.navigate(['/login']);
      return;
    }

       this.newNote.equipe = this.currentUser?.equipe ?? ''; 
       this.newNote.auteur_id = this.currentUser?.id ?? 0;
  }

  handleFileInput(event: any) {
    const files: FileList = event.target.files;
    for (let i = 0; i < files.length; i++) {
      this.newFiles.push(files[i]);
    }
  }

  removeFile(index: number) {
    this.newFiles.splice(index, 1);
  }

  addNote(): void {
    if (!this.newNote.titre || !this.newNote.contenu || !this.newNote.categorie || !this.newNote.priorite) {
      this.toast.show("❗ Veuillez remplir tous les champs obligatoires.", "error");
      return;
    }

    this.newNote.contenu = DOMPurify.sanitize(this.newNote.contenu);
    this.isSubmitting = true;

    this.api.createNoteWithFiles(this.newNote, this.newFiles).subscribe({
      next: (note: Note) => {
        this.toast.show("✅ Note créée avec succès !", "success");
        this.router.navigate(['/notes', note.id]);
      },
      error: () => {
        this.toast.show("❌ Erreur lors de la création de la note", "error");
        this.isSubmitting = false;
      }
    });
  }

  goBack(): void {
    this.location.back();
  } 
}
