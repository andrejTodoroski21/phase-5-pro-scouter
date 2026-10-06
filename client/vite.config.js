import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5555',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:5555',
        ws: true,
      },
      // Locally-stored clip uploads. In production Flask serves these itself,
      // and with R2 configured they come from the bucket instead.
      '/media': {
        target: 'http://localhost:5555',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Router and React change far less often than app code, so giving them
    // their own chunk keeps them cached across deploys.
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
})
