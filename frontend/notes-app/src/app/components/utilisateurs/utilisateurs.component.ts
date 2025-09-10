import { Component, OnInit } from '@angular/core';
import { ApiService, Utilisateur } from '../../services/api.service';

@Component({
  selector: 'app-utilisateurs',
  templateUrl: './utilisateurs.component.html',
  styleUrls: ['./utilisateurs.component.css']
})
export class UtilisateursComponent implements OnInit {
  utilisateurs: Utilisateur[] = [];
  newUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '' };

  isLoading = false;
  errorMessage = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  // Charger les utilisateurs
  loadUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.api.getUtilisateurs().subscribe({
      next: (data) => {
        this.utilisateurs = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "Impossible de charger les utilisateurs.";
        this.isLoading = false;
      }
    });
  }

  // Ajouter un utilisateur
  addUtilisateur(): void {
    if (!this.newUser.nom || !this.newUser.email) {
      alert("Nom et email sont requis !");
      return;
    }

    this.api.createUtilisateur(this.newUser).subscribe({
      next: (user) => {
        this.utilisateurs.push(user);
        this.newUser = { nom: '', email: '', mot_de_passe: '', equipe: '' };
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "Erreur lors de la création de l'utilisateur.";
      }
    });
  }
}
