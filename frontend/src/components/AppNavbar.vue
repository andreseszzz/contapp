<script setup>
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()

const navLinks = [
  { to: '/', label: 'dashboard' },
  { to: '/clients', label: 'clients' },
  { to: '/products', label: 'products' },
  { to: '/invoices', label: 'invoices' },
  { to: '/invoices/new', label: 'newInvoice' },
  { to: '/reports', label: 'reports' },
]

const isPublic = computed(() => route.meta.public)

async function logout() {
  await auth.logout()
  router.push('/login')
}

function setLanguage(lang) {
  locale.value = lang
  localStorage.setItem('contapp_locale', lang)
}
</script>

<template>
  <nav class="bg-card border-b border-gray-200 px-6 py-4 shadow-sm">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xl font-bold text-primary">Contapp</span>
      </div>

      <div v-if="!isPublic" class="hidden md:flex items-center gap-6">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="text-sm font-medium text-secondary hover:text-primary transition"
        >
          {{ t(`nav.${link.label}`) }}
        </RouterLink>
      </div>

      <div class="flex items-center gap-4">
        <select
          class="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white"
          :value="locale"
          @change="setLanguage($event.target.value)"
        >
          <option value="es">ES</option>
          <option value="en">EN</option>
        </select>

        <div v-if="auth.isAuthenticated" class="flex items-center gap-3">
          <span class="text-sm text-muted hidden sm:inline">{{ auth.user?.email }}</span>
          <button
            class="text-sm text-danger hover:underline"
            @click="logout"
          >
            {{ t('nav.logout') }}
          </button>
        </div>
        <div v-else class="flex items-center gap-3">
          <RouterLink to="/login" class="text-sm text-primary hover:underline">
            {{ t('nav.login') }}
          </RouterLink>
          <RouterLink to="/register" class="text-sm text-primary hover:underline">
            {{ t('nav.register') }}
          </RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>
