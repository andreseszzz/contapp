<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api.js'

const { t } = useI18n()

const products = ref([])
const loading = ref(true)
const editing = ref(null)
const form = ref({
  code_reference: '',
  name: '',
  description: '',
  price: 0,
  unit_measure_code: '94',
  standard_code: '999',
  tax_rate: 19,
  tax_code: '01',
})

onMounted(loadProducts)

async function loadProducts() {
  loading.value = true
  try {
    const { data } = await api.get('/products')
    products.value = data
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editing.value = null
  form.value = {
    code_reference: '',
    name: '',
    description: '',
    price: 0,
    unit_measure_code: '94',
    standard_code: '999',
    tax_rate: 19,
    tax_code: '01',
  }
}

function editProduct(product) {
  editing.value = product.id
  form.value = { ...product }
}

async function saveProduct() {
  try {
    const payload = { ...form.value, price: Number(form.value.price), tax_rate: Number(form.value.tax_rate) }
    if (editing.value) {
      await api.put(`/products/${editing.value}`, payload)
    } else {
      await api.post('/products', payload)
    }
    resetForm()
    await loadProducts()
  } catch (err) {
    alert(err.response?.data?.detail || t('common.error'))
  }
}

async function deleteProduct(id) {
  if (!confirm(t('common.delete') + '?')) return
  try {
    await api.delete(`/products/${id}`)
    await loadProducts()
  } catch (err) {
    alert(err.response?.data?.detail || t('common.error'))
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ t('products.title') }}</h1>

    <form class="bg-card p-4 rounded-lg shadow mb-6 grid grid-cols-1 md:grid-cols-3 gap-4" @submit.prevent="saveProduct">
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('products.code') }}</label>
        <input v-model="form.code_reference" required class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('products.name') }}</label>
        <input v-model="form.name" required class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('products.price') }}</label>
        <input v-model.number="form.price" type="number" required min="0" step="0.01" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">{{ t('products.taxRate') }} (%)</label>
        <input v-model.number="form.tax_rate" type="number" required min="0" step="0.01" class="w-full border rounded-md px-3 py-2" />
      </div>
      <div class="md:col-span-2 flex items-end gap-2">
        <button type="submit" class="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark">
          {{ t('products.save') }}
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
          <th class="px-4 py-3">{{ t('products.code') }}</th>
          <th class="px-4 py-3">{{ t('products.name') }}</th>
          <th class="px-4 py-3">{{ t('products.price') }}</th>
          <th class="px-4 py-3">{{ t('products.taxRate') }}</th>
          <th class="px-4 py-3">{{ t('common.actions') }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-for="product in products" :key="product.id">
          <td class="px-4 py-3">{{ product.code_reference }}</td>
          <td class="px-4 py-3">{{ product.name }}</td>
          <td class="px-4 py-3">${{ product.price.toLocaleString() }}</td>
          <td class="px-4 py-3">{{ product.tax_rate }}%</td>
          <td class="px-4 py-3 flex gap-2">
            <button class="text-primary hover:underline" @click="editProduct(product)">{{ t('common.edit') }}</button>
            <button class="text-danger hover:underline" @click="deleteProduct(product.id)">{{ t('common.delete') }}</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
