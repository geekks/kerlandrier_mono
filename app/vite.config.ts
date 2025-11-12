import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  preview: {
    allowedHosts: [
      'app.kerlandrier.cc',
      'localhost',
      '127.0.0.1'
    ]
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks for large libraries
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['@mui/material', '@emotion/react', '@emotion/styled'],
          'vendor-data': ['@tanstack/react-query'],
          'vendor-utils': ['luxon', 'ky', 'react-icons'],
        }
      }
    },
    // Increase chunk size warning limit to 1MB for vendor chunks
    chunkSizeWarningLimit: 1000,
    // Enable source maps for better debugging (optional)
    sourcemap: false
  }
})
