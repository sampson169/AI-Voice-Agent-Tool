import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    
    define: {
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION || '1.0.0'),
      __APP_NAME__: JSON.stringify(env.VITE_APP_NAME || 'Voice Agent Tool'),
    },
    
    server: {
      port: parseInt(env.VITE_DEV_PORT) || 5173,
      open: true,
      cors: true,
    },
    
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            retell: ['retell-client-js-sdk'],
            utils: ['axios', 'lucide-react']
          }
        }
      }
    },
    
    envPrefix: 'VITE_',
  }
})
