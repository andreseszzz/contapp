<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const auth = useAuthStore()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.message || t('common.error')
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-12 bg-card p-8 rounded-lg shadow">
    <h1 class="text-2xl font-bold text-center mb-2">{{ t('auth.welcome') }}</h1>
    <p class="text-center text-muted mb-6">{{ t('auth.subtitle') }}</p>

    <form class="space-y-4" @submit.prevent="handleLogin">
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('auth.email') }}</label>
        <input v-model="email" type="email" required class="w-full border border-gray-300 rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('auth.password') }}</label>
        <input v-model="password" type="password" required class="w-full border border-gray-300 rounded-md px-3 py-2" />
      </div>

      <p v-if="error" class="text-danger text-sm">{{ error }}</p>

      <button type="submit" class="w-full bg-primary text-white rounded-md py-2 font-medium hover:bg-primary-dark transition">
        {{ t('auth.login') }}
      </button>
    </form>

    <p class="text-center text-sm mt-4">
      {{ t('auth.noAccount') }}
      <RouterLink to="/register" class="text-primary hover:underline">{{ t('auth.register') }}</RouterLink>
    </p>
  </div>
</template>
