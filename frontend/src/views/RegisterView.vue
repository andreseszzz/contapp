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
const fullName = ref('')
const error = ref('')
const confirmationRequired = ref(false)

async function handleRegister() {
  error.value = ''
  confirmationRequired.value = false
  try {
    const result = await auth.register(email.value, password.value, fullName.value)
    if (result?.confirmationRequired) {
      confirmationRequired.value = true
    } else {
      router.push('/')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || t('common.error')
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-12 bg-card p-8 rounded-lg shadow">
    <h1 class="text-2xl font-bold text-center mb-6">{{ t('auth.register') }}</h1>

    <div v-if="confirmationRequired" class="bg-blue-50 border border-blue-200 text-blue-800 p-4 rounded-md mb-4">
      <p class="font-semibold mb-1">{{ t('auth.confirmRequired') }}</p>
      <p class="text-sm">{{ t('auth.checkEmail') }}</p>
      <RouterLink to="/login" class="mt-3 inline-block text-sm text-primary hover:underline">
        {{ t('auth.login') }}
      </RouterLink>
    </div>

    <form v-else class="space-y-4" @submit.prevent="handleRegister">
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('auth.fullName') }}</label>
        <input v-model="fullName" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('auth.email') }}</label>
        <input v-model="email" type="email" required class="w-full border border-gray-300 rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('auth.password') }}</label>
        <input v-model="password" type="password" required minlength="6" class="w-full border border-gray-300 rounded-md px-3 py-2" />
      </div>

      <p v-if="error" class="text-danger text-sm">{{ error }}</p>

      <button type="submit" class="w-full bg-primary text-white rounded-md py-2 font-medium hover:bg-primary-dark transition">
        {{ t('auth.register') }}
      </button>
    </form>

    <p v-if="!confirmationRequired" class="text-center text-sm mt-4">
      {{ t('auth.hasAccount') }}
      <RouterLink to="/login" class="text-primary hover:underline">{{ t('auth.login') }}</RouterLink>
    </p>
  </div>
</template>
