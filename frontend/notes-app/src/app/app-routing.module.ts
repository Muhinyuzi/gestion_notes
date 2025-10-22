import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { UtilisateursComponent } from './components/utilisateurs/utilisateurs.component';
import { UtilisateurDetailComponent } from './components/utilisateur-detail/utilisateur-detail.component';
import { NotesComponent } from './components/notes/notes.component';
import { NoteCreateComponent } from './components/note-create/note-create.component';
import { NoteDetailComponent } from './components/note-detail/note-detail.component';
import { ElevesComponent } from './components/eleves/eleves.component';
import { EleveDetailComponent } from './components/eleves/eleve-detail/eleve-detail.component';
import { LoginComponent } from './components/login/login.component';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';

const routes: Routes = [
  { path: '', component: HomeComponent , canActivate: [AuthGuard]},  // 👈 Home as default
  { path: 'utilisateurs', component: UtilisateursComponent, canActivate: [AuthGuard, AdminGuard] },
  { path: 'utilisateurs/:id', component: UtilisateurDetailComponent },
  { path: 'notes', component: NotesComponent, canActivate: [AuthGuard] },
  { path: 'notes/create', component: NoteCreateComponent },
  { path: 'notes/:id', component: NoteDetailComponent, canActivate: [AuthGuard] },
  { path: 'notes', component: NotesComponent, canActivate: [AuthGuard] },
  { path: 'eleves', component: ElevesComponent, canActivate: [AuthGuard] },
  { path: 'eleves/:id', component: EleveDetailComponent },
  { path: 'login', component: LoginComponent },
  { path: '**', redirectTo: 'login' }, // fallback to home
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}