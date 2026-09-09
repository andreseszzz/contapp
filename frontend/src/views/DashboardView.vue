<script setup>
import { ref, onMounted, computed, watch } from 'vue'
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
const monthly = ref({ labels: [], sales: [], taxes: [] })
const statusCounts = ref({ draft: 0, pending: 0, validated: 0, rejected: 0 })
const statusFilter = ref('validated')
const loading = ref(true)
const chartLoading = ref(false)
const chartError = ref(null)

const statusOptions = [
  { value: 'all', label: 'dashboard.all' },
  { value: 'draft', label: 'dashboard.draft' },
  { value: 'pending', label: 'dashboard.pending' },
  { value: 'validated', label: 'dashboard.validated' },
  { value: 'rejected', label: 'dashboard.rejected' },
]

const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

const lineChartOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: false },
    zoom: { enabled: false },
    fontFamily: 'inherit',
  },
  title: {
    text: t('dashboard.salesOverTime'),
    align: 'left',
    style: { fontSize: '16px', fontWeight: 600 },
  },
  colors: ['#2563eb', '#16a34a'],
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { shadeIntensity: 0.4, opacityFrom: 0.4, opacityTo: 0.05 } },
  xaxis: {
    categories: monthly.value.labels,
    title: { text: 'Mes' },
  },
  yaxis: {
    labels: {
      formatter: (value) => (value ? `$${Number(value).toLocaleString()}` : '$0'),
    },
  },
  tooltip: {
    y: {
      formatter: (value) => (value ? currencyFormatter.format(value) : '$0'),
    },
  },
  legend: { position: 'top' },
  noData: {
    text: t('dashboard.noData'),
  },
}))

const lineChartSeries = computed(() => [
  { name: t('dashboard.totalSales'), data: monthly.value.sales },
  { name: t('dashboard.totalTax'), data: monthly.value.taxes },
])

const donutChartOptions = computed(() => ({
  chart: { type: 'donut', fontFamily: 'inherit' },
  title: {
    text: t('dashboard.invoicesByStatus'),
    align: 'left',
    style: { fontSize: '16px', fontWeight: 600 },
  },
  labels: [
    t('dashboard.draft'),
    t('dashboard.pending'),
    t('dashboard.validated'),
    t('dashboard.rejected'),
  ],
  colors: ['#6b7280', '#f59e0b', '#16a34a', '#ef4444'],
  legend: { position: 'bottom' },
  noData: { text: t('dashboard.noData') },
}))

const donutChartSeries = computed(() => [
  statusCounts.value.draft,
  statusCounts.value.pending,
  statusCounts.value.validated,
  statusCounts.value.rejected,
])

async function loadDashboard() {
  loading.value = true
  try {
    const [salesRes, clientsRes, productsRes, invoicesRes, statusRes] = await Promise.all([
      api.get('/reports/sales-summary'),
      api.get('/clients'),
      api.get('/products'),
      api.get('/invoices'),
      api.get('/reports/sales-by-status'),
    ])
    stats.value = salesRes.data
    counts.value = {
      clients: clientsRes.data.length,
      products: productsRes.data.length,
      invoices: invoicesRes.data.length,
    }
    statusCounts.value = statusRes.data
  } finally {
    loading.value = false
  }
}

async function loadMonthlySales() {
  chartLoading.value = true
  chartError.value = null
  try {
    const { data } = await api.get('/reports/monthly-sales', {
      params: { status: statusFilter.value },
    })
    monthly.value = data
  } catch (err) {
    chartError.value = err.response?.data?.detail || err.message
  } finally {
    chartLoading.value = false
  }
}

onMounted(() => {
  loadDashboard()
  loadMonthlySales()
})

watch(statusFilter, () => {
  loadMonthlySales()
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">{{ t('dashboard.title') }}</h1>
    <p class="text-muted mb-6">{{ t('dashboard.welcome') }}, {{ auth.user?.full_name || auth.user?.email }}</p>

    <div v-if="loading" class="text-muted">{{ t('common.loading') }}</div>

    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
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

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div class="lg:col-span-2 bg-card p-4 rounded-lg shadow border border-gray-100">
          <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
            <h2 class="text-lg font-semibold">{{ t('dashboard.salesOverTime') }}</h2>
            <div class="flex items-center gap-2">
              <label class="text-sm text-muted">{{ t('dashboard.statusFilter') }}</label>
              <select
                v-model="statusFilter"
                class="border rounded-md px-3 py-2 text-sm bg-white"
                :disabled="chartLoading"
              >
                <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
                  {{ t(opt.label) }}
                </option>
              </select>
            </div>
          </div>
          <div v-if="chartLoading" class="text-muted">{{ t('common.loading') }}</div>
          <div v-else-if="chartError" class="text-red-600">{{ chartError }}</div>
          <apexchart
            v-else
            type="area"
            height="350"
            :options="lineChartOptions"
            :series="lineChartSeries"
          />
        </div>

        <div class="bg-card p-4 rounded-lg shadow border border-gray-100">
          <h2 class="text-lg font-semibold mb-4">{{ t('dashboard.invoicesByStatus') }}</h2>
          <apexchart
            type="donut"
            height="350"
            :options="donutChartOptions"
            :series="donutChartSeries"
          />
        </div>
      </div>
    </template>
  </div>
</template>
