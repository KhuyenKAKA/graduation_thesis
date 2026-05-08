<template>
  <div class="comparison-wrapper">
    <Header />

    <div class="comparison-content">
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-inner">
          <h1 class="page-title">University Comparison</h1>
          <p class="page-subtitle" v-if="tableRows.length > 0">
            Comparing {{ tableRows.length }} universities across key metrics
          </p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>Loading comparison data...</span>
      </div>

      <!-- Empty state -->
      <div v-else-if="tableRows.length === 0" class="empty-state">
        <div class="empty-icon">📊</div>
        <p>No universities selected for comparison.</p>
        <button class="btn-back" @click="router.push('/universities')">Go to Rankings</button>
      </div>

      <div v-show="!loading && tableRows.length > 0">
        <!-- Comparison Table -->
        <div class="table-section">
          <div class="table-title-bar">
            <h2 class="table-title">Student Ratio Information Table</h2>
          </div>
          <div class="table-wrap">
            <table class="comparison-table">
              <thead>
                <tr>
                  <th class="col-university">University</th>
                  <th>Tuition Fee</th>
                  <th>Scholarship</th>
                  <th>Domestic Student Rate (%)</th>
                  <th>International Student Rate (%)</th>
                  <th>Total Students</th>
                  <th>Undergraduate Students (%)</th>
                  <th>Postgraduate Students (%)</th>
                  <th>Total International Students</th>
                  <th>International Undergraduate (%)</th>
                  <th>International Postgraduate (%)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableRows" :key="row.id">
                  <td class="col-university">{{ row.name }}</td>
                  <td>{{ row.fee }}</td>
                  <td>{{ row.scholarship }}</td>
                  <td>{{ row.domestic }}</td>
                  <td>{{ row.international }}</td>
                  <td>{{ row.total_stu }}</td>
                  <td>{{ row.ug_rate }}</td>
                  <td>{{ row.pg_rate }}</td>
                  <td>{{ row.inter_total }}</td>
                  <td>{{ row.inter_ug_rate }}</td>
                  <td>{{ row.inter_pg_rate }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Entry Criteria Chart -->
        <div class="chart-section">
          <div class="chart-title-bar">
            <h2 class="chart-title">Entry Criteria Index</h2>
            <div class="degree-toggle">
              <button
                :class="['toggle-btn', { active: activeDegree === 1 }]"
                @click="switchDegree(1)"
              >Bachelor</button>
              <button
                :class="['toggle-btn', { active: activeDegree === 2 }]"
                @click="switchDegree(2)"
              >Master</button>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { universityAPI } from '@/services/api'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, LineController, Title, Tooltip, Legend)

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const tableRows = ref([])
const chartCanvas = ref(null)
const activeDegree = ref(1)
// entryData[degreeType] = array of { id, name, sat, gre, ... }
const entryData = ref({ 1: [], 2: [] })
let chartInstance = null

const LINE_COLORS = [
  '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'
]

