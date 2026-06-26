import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-skeleton',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './skeleton.html',
  styleUrls: ['./skeleton.css']
})
export class SkeletonComponent {
  @Input() type: 'text' | 'circular' | 'rectangular' = 'text';
  @Input() width: string = '100%';
  @Input() height: string = '1rem';
  @Input() className: string = '';

  get skeletonClasses(): string {
    const baseClasses = 'animate-pulse bg-slate-200 dark:bg-slate-700';
    let typeClasses = '';

    switch (this.type) {
      case 'circular':
        typeClasses = 'rounded-full';
        break;
      case 'rectangular':
        typeClasses = 'rounded-md';
        break;
      case 'text':
      default:
        typeClasses = 'rounded';
        break;
    }

    return `${baseClasses} ${typeClasses} ${this.className}`;
  }
}
