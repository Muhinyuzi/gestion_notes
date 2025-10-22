import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { EleveService, Eleve } from '../../../services/eleve.service';
import { NoteService, Note } from '../../../services/note.service';

@Component({
  selector: 'app-eleve-detail',
  templateUrl: './eleve-detail.component.html',
  styleUrls: ['./eleve-detail.component.css']
})
export class EleveDetailComponent implements OnInit {

  eleve?: Eleve;
  note?: Note;
  isLoading = false;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private eleveService: EleveService,
    private noteService: NoteService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadEleve(id);
    } else {
      this.errorMessage = 'ID élève non valide.';
    }
  }

  loadEleve(id: number): void {
    this.isLoading = true;
    this.eleveService.getEleveById(id).subscribe({
      next: (data) => {
        this.eleve = data;
        this.isLoading = false;

        // Charger la note associée si elle existe
        if (data.note_id) {
          this.noteService.getNoteById(data.note_id).subscribe({
            next: (n) => this.note = n,
            error: (err) => console.error('Erreur chargement note', err)
          });
        }
      },
      error: (err) => {
        this.errorMessage = 'Erreur lors du chargement de l’élève.';
        console.error(err);
        this.isLoading = false;
      }
    });
  }

  editEleve(): void {
    if (this.eleve?.id)
      this.router.navigate(['/eleves/edit', this.eleve.id]);
  }

  deleteEleve(): void {
    if (!this.eleve?.id) return;
    if (!confirm(`Supprimer ${this.eleve.prenom} ${this.eleve.nom} ?`)) return;

    this.eleveService.deleteEleve(this.eleve.id).subscribe({
      next: () => this.router.navigate(['/eleves']),
      error: (err) => {
        alert('Erreur lors de la suppression');
        console.error(err);
      }
    });
  }

  unassignNote(): void {
    if (!this.eleve?.id) return;

    this.eleveService.unassignNoteFromEleve(this.eleve.id).subscribe({
      next: (updated) => this.eleve = updated,
      error: (err) => console.error('Erreur désassignation', err)
    });
  }

}
