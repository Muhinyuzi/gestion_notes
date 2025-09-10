import { Component, OnInit } from '@angular/core';
import { ApiService, Note , NoteCreate} from '../../services/api.service';

@Component({
  selector: 'app-notes',
  templateUrl: './notes.component.html',
  styleUrls: ['./notes.component.css']
})
export class NotesComponent implements OnInit {
  notes: Note[] = [];
  newNote: NoteCreate = { titre: '', contenu: '', equipe: '', auteur_id: 1 };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadNotes();
  }

  // Charger toutes les notes
  loadNotes(): void {
    this.api.getNotes().subscribe(data => this.notes = data);
  }

  // Ajouter une note
  addNote(): void {
    if (!this.newNote.titre || !this.newNote.contenu) {
      alert('Veuillez entrer un titre et un contenu.');
      return;
    }

    this.api.createNote(this.newNote).subscribe(note => {
      this.notes.push(note);
      this.newNote = { titre: '', contenu: '', equipe: '', auteur_id: 1 }; // reset
    });
  }
}
