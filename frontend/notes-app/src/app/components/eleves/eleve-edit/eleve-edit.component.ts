import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { EleveService, Eleve } from '../../../services/eleve.service';
import { Location } from '@angular/common';

@Component({
  selector: 'app-eleve-edit',
  templateUrl: './eleve-edit.component.html',
  styleUrls: ['./eleve-edit.component.css']
})
export class EleveEditComponent implements OnInit {

  eleve: Eleve = { nom: '', prenom: '', adresse: '', actif: true, en_attente: false };
  isLoading = false;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private eleveService: EleveService,
    private location: Location
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadEleve(id);
    } else {
      this.errorMessage = 'ID élève invalide.';
    }
  }

  loadEleve(id: number): void {
    this.isLoading = true;
    this.eleveService.getEleveById(id).subscribe({
      next: (data) => {
        this.eleve = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Erreur lors du chargement de l’élève.';
        console.error(err);
        this.isLoading = false;
      }
    });
  }

  onSubmit(): void {
    if (!this.eleve.nom || !this.eleve.prenom) {
      this.errorMessage = 'Veuillez remplir tous les champs obligatoires.';
      return;
    }

    this.isLoading = true;
    console.log('Payload envoyé:', this.eleve);
    this.eleveService.updateEleve(this.eleve.id!, this.eleve).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/eleves']);
      },
      error: (err) => {
        this.errorMessage = 'Erreur lors de la mise à jour.';
        console.error(err);
        this.isLoading = false;
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
