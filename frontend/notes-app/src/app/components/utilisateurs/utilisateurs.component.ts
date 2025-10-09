import { Component, OnInit } from '@angular/core';
import { ApiService, Utilisateur } from '../../services/api.service';

@Component({
  selector: 'app-utilisateurs',
  templateUrl: './utilisateurs.component.html',
  styleUrls: ['./utilisateurs.component.css']
})
export class UtilisateursComponent implements OnInit {
  utilisateurs: Utilisateur[] = [];

  // Pour ajout et édition
  newUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '' };
  selectedUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '' };
  isEditing = false;

  isLoading = false;
  errorMessage = '';

  // Filtres
  filterNom = '';
  filterEmail = '';
  filterEquipe = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  // Getter pour le formulaire
  get formUser(): Utilisateur {
    return this.isEditing ? this.selectedUser : this.newUser;
  }

  // Retourne la liste filtrée pour affichage
  get filteredUsers(): Utilisateur[] {
    return this.utilisateurs.filter(u =>
      u.nom.toLowerCase().includes(this.filterNom.toLowerCase()) &&
      u.email.toLowerCase().includes(this.filterEmail.toLowerCase()) &&
      (!this.filterEquipe || (u.equipe && u.equipe.toLowerCase().includes(this.filterEquipe.toLowerCase())))
    );
  }

  // Charger les utilisateurs
  loadUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.api.getUtilisateurs().subscribe({
      next: (data: any) => {
        // Assurer que c’est toujours un tableau
        this.utilisateurs = Array.isArray(data) ? data : data.utilisateurs || [];
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
        this.resetForm();
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "Erreur lors de la création de l'utilisateur.";
      }
    });
  }

  // Préparer la modification
  editUtilisateur(user: Utilisateur): void {
    this.selectedUser = { ...user };
    this.isEditing = true;
  }

  // Sauvegarder les modifications
  updateUtilisateur(): void {
    if (!this.selectedUser.id) return;

    this.api.updateUtilisateur(this.selectedUser.id, this.selectedUser).subscribe({
      next: (updated) => {
        const index = this.utilisateurs.findIndex(u => u.id === updated.id);
        if (index !== -1) this.utilisateurs[index] = updated;
        this.resetForm();
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "Erreur lors de la mise à jour.";
      }
    });
  }

  // Supprimer un utilisateur
  deleteUtilisateur(user: Utilisateur): void {
    if (!user.id) return;
    if (!confirm(`Voulez-vous vraiment supprimer ${user.nom} ?`)) return;

    this.api.deleteUtilisateur(user.id).subscribe({
      next: () => {
        this.utilisateurs = this.utilisateurs.filter(u => u.id !== user.id);
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "Erreur lors de la suppression.";
      }
    });
  }

  // Réinitialiser le formulaire
  resetForm(): void {
    this.isEditing = false;
    this.selectedUser = { nom: '', email: '', mot_de_passe: '', equipe: '' };
    this.newUser = { nom: '', email: '', mot_de_passe: '', equipe: '' };
  }
}
