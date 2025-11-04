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
import { NoteDetailComponent } from './components/notes/note-detail/note-detail.component';
import { LoginComponent } from './components/login/login.component';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { ToastComponent } from './components/shared/toast/toast.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { ConfirmDialogComponent } from './components/shared/confirm-dialog/confirm-dialog.component';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDividerModule } from '@angular/material/divider';
import { MatCardModule } from '@angular/material/card';
import { UtilisateurDetailComponent } from './components/utilisateurs/utilisateur-detail/utilisateur-detail.component';
import { NoteCreateComponent } from './components/notes/note-create/note-create.component';
import { EditorModule } from '@progress/kendo-angular-editor';
import { ElevesComponent } from './components/eleves/eleves.component';
import { EleveDetailComponent } from './components/eleves/eleve-detail/eleve-detail.component';
import { EleveCreateComponent } from './components/eleves/eleve-create/eleve-create.component';
import { EleveEditComponent } from './components/eleves/eleve-edit/eleve-edit.component';

@NgModule({
  declarations: [
    AppComponent,
    UtilisateursComponent,
    NotesComponent,
    CommentairesComponent,
    HomeComponent,
    NoteDetailComponent,
    LoginComponent,
    ToastComponent,
    ConfirmDialogComponent,
    UtilisateurDetailComponent,
    NoteCreateComponent,
    ElevesComponent,
    EleveDetailComponent,
    EleveCreateComponent,
    EleveEditComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,       // <-- Obligatoire pour ngModel
    HttpClientModule, AppRoutingModule,   // <-- Obligatoire pour appeler ton API
    BrowserAnimationsModule, // ✅ indispensable pour Angular Material
    MatDialogModule,         // ✅ pour <mat-dialog-content> et <mat-dialog-actions>
    MatButtonModule, 
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatInputModule,
    MatDividerModule,
    MatCardModule,
    EditorModule,
  ],
  providers: [{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }, provideAnimationsAsync()],
  bootstrap: [AppComponent]
})
export class AppModule {}
