import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService, UtilisateurDetailOut } from '../../services/api.service';

@Component({
  selector: 'app-utilisateur-detail',
  templateUrl: './utilisateur-detail.component.html',
  styleUrls: ['./utilisateur-detail.component.css']
})
export class UtilisateurDetailComponent implements OnInit {
  utilisateur?: UtilisateurDetailOut;
  isLoading = true;
  errorMessage = '';
  isEditing = false;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadUtilisateur(id);
  }

  loadUtilisateur(id: number) {
    this.api.getUtilisateurDetail(id).subscribe({
      next: (data) => {
        this.utilisateur = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "Impossible de charger l'utilisateur.";
        this.isLoading = false;
      }
    });
  }

  updateUtilisateur() {
    if (!this.utilisateur) return;
    this.api.updateUtilisateur(this.utilisateur.id, this.utilisateur).subscribe({
      next: (updated) => {
        this.utilisateur = updated as UtilisateurDetailOut;
        this.isEditing = false;
      },
      error: () => this.errorMessage = "Erreur lors de la mise à jour."
    });
  }

  deleteUtilisateur() {
    if (!this.utilisateur) return;
    if (confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
      this.api.deleteUtilisateur(this.utilisateur.id).subscribe({
        next: () => this.router.navigate(['/utilisateurs']),
        error: () => this.errorMessage = "Erreur lors de la suppression."
      });
    }
  }
}
