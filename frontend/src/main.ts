import { createApp } from 'vue'

import App from './App.vue'
import { developDirective } from './directives/develop'

import './style.css'

createApp(App).directive('develop', developDirective).mount('#app')

if ('serviceWorker' in navigator && import.meta.env.DEV) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.getRegistrations().then(registrations => {
      registrations.forEach(registration => registration.unregister())
    }).catch(() => {
      // Old PWA registrations should not be able to break the dev server.
    })

    if ('caches' in window) {
      caches.keys().then(keys => {
        keys
          .filter(key => key.startsWith('u-life-film-journal'))
          .forEach(key => caches.delete(key))
      }).catch(() => {
        // Cache cleanup is best-effort in development.
      })
    }
  })
}

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // PWA registration is optional; the app should still run normally.
    })
  })
}
