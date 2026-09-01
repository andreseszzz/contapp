<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api.js'

const router = useRouter()
const { t } = useI18n()

const clients = ref([])
const products = ref([])
const loading = ref(true)

const form = ref({
  client_id: '',
  reference_code: '',
  document: '01',
  numbering_range_id: 1,
  operation_type: '10',
  observation: '',
  items: [],
})

const selectedItem = ref({
  product_id: '',
  quantity: 1,
  discount_rate: 0,
})

onMounted(async () => {
  try {
    const [clientsRes, productsRes] = await Promise.all([
      api.get('/clients'),
      api.get('/products'),
    ])
    clients.value = clientsRes.data
    products.value = productsRes.data
  } finally {
    loading.value = false
  }
})

function addItem() {
  if (!selectedItem.value.product_id || selectedItem.value.quantity <= 0) return
  const product = products.value.find((p) => p.id === selectedItem.value.product_id)
  if (!product) return
  form.value.items.push({ ...selectedItem.value })
  selectedItem.value = { product_id: '', quantity: 1, discount_rate: 0 }
}

function removeItem(index) {
  form.value.items.splice(index, 1)
}

function getProductName(id) {
  return products.value.find((p) => p.id === id)?.name || id
}

async function createInvoice() {
  try {
    await api.post('/invoices', form.value)
    router.push('/invoices')
  } catch (err) {
    alert(err.response?.data?.detail || t('common.error'))
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ t('invoices.new') }}</h1>

    <div v-if="loading" class="text-muted">{{ t('common.loading') }}</div>

    <form v-else class="bg-card p-6 rounded-lg shadow space-y-6" @submit.prevent="createInvoice">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('invoices.client') }}</label>
          <select v-model="form.client_id" required class="w-full border rounded-md px-3 py-2">
            <option value="" disabled>{{ t('common.search') }}</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.company || client.trade_name || client.identification }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('invoices.reference') }}</label>
          <input v-model="form.reference_code" required class="w-full border rounded-md px-3 py-2" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">{{ t('invoices.items') }}</label>
        <div class="flex gap-2 items-end mb-2">
          <select v-model="selectedItem.product_id" class="border rounded-md px-3 py-2 flex-1">
            <option value="" disabled>{{ t('products.title') }}</option>
            <option v-for="product in products" :key="product.id" :value="product.id">
              {{ product.name }} - ${{ product.price.toLocaleString() }}
            </option>
          </select>
          <input
            v-model.number="selectedItem.quantity"
            type="number"
            min="1"
            step="0.01"
            class="border rounded-md px-3 py-2 w-24"
            :placeholder="t('invoices.quantity')"
          />
          <input
            v-model.number="selectedItem.discount_rate"
            type="number"
            min="0"
            max="100"
            step="0.01"
            class="border rounded-md px-3 py-2 w-24"
            :placeholder="t('invoices.discount') + '%'"
          />
          <button type="button" class="bg-secondary text-white px-4 py-2 rounded-md" @click="addItem">
            {{ t('invoices.addItem') }}
          </button>
        </div>

        <table class="w-full text-sm">
          <thead class="bg-gray-100 text-muted">
            <tr>
              <th class="px-3 py-2 text-left">{{ t('products.name') }}</th>
              <th class="px-3 py-2 text-left">{{ t('invoices.quantity') }}</th>
              <th class="px-3 py-2 text-left">{{ t('invoices.discount') }}</th>
              <th class="px-3 py-2 text-left">{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(item, index) in form.items" :key="index">
              <td class="px-3 py-2">{{ getProductName(item.product_id) }}</td>
              <td class="px-3 py-2">{{ item.quantity }}</td>
              <td class="px-3 py-2">{{ item.discount_rate }}%</td>
              <td class="px-3 py-2">
                <button type="button" class="text-danger hover:underline" @click="removeItem(index)">
                  {{ t('common.delete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <button type="submit" class="bg-primary text-white px-6 py-2 rounded-md hover:bg-primary-dark">
        {{ t('invoices.create') }}
      </button>
    </form>
  </div>
</template>
