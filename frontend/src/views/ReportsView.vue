<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api.js'

const { t } = useI18n()

const startDate = ref('')
const endDate = ref('')
const sales = ref(null)
const taxes = ref(null)
const receivable = ref(null)
const loading = ref(false)

async function generateReports() {
  loading.value = true
  try {
    const params = {}
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value

    const [salesRes, taxesRes, receivableRes] = await Promise.all([
      api.get('/reports/sales-summary', { params }),
      api.get('/reports/taxes', { params }),
      api.get('/reports/accounts-receivable'),
    ])

    sales.value = salesRes.data
    taxes.value = taxesRes.data
    receivable.value = receivableRes.data
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ t('reports.title') }}</h1>

    <div class="bg-card p-4 rounded-lg shadow mb-6 flex flex-wrap gap-4 items-end">
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('reports.startDate') }}</label>
        <input v-model="startDate" type="date" class="border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('reports.endDate') }}</label>
        <input v-model="endDate" type="date" class="border rounded-md px-3 py-2" />
      </div>
      <button
        class="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark"
        :disabled="loading"
        @click="generateReports"
      >
        {{ loading ? t('common.loading') : t('reports.generate') }}
      </button>
    </div>

    <div v-if="sales" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('reports.salesSummary') }}</p>
        <p class="text-2xl font-bold">${{ sales.total_sales.toLocaleString() }}</p>
        <p class="text-sm text-muted">{{ sales.invoice_count }} facturas</p>
      </div>
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('reports.taxes') }}</p>
        <p class="text-2xl font-bold">${{ taxes.total_iva.toLocaleString() }}</p>
        <p class="text-sm text-muted">{{ taxes.invoice_count }} facturas validadas</p>
      </div>
      <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
        <p class="text-sm text-muted">{{ t('reports.accountsReceivable') }}</p>
        <p class="text-2xl font-bold">${{ receivable.total_accounts_receivable.toLocaleString() }}</p>
        <p class="text-sm text-muted">{{ receivable.invoice_count }} facturas</p>
      </div>
    </div>
  </div>
</template>
