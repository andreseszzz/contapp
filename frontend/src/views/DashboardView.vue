<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useI18n } from 'vue-i18n'
import api from '@/services/api.js'

const auth = useAuthStore()
const { t } = useI18n()

const stats = ref({
  total_sales: 0,
  total_tax: 0,
  invoice_count: 0,
})
const counts = ref({ clients: 0, products: 0, invoices: 0 })
const loading = ref(true)

onMounted(async () => {
  try {
    const [salesRes, clientsRes, productsRes, invoicesRes] = await Promise.all([
      api.get('/reports/sales-summary'),
      api.get('/clients'),
      api.get('/products'),
      api.get('/invoices'),
    ])
    stats.value = salesRes.data
    counts.value = {
      clients: clientsRes.data.length,
      products: productsRes.data.length,
      invoices: invoicesRes.data.length,
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">{{ t('dashboard.title') }}</h1>
    <p class="text-muted mb-6">{{ t('dashboard.welcome') }}, {{ auth.user?.email }}</p>

    <div v-if="loading" class="text-muted">{{ t('common.loading') }}</div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('dashboard.totalSales') }}</p>
        <p class="text-2xl font-bold">${{ stats.total_sales.toLocaleString() }}</p>
      </div>
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('dashboard.totalTax') }}</p>
        <p class="text-2xl font-bold">${{ stats.total_tax.toLocaleString() }}</p>
      </div>
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('dashboard.invoices') }}</p>
        <p class="text-2xl font-bold">{{ counts.invoices }}</p>
      </div>
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('dashboard.clients') }}</p>
        <p class="text-2xl font-bold">{{ counts.clients }}</p>
      </div>
    </div>
  </div>
</template>
