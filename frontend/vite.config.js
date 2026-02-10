import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa' // <--- Importamos esto

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Convertidor PDF a EPUB',
        short_name: 'PDF2EPUB',
        description: 'Convierte tus libros PDF a EPUB facilmente',
        theme_color: '#42b883',
        background_color: '#ffffff',
        display: 'standalone', // <--- ESTO QUITA LA BARRA DE NAVEGACIÓN
        icons: [
          {
            src: 'pwa-192x192.png', // Nota: Necesitarás crear esta imagen
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png', // Nota: Necesitarás crear esta imagen
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})