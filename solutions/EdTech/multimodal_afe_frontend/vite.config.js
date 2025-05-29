import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/multimodal/',
  plugins: [react()],
  optimizeDeps: {
    exclude: ['pdfjs-dist']
  },
  server: {
    host: true,  // ✅ Allows access from external networks
    strictPort: false,  // ✅ Allows Vite to use different ports if needed
    cors: true,  // ✅ Enables Cross-Origin Resource Sharing
    headers: {
      "Content-Security-Policy": "frame-ancestors 'self' https://docs.google.com https://localhost;",
    },
    allowedHosts: [
      'localhost',
      '.ngrok-free.app'  // ✅ Allow dynamic ngrok subdomains
    ]
  }
});
