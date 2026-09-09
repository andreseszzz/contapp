import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import VueApexCharts from 'vue3-apexcharts'
import router from './router'
import App from './App.vue'
import './style.css'

import en from './i18n/en.json'
import es from './i18n/es.json'

const i18n = createI18n({
  locale: 'es',
  fallbackLocale: 'en',
  messages: { en, es }
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(VueApexCharts)

app.mount('#app')
