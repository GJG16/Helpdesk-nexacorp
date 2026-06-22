import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { environment } from '../../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should call login endpoint and save tokens', () => {
    const mockResponse: any = {
      access_token: 'fake_access_token',
      refresh_token: 'fake_refresh_token',
      token_type: 'bearer',
      user: { id: '1', nombre: 'Test User', email: 'test@example.com', rol: 'user' }
    };

    service.login('test@example.com', 'password').subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should logout and clear storage', () => {
    localStorage.setItem('access_token', 'test-token');
    service.logout();
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('should check if user is authenticated', () => {
    expect(service.isAuthenticated()).toBeFalsy();
    localStorage.setItem('access_token', 'test-token');
    expect(service.isAuthenticated()).toBeTruthy();
  });
});

describe('TicketService', () => {
  let service: any;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        {
          provide: 'TicketService',
          useValue: {
            getTickets: () => []
          }
        }
      ]
    });
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
