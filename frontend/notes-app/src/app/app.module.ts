import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { UtilisateursComponent } from './components/utilisateurs/utilisateurs.component';
import { NotesComponent } from './components/notes/notes.component';
import { CommentairesComponent } from './components/commentaires/commentaires.component';
import { AppRoutingModule } from './app-routing.module';
import { HomeComponent } from './components/home/home.component';
import { NoteDetailComponent } from './components/note-detail/note-detail.component';

@NgModule({
  declarations: [
    AppComponent,
    UtilisateursComponent,
    NotesComponent,
    CommentairesComponent,
    HomeComponent,
    NoteDetailComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,       // <-- Obligatoire pour ngModel
    HttpClientModule, AppRoutingModule   // <-- Obligatoire pour appeler ton API
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
