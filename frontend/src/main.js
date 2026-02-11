import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { registerSW } from 'virtual:pwa-register'

const updateSW = registerSW({
  onNeedRefresh() {
    console.log('Nueva versión disponible. Por favor, actualiza la página.')
  },
  onOfflineReady() {
    console.log('La aplicación está lista para funcionar sin conexión.')
  }
})

createApp(App).mount('#app')
