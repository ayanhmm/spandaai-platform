import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/questions': {
        target: 'http://127.0.0.1:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/questions/, '')
      },
      '/api/generation': {
        target: 'http://127.0.0.1:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/generation/, '')
      },
      '/api': {
        target: 'http://127.0.0.1:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})