const MOCK_UNIVERSITIES = [
  {
    id: 1, name: 'MIT',
    fee: 100, scholarship: 100, domestic: 100, international: 100,
    total_stu: 11500, ug_rate: 60, pg_rate: 40, inter_total: 30, inter_ug_rate: 20, inter_pg_rate: 10,
    entry: { sat: 1200, gre: 316, gmat: 555, act: 33, atar: 92, gpa: 3.9, toefl: 100, ielts: 7.0 }
  },
  {
    id: 2, name: 'Imperial College London',
    fee: 95, scholarship: 99.6, domestic: 99.3, international: 100,
    total_stu: 19000, ug_rate: 55, pg_rate: 45, inter_total: 35, inter_ug_rate: 25, inter_pg_rate: 10,
    entry: { sat: 1250, gre: 320, gmat: 635, act: 32, atar: 95, gpa: 3.8, toefl: 106, ielts: 7.5 }
  },
  {
    id: 3, name: 'Stanford University',
    fee: 98, scholarship: 98.5, domestic: 99.5, international: 95,
    total_stu: 17000, ug_rate: 50, pg_rate: 50, inter_total: 25, inter_ug_rate: 15, inter_pg_rate: 10,
    entry: { sat: 1150, gre: 322, gmat: 570, act: 34, atar: 94, gpa: 3.9, toefl: 100, ielts: 7.0 }
  },
  {
    id: 4, name: 'ETH Zurich',
    fee: 90, scholarship: 95, domestic: 100, international: 90,
    total_stu: 24000, ug_rate: 65, pg_rate: 35, inter_total: 40, inter_ug_rate: 30, inter_pg_rate: 10,
    entry: { sat: 1000, gre: 310, gmat: 510, act: 32, atar: 85, gpa: 3.7, toefl: 95, ielts: 7.0 }
  },
  {
    id: 5, name: 'National University of SGP',
    fee: 92, scholarship: 97, domestic: 95, international: 98,
    total_stu: 35000, ug_rate: 70, pg_rate: 30, inter_total: 20, inter_ug_rate: 10, inter_pg_rate: 10,
    entry: { sat: 1450, gre: 318, gmat: 590, act: 34, atar: 90, gpa: 3.8, toefl: 100, ielts: 6.5 }
  }
]

const fmt = (v) => (v != null && v !== '' ? v : 'Not available')
const fmtScholarship = (v) => (v === true || v === 'true' || v === 1 ? 'Yes' : v === false || v === 'false' || v === 0 ? 'No' : 'Not available')

const buildChart = (entries) => {
  nextTick(() => {
    const canvas = chartCanvas.value
    if (!canvas) {
      console.warn('[Comparison] chartCanvas ref is null')
      return
    }
    if (chartInstance) { chartInstance.destroy(); chartInstance = null }

    const ctx = canvas.getContext('2d')
    const labels = ['SAT', 'GRE', 'GMAT', 'ACT', 'ATAR', 'GPA', 'TOEFL', 'IELTS']
    const datasets = entries.map((e, i) => ({
      label: e.name,
      data: [
        e.sat ?? null, e.gre ?? null, e.gmat ?? null,
        e.act ?? null, e.atar ?? null, e.gpa ?? null,
        e.toefl ?? null, e.ielts ?? null
      ],
      borderColor: LINE_COLORS[i % LINE_COLORS.length],
      backgroundColor: LINE_COLORS[i % LINE_COLORS.length],
      pointRadius: 5,
      pointHoverRadius: 7,
      tension: 0,
      fill: false,
      spanGaps: true
    }))
    chartInstance = new ChartJS(ctx, {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right' },
          title: { display: false }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#e0e0e0' } },
          x: { grid: { color: '#e0e0e0' } }
        }
      }
    })
  })
}

const switchDegree = (degree) => {
  activeDegree.value = degree
  buildChart(entryData.value[degree])
}

const loadComparison = async (ids) => {
  loading.value = true
  try {
    const [compRes, chartRes] = await Promise.all([
      universityAPI.compare(ids),
      universityAPI.getChartData(ids),
    ])
    const compData = compRes.data
    const chartDataRaw = chartRes.data  // [{ id, name, bachelor: {...}, master: {...} }]

    tableRows.value = compData.map((d) => ({
      id: d.id,
      name: d.name || 'Not available',
      fee: fmt(d.fee),
      scholarship: fmtScholarship(d.scholarship),
      domestic: fmt(d.domestic),
      international: fmt(d.international),
      total_stu: fmt(d.total_stu),
      ug_rate: fmt(d.ug_rate),
      pg_rate: fmt(d.pg_rate),
      inter_total: fmt(d.inter_total),
      inter_ug_rate: fmt(d.inter_ug_rate),
      inter_pg_rate: fmt(d.inter_pg_rate),
    }))

    const toEntries = (degreeKey) =>
      chartDataRaw
        .filter(c => c[degreeKey] != null)
        .map(c => ({ name: c.name, ...c[degreeKey] }))

    entryData.value[1] = toEntries('bachelor')
    entryData.value[2] = toEntries('master')
  } catch (err) {
    const detail = err.response?.data?.detail || 'Cannot connect to the database. Please try again later.'
    message.error(detail)
  } finally {
    loading.value = false
  }
  buildChart(entryData.value[activeDegree.value])
}

