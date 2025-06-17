import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  error: string = '';
  loading: boolean = false;

  constructor(private router: Router, private http: HttpClient) {}

  login() {
    this.loading = true;
    this.error = '';

    this.http.post<{ message: string }>('http://localhost:8000/login/', {
      email: this.email,
      password: this.password,
    }).subscribe({
      next: (response) => {
        localStorage.setItem('email', this.email);
        localStorage.setItem('password', this.password);

        this.router.navigate(['/emails']).then(() => {
          console.log("✅ Navigation to /emails successful");
        });
      },
      error: (err) => {
        this.error = err.status === 401 ? 'Invalid email or password.' : 'Server error. Please try again.';
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}
