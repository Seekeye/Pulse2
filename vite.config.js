import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js',
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://pulse2-production.up.railway.app',
        changeOrigin: true,
        secure: true,
      },
      '/ws': {
        target: 'wss://pulse2-production.up.railway.app',
        ws: true,
        secure: true,
      }
    }
  }
})