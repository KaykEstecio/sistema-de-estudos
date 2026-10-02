import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const qaProxy = process.env.CODETRACK_QA_API_PROXY
if (qaProxy && qaProxy !== 'http://127.0.0.1:8100') throw new Error('Proxy de QA inválido.')
const apiTarget = qaProxy || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '^/health$': apiTarget,
      '/api/v1': apiTarget,
    },
  },
})
