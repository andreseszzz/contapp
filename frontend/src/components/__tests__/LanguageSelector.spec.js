import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createPinia } from 'pinia'

const i18n = createI18n({
  locale: 'es',
  fallbackLocale: 'en',
  messages: {
    es: { nav: { language: 'Idioma', logout: 'Cerrar sesión' } },
    en: { nav: { language: 'Language', logout: 'Logout' } }
  }
})

describe('i18n setup', () => {
  it('has Spanish and English locales', () => {
    expect(i18n.global.availableLocales).toContain('es')
    expect(i18n.global.availableLocales).toContain('en')
  })
})
