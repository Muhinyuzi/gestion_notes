/*import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { UtilisateursComponent } from './components/utilisateurs/utilisateurs.component';
import { NotesComponent } from './components/notes/notes.component';

const routes: Routes = [
  { path: 'utilisateurs', component: UtilisateursComponent },
  { path: 'notes', component: NotesComponent },
  { path: '', redirectTo: '/utilisateurs', pathMatch: 'full' } // page par défaut
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
*/

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { UtilisateursComponent } from './components/utilisateurs/utilisateurs.component';
import { NotesComponent } from './components/notes/notes.component';
import { NoteDetailComponent } from './components/note-detail/note-detail.component';

const routes: Routes = [
  { path: '', component: HomeComponent },  // 👈 Home as default
  { path: 'utilisateurs', component: UtilisateursComponent },
  { path: 'notes', component: NotesComponent },
  { path: 'notes/:id', component: NoteDetailComponent },
  { path: '**', redirectTo: '' }, // fallback to home
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}