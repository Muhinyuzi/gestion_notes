import { Component, OnInit } from '@angular/core';
import { UtilisateurService, Utilisateur, UtilisateursResponse } from '../../services/utilisateur.service';
import { ToastComponent } from '../../components/shared/toast/toast.component';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-utilisateurs',
  templateUrl: './utilisateurs.component.html',
  styleUrls: ['./utilisateurs.component.css']
})
export class UtilisateursComponent implements OnInit {
  utilisateurs: Utilisateur[] = [];

  // Pour ajout et édition
  newUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
  selectedUser: Utilisateur = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
  isEditing = false;
  isAdding = false; 

  isLoading = false;
  errorMessage = '';

  // Filtres
  filterNom = '';
  filterEmail = '';
  filterEquipe = '';

  // Pagination
  page = 1;
  limit = 10;
  total = 0;

  constructor(private api: UtilisateurService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  // Getter pour formulaire
  get formUser(): Utilisateur {
    return this.isEditing ? this.selectedUser : this.newUser;
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.limit);
  }

  // Retourne la liste filtrée pour affichage
  get filteredUsers(): Utilisateur[] {
    return this.utilisateurs.filter(u =>
      u.nom.toLowerCase().includes(this.filterNom.toLowerCase()) &&
      u.email.toLowerCase().includes(this.filterEmail.toLowerCase()) &&
      (!this.filterEquipe || (u.equipe && u.equipe.toLowerCase().includes(this.filterEquipe.toLowerCase())))
    );
  }

  // Appliquer les filtres (Angular met automatiquement à jour filteredUsers)
  applyFilters(): void {}

  // Charger les utilisateurs depuis backend avec pagination
  loadUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.api.getUtilisateurs(this.page, this.limit).subscribe({
      next: (res: UtilisateursResponse) => {
        this.utilisateurs = res.users;
        this.total = res.total;
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "Impossible de charger les utilisateurs.";
        this.isLoading = false;
      }
    });
  }

  // Pagination
  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.page = page;
    this.loadUsers();
  }

  // Ajouter un utilisateur
  addUtilisateur(): void {
    if (!this.newUser.nom || !this.newUser.email || !this.newUser.mot_de_passe) {
      alert("Nom, email et mot de passe sont requis !");
      return;
    }

    this.api.createUtilisateur(this.newUser).subscribe({
      next: (user) => {
        this.utilisateurs.unshift(user);
        this.total += 1;
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
    this.selectedUser = { ...user, mot_de_passe: '' }; // mot de passe vide
    this.isEditing = true;
  }

  // Sauvegarder les modifications
  updateUtilisateur(): void {
    if (!this.selectedUser.id) return;

    const updatedData: Partial<Utilisateur> = { ...this.selectedUser };
    if (!updatedData.mot_de_passe) delete updatedData.mot_de_passe;

    this.api.updateUtilisateur(this.selectedUser.id, updatedData).subscribe({
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

  // Ouvrir le dialogue de confirmation
  const dialogRef = this.dialog.open(ConfirmDialogComponent, {
    width: '350px',
    data: { message: `Voulez-vous vraiment supprimer ${user.nom} ?` }
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result) { // si l'utilisateur a confirmé
      this.api.deleteUtilisateur(user.id!).subscribe({
        next: () => {
          this.utilisateurs = this.utilisateurs.filter(u => u.id !== user.id);
          this.total -= 1;
        },
        error: (err) => {
          console.error(err);
          this.errorMessage = "Erreur lors de la suppression.";
        }
      });
    }
    });
   }


  // Réinitialiser le formulaire
  resetForm(): void {
    this.isEditing = false;
    this.selectedUser = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
    this.newUser = { nom: '', email: '', mot_de_passe: '', equipe: '', adresse: '', telephone: '', type: '' };
  }

  startAdding() {
  this.isAdding = true;
  this.isEditing = false;
  this.resetForm(); // vide le formulaire pour un nouvel utilisateur
 }

 cancelForm() {
  this.isAdding = false;
  this.isEditing = false;
  this.resetForm();
}
}
