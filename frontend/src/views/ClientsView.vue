<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api.js'

const { t } = useI18n()

const clients = ref([])
const loading = ref(true)
const editing = ref(null)
const form = ref({
  identification_document_code: '31',
  identification: '',
  company: '',
  trade_name: '',
  address: '',
  email: '',
  phone: '',
  legal_organization_code: '1',
  tribute_code: 'ZZ',
  municipality_code: '11001',
})

onMounted(loadClients)

async function loadClients() {
  loading.value = true
  try {
    const { data } = await api.get('/clients')
    clients.value = data
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editing.value = null
  form.value = {
    identification_document_code: '31',
    identification: '',
    company: '',
    trade_name: '',
    address: '',
    email: '',
    phone: '',
    legal_organization_code: '1',
    tribute_code: 'ZZ',
    municipality_code: '11001',
  }
}

function editClient(client) {
  editing.value = client.id
  form.value = { ...client }
}

async function saveClient() {
  try {
    if (editing.value) {
      await api.put(`/clients/${editing.value}`, form.value)
    } else {
      await api.post('/clients', form.value)
    }
    resetForm()
    await loadClients()
  } catch (err) {
    alert(err.response?.data?.detail || t('common.error'))
  }
}

async function deleteClient(id) {
  if (!confirm(t('common.delete') + '?')) return
  try {
    await api.delete(`/clients/${id}`)
    await loadClients()
  } catch (err) {
    alert(err.response?.data?.detail || t('common.error'))
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ t('clients.title') }}</h1>

    <form class="bg-card p-4 rounded-lg shadow mb-6 grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="saveClient">
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('clients.identification') }}</label>
        <input v-model="form.identification" required class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('clients.company') }}</label>
        <input v-model="form.company" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('clients.tradeName') }}</label>
        <input v-model="form.trade_name" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('clients.email') }}</label>
        <input v-model="form.email" type="email" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('clients.phone') }}</label>
        <input v-model="form.phone" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('clients.address') }}</label>
        <input v-model="form.address" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div class="md:col-span-2 flex gap-2">
        <button type="submit" class="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark">
          {{ t('clients.save') }}
        </button>
        <button v-if="editing" type="button" class="text-secondary hover:underline" @click="resetForm">
          {{ t('common.cancel') }}
        </button>
      </div>
    </form>

    <div v-if="loading" class="text-muted">{{ t('common.loading') }}</div>

    <table v-else class="w-full bg-card rounded-lg shadow overflow-hidden">
      <thead class="bg-gray-100 text-left text-sm uppercase text-muted">
        <tr>
          <th class="px-4 py-3">{{ t('clients.identification') }}</th>
          <th class="px-4 py-3">{{ t('clients.company') }}</th>
          <th class="px-4 py-3">{{ t('clients.email') }}</th>
          <th class="px-4 py-3">{{ t('common.actions') }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-for="client in clients" :key="client.id">
          <td class="px-4 py-3">{{ client.identification }}</td>
          <td class="px-4 py-3">{{ client.company || client.trade_name || '-' }}</td>
          <td class="px-4 py-3">{{ client.email || '-' }}</td>
          <td class="px-4 py-3 flex gap-2">
            <button class="text-primary hover:underline" @click="editClient(client)">{{ t('common.edit') }}</button>
            <button class="text-danger hover:underline" @click="deleteClient(client.id)">{{ t('common.delete') }}</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
