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
import { LoginComponent } from './components/login/login.component';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './auth.interceptor';
import { ToastComponent } from './components/shared/toast/toast.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { ConfirmDialogComponent } from './components/shared/confirm-dialog/confirm-dialog.component';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { UtilisateurDetailComponent } from './components/utilisateur-detail/utilisateur-detail.component';

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
    UtilisateurDetailComponent
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
  ],
  providers: [{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }, provideAnimationsAsync()],
  bootstrap: [AppComponent]
})
export class AppModule {}
