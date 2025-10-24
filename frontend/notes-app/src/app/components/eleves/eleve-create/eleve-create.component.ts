import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { EleveService, Eleve } from '../../../services/eleve.service';

@Component({
  selector: 'app-eleve-create',
  templateUrl: './eleve-create.component.html',
  styleUrls: ['./eleve-create.component.css']
})
export class EleveCreateComponent {
  eleve: Eleve = {
    nom: '',
    prenom: '',
    adresse: '',
    actif: true,
    en_attente: false
  };

  isSubmitting = false;
  errorMessage = '';

  constructor(private eleveService: EleveService, private router: Router) {}

  onSubmit(): void {
    if (!this.eleve.nom || !this.eleve.prenom) {
      this.errorMessage = 'Veuillez remplir au moins le nom et le prénom.';
      return;
    }

    this.isSubmitting = true;
    console.log(this.eleve);
    this.eleveService.createEleve(this.eleve).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.router.navigate(['/eleves']);
      },
      error: (err) => {
        console.error('Erreur création élève:', err);
        this.errorMessage = 'Une erreur est survenue lors de la création.';
        this.isSubmitting = false;
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/eleves']);
  }
}
