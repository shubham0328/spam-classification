import { Component, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { EmailListComponent } from './components/email-list/email-list.component';

@Component({
  selector: 'app-root',
  standalone: true, // ✅ Make AppComponent standalone
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [RouterModule] // ✅ Import standalone components
})
export class AppComponent {
  title = 'email-spam-filter';

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      // Only execute this code in the browser
      document.title = 'Email Spam Filter';
    }
  }
}


