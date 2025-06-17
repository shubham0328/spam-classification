import { Component, OnInit, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common'; // ✅ Import CommonModule


@Component({
  selector: 'app-email-list',
  standalone: true,
  imports: [CommonModule], // ✅ Add CommonModule here
  templateUrl: './email-list.component.html',
  styleUrls: ['./email-list.component.css'],
})
export class EmailListComponent implements OnInit {
  allEmails: any[] = [];
  displayedEmails: any[] = [];
  batchSize: number = 20;
  currentIndex: number = 0;
  loadingMore: boolean = false;

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    const email = localStorage.getItem('email');
    const password = localStorage.getItem('password');

    if (!email || !password) {
      console.error("⚠️ No stored credentials. Redirecting to login.");
      this.router.navigate(['/']);
      return;
    }

    this.http.post<{ emails: any[] }>('http://localhost:8000/emails/', {
      email,
      password
    }).subscribe({
      next: (response) => {
        if (response.emails.length === 0) {
          console.warn("⚠️ No emails found.");
        }
        this.allEmails = response.emails.slice(0, 1000);
        this.loadMore();
      },
      error: (err) => {
        console.error("❌ Error fetching emails:", err);
        alert("Failed to fetch emails. Please login again.");
        this.router.navigate(['/']);
      }
    });
  }

  loadMore() {
    this.loadingMore = true;
    setTimeout(() => {
      const nextIndex = this.currentIndex + this.batchSize;
      const newBatch = this.allEmails.slice(this.currentIndex, nextIndex);
      this.displayedEmails = [...this.displayedEmails, ...newBatch];
      this.currentIndex = nextIndex;
      this.loadingMore = false;
    }, 500);
  }


  @HostListener('scroll', ['$event'])
  onScroll(event: any) {
    const element = event.target;
    if (element.scrollHeight - element.scrollTop === element.clientHeight) {
      if (this.currentIndex < this.allEmails.length && !this.loadingMore) {
        this.loadMore();
      }
    }
  }

  logout() {
    localStorage.removeItem('email');
    localStorage.removeItem('password');
    localStorage.removeItem('emails');
    this.router.navigate(['/']);
  }
}
