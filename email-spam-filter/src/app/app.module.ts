import { NgModule, PLATFORM_ID, Inject } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { isPlatformBrowser } from '@angular/common';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    BrowserModule,
    AppRoutingModule, // ✅ Ensure AppRoutingModule is imported
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
  declarations: [],
})
export class AppModule {
  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      console.log('Running in the browser');
    }
  }
}
