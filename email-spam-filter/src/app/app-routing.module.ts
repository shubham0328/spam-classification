import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { EmailListComponent } from './components/email-list/email-list.component';

const routes: Routes = [
  { path: '', component: LoginComponent }, // Default route → Login
  { path: 'emails', component: EmailListComponent }, // Redirect to emails page
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
