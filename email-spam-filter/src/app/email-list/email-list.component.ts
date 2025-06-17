import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-email-list',
  standalone: true, // Ensure it's a standalone component
  templateUrl: './email-list.component.html',
  styleUrls: ['./email-list.component.css'],
})
export class EmailListComponent implements OnInit {
  emails: any[] = [];

  ngOnInit() {
    const storedEmails = localStorage.getItem('emails');
    this.emails = storedEmails ? JSON.parse(storedEmails) : [];
  }
}
