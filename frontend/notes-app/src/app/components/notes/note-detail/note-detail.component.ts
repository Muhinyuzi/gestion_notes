import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NoteService, Note, Utilisateur } from '../../../services/note.service';
import { AuthService } from '../../../services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';
import { ToastService } from '../../../services/toast.service'; // ✅ Import du service

@Component({
  selector: 'app-note-detail',
  templateUrl: './note-detail.component.html',
  styleUrls: ['./note-detail.component.css']
})
export class NoteDetailComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  note?: Note;
  utilisateur?: Utilisateur;
  isLoading = true;
  errorMessage = '';
  isEditing = false;
  hasLiked = false;

  newFiles: File[] = [];
  currentUser?: Utilisateur;

  constructor(
    private route: ActivatedRoute,
    private api: NoteService,
    private router: Router,
    private dialog: MatDialog,
    private auth: AuthService,
    private toast: ToastService  // ✅ Injection du service
  ) {}

  ngOnInit(): void {
    this.currentUser = this.auth.getUser();

    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.api.getNoteById(id).subscribe({
      next: (data) => {
        this.note = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "❌ Impossible de charger la note.";
        this.isLoading = false;
        this.toast.show("❌ Impossible de charger la note.", "error");
      }
    });
  }

  handleFileInput(event: any) {
    const files: FileList = event.target.files;
    for (let i = 0; i < files.length; i++) this.newFiles.push(files[i]);

    if (this.note) {
      this.note.fichiers = this.note.fichiers || [];
      this.note.fichiers.push(...Array.from(files).map((file, i) => ({
        id: Date.now() + i,
        nom_fichier: file.name,
        chemin: ''
      })));
    }
  }

  removeFile(index: number) {
    this.newFiles.splice(index, 1);
  }

  updateNote(): void {
    if (!this.note) return;

    const formData = new FormData();
    formData.append('titre', this.note.titre);
    formData.append('contenu', this.note.contenu);
    if (this.note.equipe) formData.append('equipe', this.note.equipe);
    if (this.note.priorite) formData.append('priorite', this.note.priorite);
    if (this.note.categorie) formData.append('categorie', this.note.categorie);

    this.newFiles.forEach(file => formData.append('fichiers', file));

    this.api.updateNote(this.note.id, formData as any).subscribe({
      next: () => {
        this.isEditing = false;
        this.newFiles = [];
        this.toast.show("✅ Note mise à jour avec succès !", "success");
      },
      error: () => {
        this.toast.show("❌ Erreur lors de la mise à jour", "error");
      }
    });
  }

  deleteNote(): void {
    if (!this.note) return;

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '350px',
      data: { message: "Voulez-vous vraiment supprimer cette note ?" }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.api.deleteNote(this.note!.id).subscribe({
          next: () => {
            this.toast.show("✅ Note supprimée", "success");
            this.router.navigate(['/notes']);
          },
          error: () => {
            this.toast.show("❌ Erreur lors de la suppression", "error");
          }
        });
      }
    });
  }

  canEditOrDelete(note: Note): boolean {
    return this.currentUser?.id === note.auteur?.id || this.currentUser?.type === 'admin';
  }

  likeNote(): void {
    if (!this.note || this.hasLiked) return;

    this.api.likeNote(this.note.id).subscribe({
      next: res => {
        if (this.note) this.note.likes = res.likes;
        this.hasLiked = true;
      },
      error: () => {
        this.toast.show("❌ Erreur lors du like", "error");
      }
    });
  }

  getFileUrl(path: string): string {
    const fixedPath = path.replace(/\\/g, '/');
    return `${this.api.getBaseUrl()}${fixedPath}`;
  }

  viewImage(path: string) {
    window.open(this.getFileUrl(path), '_blank');
  }

  isNew(dateStr: string): boolean {
    const created = new Date(dateStr);
    const now = new Date();
    const diff = (now.getTime() - created.getTime()) / (1000*60*60*24);
    return diff <= 7;
  }

  removeExistingFile(fichierId: number) {
    if (!this.note) return;

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '350px',
      data: { message: "Voulez-vous vraiment supprimer ce fichier ?" }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.api.deleteFile(fichierId).subscribe({
          next: () => {
            this.note!.fichiers = this.note!.fichiers?.filter(f => f.id !== fichierId);
            this.toast.show("✅ Fichier supprimé", "success");
          },
          error: () => {
            this.toast.show("❌ Erreur lors de la suppression du fichier", "error");
          }
        });
      }
    });
  }
}
