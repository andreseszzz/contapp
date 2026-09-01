<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api.js'

const { t } = useI18n()

const invoices = ref([])
const loading = ref(true)

onMounted(loadInvoices)

async function loadInvoices() {
  loading.value = true
  try {
    const { data } = await api.get('/invoices')
    invoices.value = data
  } finally {
    loading.value = false
  }
}

async function emitInvoice(id) {
  try {
    await api.post(`/invoices/${id}/emit`)
    await loadInvoices()
  } catch (err) {
    alert(err.response?.data?.detail || t('common.error'))
  }
}

function statusClass(status) {
  if (status === 'validated') return 'text-success'
  if (status === 'rejected') return 'text-danger'
  return 'text-warning'
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">{{ t('invoices.title') }}</h1>
      <RouterLink to="/invoices/new" class="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark">
        {{ t('invoices.new') }}
      </RouterLink>
    </div>

    <div v-if="loading" class="text-muted">{{ t('common.loading') }}</div>

    <table v-else class="w-full bg-card rounded-lg shadow overflow-hidden">
      <thead class="bg-gray-100 text-left text-sm uppercase text-muted">
        <tr>
          <th class="px-4 py-3">{{ t('invoices.reference') }}</th>
          <th class="px-4 py-3">{{ t('invoices.client') }}</th>
          <th class="px-4 py-3">{{ t('invoices.status') }}</th>
          <th class="px-4 py-3">{{ t('invoices.total') }}</th>
          <th class="px-4 py-3">{{ t('common.actions') }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-for="invoice in invoices" :key="invoice.id">
          <td class="px-4 py-3">{{ invoice.reference_code }}</td>
          <td class="px-4 py-3">{{ invoice.client_id }}</td>
          <td class="px-4 py-3 font-medium" :class="statusClass(invoice.status)">
            {{ t(`invoices.${invoice.status}`) }}
          </td>
          <td class="px-4 py-3">${{ invoice.total_amount.toLocaleString() }}</td>
          <td class="px-4 py-3">
            <button
              v-if="invoice.status === 'draft'"
              class="text-primary hover:underline"
              @click="emitInvoice(invoice.id)"
            >
              {{ t('invoices.emit') }}
            </button>
            <a v-if="invoice.pdf_url" :href="invoice.pdf_url" target="_blank" class="text-primary hover:underline ml-2">PDF</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
