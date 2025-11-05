import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { EleveService, Eleve } from '../../../services/eleve.service';
import { ToastService } from '../../../services/toast.service';
import { Location } from '@angular/common';

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

  constructor(
    private eleveService: EleveService,
    private router: Router,
    private toast: ToastService,
    private location: Location,
  ) {}

  onSubmit(): void {
    //this.toast.show("🟢 Test Toast OK !", "success");
    if (!this.eleve.nom || !this.eleve.prenom) {
      this.toast.show('Veuillez remplir nom et prénom ❗', 'error');
      return;
    }

    this.isSubmitting = true;

    this.eleveService.createEleve(this.eleve).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.toast.show('✅ Élève créé avec succès', 'success');
        this.router.navigate(['/eleves']);
      },
      error: (err) => {
        console.error('Erreur création élève:', err);
        this.toast.show('❌ Erreur lors de la création', 'error');
        this.isSubmitting = false;
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/eleves']);
  }

  goBack(): void {
    this.location.back();
  }

}