const loadMockData = () => {
  tableRows.value = MOCK_UNIVERSITIES.map(u => ({
    ...u,
    fee: fmt(u.fee),
    scholarship: fmtScholarship(u.scholarship),
    domestic: fmt(u.domestic),
    international: fmt(u.international),
    total_stu: fmt(u.total_stu),
    ug_rate: fmt(u.ug_rate),
    pg_rate: fmt(u.pg_rate),
    inter_total: fmt(u.inter_total),
    inter_ug_rate: fmt(u.inter_ug_rate),
    inter_pg_rate: fmt(u.inter_pg_rate)
  }))
  const mockEntries = MOCK_UNIVERSITIES.map(u => ({ ...u.entry, id: u.id, name: u.name }))
  entryData.value[1] = mockEntries
  entryData.value[2] = mockEntries
  buildChart(entryData.value[activeDegree.value])
}

onBeforeUnmount(() => {
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }
})

onMounted(() => {
  const idsParam = route.query.ids
  if (idsParam) {
    const ids = idsParam.split(',').map(Number).filter(Boolean)
    if (ids.length >= 1) {
      loadComparison(ids)
      return
    }
  }
  // Fallback: sessionStorage
  const saved = sessionStorage.getItem('compareList')
  if (saved) {
    try {
      const ids = JSON.parse(saved).map(Number).filter(Boolean)
      if (ids.length >= 1) {
        loadComparison(ids)
        return
      }
    } catch {}
  }
  // No IDs at all — show mock data
  loadMockData()
})
</script>

<style scoped>
.comparison-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.comparison-content {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 0 24px 48px;
}

/* Page Header */
.page-header {
  padding: 32px 0 24px;
}
.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}
.page-subtitle {
  color: #6b7280;
  font-size: 15px;
  margin: 0;
}

/* Loading */
.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  padding: 80px 0;
  color: #6b7280;
  font-size: 16px;
}
.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e5e7eb;
  border-top-color: #1a56db;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Empty state */
.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #6b7280;
}
.empty-icon { font-size: 48px; margin-bottom: 16px; }

/* Table */
.table-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  overflow: hidden;
  margin-bottom: 32px;
}
.table-title-bar {
  background: #eef2ff;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
}
.table-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}
.table-wrap {
  overflow-x: auto;
}
.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
.comparison-table thead tr {
  background: #f9fafb;
}
.comparison-table th {
  padding: 12px 14px;
  text-align: center;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  border-right: 1px solid #e5e7eb;
  white-space: nowrap;
  font-size: 13px;
}
.comparison-table th:last-child,
.comparison-table td:last-child { border-right: none; }
.comparison-table td {
  padding: 12px 14px;
  text-align: center;
  border-bottom: 1px solid #e5e7eb;
  border-right: 1px solid #e5e7eb;
  color: #374151;
}
.comparison-table tbody tr:last-child td { border-bottom: none; }
.col-university {
  text-align: left !important;
  font-weight: 600;
  white-space: nowrap;
  min-width: 180px;
  position: sticky;
  left: 0;
  background: #fff;
  z-index: 1;
}
thead .col-university { background: #f9fafb; z-index: 2; }

/* Chart */
.chart-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  overflow: hidden;
}
.chart-title-bar {
  background: #eef2ff;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.chart-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}
.degree-toggle {
  display: flex;
  gap: 8px;
}
.toggle-btn {
  padding: 6px 20px;
  border-radius: 6px;
  border: 1.5px solid #1a56db;
  background: #fff;
  color: #1a56db;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.toggle-btn:hover { background: #eef2ff; }
.toggle-btn.active { background: #1a56db; color: #fff; }
.chart-wrap {
  padding: 32px 24px 24px;
  height: 400px;
  position: relative;
}
</style>
