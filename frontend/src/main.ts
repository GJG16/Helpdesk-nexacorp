import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

// Hook temporal: interceptar window.fetch para loggear llamadas a /api/tickets/
try {
  const _origFetch = window.fetch;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  window.fetch = function(input: RequestInfo, init?: RequestInit) {
    try {
      const url = typeof input === 'string' ? input : input.url;
      if (url && url.includes('/api/tickets')) {
        const headers = (init && init.headers) || (typeof input !== 'string' && (input as Request).headers) || {};
        const hasAuth = (headers && ((headers as any).Authorization || (headers as any).authorization)) ? true : false;
        console.debug('fetch-hook: /api/tickets/ called, hasAuth=', hasAuth, 'url=', url, 'initHeaders=', headers);
      }
    } catch (e) {}
    return _origFetch.apply(this, arguments as any);
  };
} catch (e) {}

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
