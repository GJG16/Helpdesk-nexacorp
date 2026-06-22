import { ChangeDetectorRef, Component, OnInit, OnDestroy, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { TicketService } from '../../../services/ticket.service';
import { AuthService } from '../../../services/auth.service';
import { UsuariosService } from '../../../services/usuarios.service';
import { Ticket, User, TicketComment } from '../../../models';

import { QuillModule } from 'ngx-quill';

@Component({
  selector: 'app-ticket-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule, RouterModule, QuillModule],
  templateUrl: './ticket-form.component.html',
  styleUrls: ['./ticket-form.component.css']
})
export class TicketFormComponent implements OnInit, OnDestroy, OnChanges {
  @Input() modalTicketId: string | null = null;
  @Output() close = new EventEmitter<void>();

  ticketForm: FormGroup;
  loading = false;
  isEditMode = false;
  ticketId: string | null = null;
  error = '';
  currentUser: User | null = null;
  usuarios: User[] = [];
  
  comments: TicketComment[] = [];
  newCommentTexto = '';
  submittingComment = false;
  timelineItems: any[] = [];
  currentTicket: Ticket | null = null;

  attachments: any[] = [];
  isDragover = false;
  apiUrl = 'http://localhost:8000'; // Or use environment.apiUrl

  private destroy$ = new Subject<void>();

  constructor(
    private formBuilder: FormBuilder,
    private ticketService: TicketService,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private usuariosService: UsuariosService
  ) {
    this.currentUser = this.authService.getCurrentUser();
    this.ticketForm = this.formBuilder.group({
      titulo: ['', [Validators.required, Validators.minLength(5)]],
      descripcion: ['', [Validators.required, Validators.minLength(10)]],
      prioridad: ['baja', Validators.required],
      estado: ['abierto', Validators.required],
      tipo: ['incidente', Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadUsuarios();
    
    if (this.modalTicketId) {
      this.setupEditMode(this.modalTicketId);
    } else {
      this.route.paramMap.pipe(takeUntil(this.destroy$)).subscribe(params => {
        const id = params.get('id');
        if (id && id !== 'new') {
          this.setupEditMode(id);
        }
      });
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['modalTicketId'] && changes['modalTicketId'].currentValue) {
      this.setupEditMode(changes['modalTicketId'].currentValue);
    }
  }

  setupEditMode(id: string) {
    this.isEditMode = true;
    this.ticketId = id;
    this.loadTicket(id);
    this.loadComments(id);
  }

  closeModal(): void {
    this.close.emit();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadUsuarios(): void {
    if (this.isAdmin() || this.authService.isAgent()) {
      this.usuariosService.getUsuarios().subscribe({
        next: (response: any) => {
          this.usuarios = response.items || response;
          this.cdr.detectChanges();
        },
        error: (err) => console.error('Error al cargar usuarios:', err)
      });
    }
  }

  loadTicket(id: string): void {
    this.loading = true;
    this.ticketService.getTicket(id).subscribe({
      next: (ticket) => {
        this.currentTicket = ticket;
        this.ticketForm.patchValue({
          titulo: ticket.titulo,
          descripcion: ticket.descripcion,
          prioridad: ticket.prioridad,
          estado: ticket.estado,
          tipo: ticket.tipo || 'incidente'
        });
        
        this.attachments = ticket.adjuntos || [];

        // Disable for users
        if (!this.isAdmin() && !this.authService.isAgent()) {
          this.ticketForm.disable();
        }
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.error = 'Error al cargar el ticket';
        this.loading = false;
      }
    });
  }

  loadComments(id: string): void {
    this.ticketService.getComments(id).subscribe({
      next: (comments) => {
        this.comments = comments;
        this.buildTimeline();
      },
      error: (err) => console.error('Error al cargar comentarios:', err)
    });
  }

  buildTimeline(): void {
    this.timelineItems = [];
    
    // Add history events
    if (this.currentTicket?.historial) {
      this.currentTicket.historial.forEach((h: any) => {
        this.timelineItems.push({
          type: 'history',
          date: new Date(h.fecha),
          data: h
        });
      });
    }

    // Add comments
    this.comments.forEach((c: any) => {
      this.timelineItems.push({
        type: 'comment',
        date: new Date(c.fecha_creacion),
        data: c
      });
    });

    // Sort by date
    this.timelineItems.sort((a, b) => a.date.getTime() - b.date.getTime());
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragover = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragover = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragover = false;
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.uploadFiles(files);
    }
  }

  onFileSelected(event: any): void {
    const files = event.target.files;
    if (files && files.length > 0) {
      this.uploadFiles(files);
    }
  }

  uploadFiles(files: FileList): void {
    if (!this.ticketId) return;
    // For simplicity, just upload the first file
    const file = files[0];
    this.loading = true;
    this.ticketService.uploadAttachment(this.ticketId, file).subscribe({
      next: (res) => {
        this.loading = false;
        this.loadTicket(this.ticketId!);
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Error al subir el archivo.';
        console.error(err);
      }
    });
  }

  submitComment(): void {
    if (!this.newCommentTexto.trim() || !this.ticketId) return;
    this.submittingComment = true;
    this.ticketService.addComment(this.ticketId, this.newCommentTexto).subscribe({
      next: (comment) => {
        this.comments.push(comment);
        this.newCommentTexto = '';
        this.submittingComment = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error enviando comentario:', err);
        this.submittingComment = false;
      }
    });
  }

  onSubmit(): void {
    if (this.ticketForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    const formValue = this.ticketForm.value;

    if (this.isEditMode && this.ticketId) {
      const updatePayload = this.isAdmin()
        ? formValue
        : {
            estado: formValue.estado,
            prioridad: formValue.prioridad,
            tipo: formValue.tipo,
          };

      this.ticketService.updateTicket(this.ticketId, updatePayload).subscribe({
        next: () => {
          if (this.modalTicketId) {
            this.close.emit();
          } else {
            this.router.navigate(['/tickets']);
          }
        },
        error: (error) => {
          this.error = error.error?.detail || 'Error al actualizar el ticket';
          this.loading = false;
          this.cdr.detectChanges();
        }
      });
    } else {
      const newTicket = {
        ...formValue,
        usuario_id: this.authService.isAdmin() ? formValue.usuario_id : this.currentUser?.id
      };
      this.ticketService.createTicket(newTicket).subscribe({
        next: () => {
          if (this.modalTicketId) {
            this.close.emit();
          } else {
            this.router.navigate(['/tickets']);
          }
        },
        error: (error) => {
          this.error = error.error?.detail || 'Error al crear el ticket';
          this.loading = false;
          this.cdr.detectChanges();
        }
      });
    }
  }

  cancel(): void {
    if (this.modalTicketId) {
      this.close.emit();
    } else {
      this.router.navigate(['/tickets']);
    }
  }

  get f() {
    return this.ticketForm.controls;
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }
}
