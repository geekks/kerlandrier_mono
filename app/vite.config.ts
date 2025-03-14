import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // server: {
  //   watch: {
  //     ignored: ['!**/node_modules/**'], // Exclude node_modules explicitly
  //     usePolling: true, // Use polling instead of file system events
  //     interval: 100,    // Polling interval in milliseconds
  //   },
  // },
})
