<template>
  <div class="universities-page">
    <Header />

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">UC World University Rankings 2026: Top global universities</h1>
        <p class="hero-desc">
          Discover the top universities around the world with the UC World University Rankings 2026.
        </p>
        <p class="hero-desc">
          Over 1,500 of the world's top universities are included in the 2026 edition of the UC World University Rankings,
          with over 100 locations represented around the world....
        </p>
        <a href="#" class="read-more">Read more</a>

        <div v-if="!isAuthenticated" class="register-banner">
          <span>Register for free site membership to access direct university comparisons and more</span>
          <button class="btn-register" @click="router.push('/signup')">Register today!</button>
        </div>
      </div>
    </section>

    <!-- Search & Filter Bar -->
    <section class="search-bar-section">
      <div class="search-bar-container">
        <div class="view-toggle">
          <button :class="['toggle-btn', { active: viewMode === 'quick' }]" @click="viewMode = 'quick'">
            <span>☰</span> Quick View
          </button>
          <button :class="['toggle-btn', { active: viewMode === 'table' }]" @click="viewMode = 'table'">
            <span>▦</span> Table View
          </button>
        </div>
        <div class="search-input-wrap">
          <img src="/assets/search.png" alt="Search" class="search-icon-inner" />
          <input v-model="searchQuery" placeholder="Search" @keyup.enter="handleSearch" @input="onSearchInput" />
          <button v-if="searchQuery" class="search-clear-btn" @click="clearSearch">×</button>
        </div>
        <div class="results-count">{{ totalResults }} Results</div>
        <button class="btn-apply-filters" @click="showFilterModal = true">
          <span>☰</span> Apply Filters <span class="filter-badge">{{ activeFilters.length }}</span>
        </button>
        <button class="btn-compare-nav" @click="goToCompare">
          Compare <span class="filter-badge">{{ comparedIds.size }}</span>
        </button>
      </div>
    </section>

    <!-- Toolbar -->
    <section class="toolbar-section">
      <div class="toolbar-container">
        <button class="btn-download" @click="downloadExcel">
          ⬇ Download Excel Table
        </button>
        <div class="toolbar-right">
          <span class="published-date">Published on: 29 March 2026</span>
          <select v-model="sortOrder" class="sort-select" @change="sortUniversities">
            <option value="rank_asc">University rank (High to Low)</option>
            <option value="rank_desc">University rank (Low to High)</option>
          </select>
        </div>
      </div>
    </section>

    <!-- Loading -->
    <div v-if="loading" class="loading-wrap">
      <div class="spinner"></div>
      <span>Loading universities...</span>
    </div>

    <!-- University Cards (Quick View) -->
    <section v-else-if="viewMode === 'quick'" class="cards-section">
      <div class="cards-container">
        <div v-if="paginatedUniversities.length === 0" class="empty-state">
          No universities found.
        </div>

        <div v-for="(uni, index) in paginatedUniversities" :key="uni.id" class="uni-card" @click="viewUniversity(uni.id)">
          <div class="card-left">
            <div class="rank-block">
              <span class="rank-label">Rank</span>
              <span class="rank-number">{{ uni.rank || (currentPage - 1) * perPage + index + 1 }}</span>
            </div>
            <div class="score-block">
              <span class="score-label">Overall Score</span>
              <span class="score-number">{{ uni.overall_score?.toFixed(1) || 'N/A' }}</span>
            </div>
          </div>

          <div class="card-center">
            <div class="uni-header">
              <div class="uni-logo-wrap">
                <img v-if="uni.logo && !failedLogos.has(uni.id)" :src="uni.logo" :alt="uni.name" class="uni-logo"
                  referrerpolicy="no-referrer" @error="handleLogoError(uni.id)" />
                <div v-else class="uni-logo-placeholder">🎓</div>
              </div>
              <div class="uni-info">
                <h3 class="uni-name">{{ uni.name }}</h3>
                <p class="uni-location">📍 {{ uni.city }}, {{ uni.country }}</p>
              </div>
              <div class="card-actions">
                <button :class="['btn-action', { active: comparedIds.has(uni.id) }]" @click.stop="toggleCompare(uni)">
                  <svg class="action-icon" viewBox="0 0 24 24" width="18" height="18">
                    <circle v-if="!comparedIds.has(uni.id)" cx="12" cy="12" r="9" fill="none" stroke="#555" stroke-width="1.8"/>
                    <template v-else>
                      <circle cx="12" cy="12" r="10" fill="#222"/>
                      <path d="M9 12.5l2 2 4-4.5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </template>
                  </svg>
                  <span>{{ comparedIds.has(uni.id) ? 'Added to compare' : 'Compare' }}</span>
                </button>
              </div>
            </div>

            <!-- Category Tabs -->
            <div class="category-tabs">
              <button
                v-for="(cat, ci) in quickViewCategories"
                :key="ci"
                :class="['cat-tab', { active: (activeTabMap.get(uni.id) ?? 0) === ci }]"
                @click.stop="setActiveTab(uni.id, ci)"
              >{{ cat.name }}</button>
            </div>

            <!-- Score Bars -->
            <div class="score-bars">
              <div v-for="col in quickViewCategories[activeTabMap.get(uni.id) ?? 0].cols" :key="col.key" class="score-bar-item">
                <span class="bar-label">{{ col.label }}</span>
                <div class="bar-row">
                  <div class="bar-track">
                    <div class="bar-fill" :style="{ width: getScorePercent(uni, col.key) + '%' }"></div>
                  </div>
                  <span class="bar-value">{{ getScoreDisplay(uni, col.key) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Table View -->
    <section v-else-if="!loading && viewMode === 'table'" class="table-section">
      <div class="table-outer">
        <div class="table-wrap">
          <table class="rank-table">
            <thead>
              <!-- Group header row -->
              <tr class="thead-group">
                <th class="th-rank" rowspan="2">Overall Rank <span class="sort-arrow">⇅</span></th>
                <th class="th-university" rowspan="2">University <span class="sort-arrow">⇅</span></th>
                <template v-for="(group, gi) in tableGroups" :key="gi">
                  <th :colspan="group.cols.length" class="th-group" :style="{ background: group.headerBg, borderTop: '3px solid ' + group.borderColor }">
                    {{ group.name }}
                  </th>
                </template>
              </tr>
              <!-- Sub-column header row -->
              <tr class="thead-sub">
                <template v-for="(group, gi) in tableGroups" :key="'sub-' + gi">
                  <th v-for="col in group.cols" :key="col.key" class="th-col" :style="{ borderBottom: '2px solid ' + group.borderColor }">
                    {{ col.label }} <span class="sort-arrow">⇅</span>
                  </th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr v-if="paginatedUniversities.length === 0">
                <td :colspan="2 + totalColCount" class="empty-td">No universities found.</td>
              </tr>
              <tr v-for="(uni, index) in paginatedUniversities" :key="uni.id" class="tr-uni" @click="viewUniversity(uni.id)">
                <td class="td-rank">{{ uni.rank || (currentPage - 1) * perPage + index + 1 }}</td>
                <td class="td-uni">
                  <div class="tbl-uni-info">
                    <div class="tbl-logo-wrap">
                      <img v-if="uni.logo && !failedLogos.has(uni.id)" :src="uni.logo" :alt="uni.name" class="tbl-logo"
                        referrerpolicy="no-referrer" @error="handleLogoError(uni.id)" />
                      <div v-else class="tbl-logo-placeholder">🎓</div>
                    </div>
                    <div>
                      <div class="tbl-uni-name">{{ uni.name }}</div>
                      <div class="tbl-uni-loc">📍 {{ uni.city }}, {{ uni.country }}</div>
                    </div>
                  </div>
                </td>
                <template v-for="(group, gi) in tableGroups" :key="'row-' + gi">
                  <td v-for="col in group.cols" :key="col.key" class="td-score">
                    {{ formatScore(uni[col.key]) }}
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Pagination -->
    <section :class="['pagination-section', { 'table-mode': viewMode === 'table' }]" v-if="!loading && universities.length > 0">
      <div class="pagination-container">
        <div class="pagination-left">
          <label>Results per page:</label>
          <select v-model.number="perPage" class="per-page-select">
            <option :value="10">10</option>
            <option :value="30">30</option>
            <option :value="50">50</option>
          </select>
          <span class="page-info">{{ pageStart }} - {{ pageEnd }} of {{ totalResults }}</span>
        </div>
        <div class="pagination-right">
          <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">‹</button>
          <button v-for="p in visiblePages" :key="p" :class="['page-btn', { active: p === currentPage, dots: p === '...' }]"
            :disabled="p === '...'" @click="p !== '...' && (currentPage = p)">
            {{ p }}
          </button>
          <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">›</button>
        </div>
      </div>
    </section>

    <!-- Filter Drawer -->
    <transition name="drawer">
      <div v-if="showFilterModal" class="filter-overlay" @click.self="showFilterModal = false">
        <div class="filter-drawer">
          <div class="filter-drawer-header">
            <span class="filter-drawer-title">Filters</span>
            <button class="filter-drawer-close" @click="showFilterModal = false">×</button>
          </div>

          <div class="filter-drawer-body">
            <!-- Region -->
            <div class="filter-group">
              <label class="filter-label">Region</label>
              <select v-model="filterForm.region_id" class="filter-input" @change="onRegionChange">
                <option :value="null">-- All Regions --</option>
                <option v-for="r in regionOptions" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
            </div>

            <!-- Country -->
            <div class="filter-group">
              <label class="filter-label">Country</label>
              <select v-model="filterForm.country" class="filter-input" :disabled="countryOptions.length === 0">
                <option value="">-- All Countries --</option>
                <option v-for="c in countryOptions" :key="c.id" :value="c.name">{{ c.name }}</option>
              </select>
            </div>

            <!-- City -->
            <div class="filter-group">
              <label class="filter-label">City</label>
              <input v-model="filterForm.city" class="filter-input" placeholder="" />
            </div>

            <!-- Study Level -->
            <div class="filter-group">
              <label class="filter-label">Study Level</label>
              <div class="filter-toggle-group">
                <button v-for="lvl in ['Bachelors', 'Masters']" :key="lvl"
                  :class="['filter-toggle-btn', { active: filterForm.studyLevels.includes(lvl) }]"
                  @click="toggleFilter(filterForm.studyLevels, lvl)">
                  {{ lvl }}
                </button>
              </div>
            </div>

            <!-- Top Ranking -->
            <div class="filter-group">
              <label class="filter-label">Top Ranking</label>
              <div class="filter-toggle-group">
                <button v-for="rng in rankingOptions" :key="rng.label"
                  :class="['filter-toggle-btn', { active: filterForm.rankingRange === rng.label }]"
                  @click="filterForm.rankingRange = filterForm.rankingRange === rng.label ? null : rng.label">
                  {{ rng.label }}
                </button>
              </div>
            </div>

            <div class="filter-divider"></div>

            <!-- Advanced Filters (require login) -->
            <div class="filter-advanced-wrap">
              <!-- Unlock banner -->
              <div v-if="!isAuthenticated" class="filter-unlock-banner">
                Unlock advanced filters by <span class="filter-unlock-link" @click="router.push('/login')">Signing in</span> or <span class="filter-unlock-link" @click="router.push('/signup')">Registering for free!</span>
              </div>

              <!-- International Fees -->
              <div class="filter-group">
                <label class="filter-label">International fees <span v-if="!isAuthenticated" class="filter-lock-icon">🔒</span></label>
                <template v-if="isAuthenticated">
                  <div class="filter-fee-row">
                    <div class="filter-fee-input-wrap">
                      <span class="fee-prefix">$</span>
                      <input v-model.number="filterForm.feeMin" type="number" class="filter-fee-input" placeholder="0" />
                      <span class="fee-suffix">Min.</span>
                    </div>
                    <div class="filter-fee-input-wrap">
                      <span class="fee-prefix">$</span>
                      <input v-model.number="filterForm.feeMax" type="number" class="filter-fee-input" placeholder="" />
                      <span class="fee-suffix">Max.</span>
                    </div>
                  </div>
                </template>
              </div>

              <div class="filter-divider"></div>

              <!-- Scholarship -->
              <div class="filter-group">
                <label class="filter-label">Scholarship availability <span v-if="!isAuthenticated" class="filter-lock-icon">🔒</span></label>
                <template v-if="isAuthenticated">
                  <div class="filter-radio-group">
                    <label class="filter-radio-label">
                      <input type="radio" v-model="filterForm.scholarship" value="yes" /> Yes
                    </label>
                    <label class="filter-radio-label">
                      <input type="radio" v-model="filterForm.scholarship" value="no" /> No
                    </label>
                  </div>
                </template>
              </div>

              <div class="filter-divider"></div>

              <!-- English Tests -->
              <div class="filter-group">
                <label class="filter-label">English Tests <span v-if="!isAuthenticated" class="filter-lock-icon">🔒</span></label>
                <template v-if="isAuthenticated">
                  <div class="filter-toggle-group">
                    <button v-for="t in ['IELTS', 'TOEFL']" :key="t"
                      :class="['filter-toggle-btn', { active: filterForm.englishTests.includes(t) }]"
                      @click="toggleFilter(filterForm.englishTests, t)">
                      {{ t }}
                    </button>
                  </div>
                </template>
              </div>

              <div class="filter-divider"></div>

              <!-- Academic Tests -->
              <div class="filter-group">
                <label class="filter-label">Academic Tests <span v-if="!isAuthenticated" class="filter-lock-icon">🔒</span></label>
                <template v-if="isAuthenticated">
                  <div class="filter-toggle-group">
                    <button v-for="t in ['ACT', 'ATAR', 'GPA', 'GMAT', 'GRE', 'SAT']" :key="t"
                      :class="['filter-toggle-btn', { active: filterForm.academicTests.includes(t) }]"
                      @click="toggleFilter(filterForm.academicTests, t)">
                      {{ t }}
                    </button>
                  </div>
                </template>
              </div>

              <div class="filter-divider"></div>

              <!-- Student Mix -->
              <div class="filter-group">
                <label class="filter-label">Student Mix <span v-if="!isAuthenticated" class="filter-lock-icon">🔒</span></label>
                <template v-if="isAuthenticated">
                  <div class="student-mix-display">
                    <span class="mix-label-domestic">Domestic {{ 100 - filterForm.studentMixMin }}%</span>
                    <span class="mix-label-intl">International {{ filterForm.studentMixMin }}%</span>
                  </div>
                  <input
                    type="range"
                    v-model.number="filterForm.studentMixMin"
                    min="0" max="100" step="1"
                    class="student-mix-slider"
                    :style="`background: linear-gradient(to right, #1a1a2e 0%, #1a1a2e ${filterForm.studentMixMin}%, #d9e0f0 ${filterForm.studentMixMin}%, #d9e0f0 100%)`"
                  />
                  <div v-if="filterForm.studentMixMin > 0" class="student-mix-hint">
                    Show universities with ≥{{ filterForm.studentMixMin }}% international students
                  </div>
                </template>
              </div>
            </div>
          </div>

          <div class="filter-drawer-footer">
            <button class="filter-btn-reset" @click="resetFilters">Reset Filters</button>
            <button class="filter-btn-apply" @click="applyFilters">Apply Filters</button>
          </div>
        </div>
      </div>
    </transition>

    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { universityAPI } from '@/services/api'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const universities = ref([])
const searchQuery = ref('')
const loading = ref(false)
const showFilterModal = ref(false)
const activeFilters = ref([])
const viewMode = ref('quick')
const sortOrder = ref('rank_asc')
const currentPage = ref(1)
const perPage = ref(30)
const regionOptions = ref([])
const countryOptions = ref([])

const filterForm = ref({
  region_id: null,
  country: '',
  city: '',
  studyLevels: [],
  rankingRange: null,
  feeMin: null,
  feeMax: null,
  scholarship: null,
  englishTests: [],
  academicTests: [],
  minRank: null,
  maxRank: null,
  studentMixMin: 0,
})

const rankingOptions = [
  { label: 'Top 100', min: 1, max: 100 },
  { label: '101 - 300', min: 101, max: 300 },
  { label: '301 - 500', min: 301, max: 500 },
  { label: '501 - 1,500', min: 501, max: 1500 },
]

const toggleFilter = (arr, val) => {
  const idx = arr.indexOf(val)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(val)
}

const resetFilters = () => {
  filterForm.value = {
    region_id: null, country: '', city: '',
    studyLevels: [], rankingRange: null,
    feeMin: null, feeMax: null,
    scholarship: null, englishTests: [], academicTests: [],
    minRank: null, maxRank: null,
    studentMixMin: 0,
  }
  loadCountries(null)
}
const totalResults = computed(() => universities.value.length)
const totalPages = computed(() => Math.ceil(totalResults.value / perPage.value))
const pageStart = computed(() => (currentPage.value - 1) * perPage.value + 1)
const pageEnd = computed(() => Math.min(currentPage.value * perPage.value, totalResults.value))

const paginatedUniversities = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return universities.value.slice(start, start + perPage.value)
})

const visiblePages = computed(() => {
  const pages = []
  const tp = totalPages.value
  const cp = currentPage.value
  if (tp <= 5) { for (let i = 1; i <= tp; i++) pages.push(i) }
  else {
    pages.push(1)
    if (cp > 3) pages.push('...')
    for (let i = Math.max(2, cp - 1); i <= Math.min(tp - 1, cp + 1); i++) pages.push(i)
    if (cp < tp - 2) pages.push('...')
    pages.push(tp)
  }
  return pages
})

// Flatten nested scores object into flat properties expected by templates
const normalizeUniversity = (uni) => {
  const s = uni.scores || {}
  const rd = s['Research & Discovery'] || {}
  const le = s['Learning Experience'] || {}
  const emp = s['Employability'] || {}
  const ge = s['Global Engagement'] || {}
  const sus = s['Sustainability'] || {}
  return {
    ...uni,
    citations_per_faculty: rd['Citations per Faculty'] ?? null,
    academic_reputation: rd['Academic Reputation'] ?? null,
    faculty_student_ratio: le['Faculty Student Ratio'] ?? null,
    employer_reputation: emp['Employer Reputation'] ?? null,
    graduate_employment_rate: emp['Employment Outcomes'] ?? null,
    international_students: ge['International Student Ratio'] ?? null,
    international_research_network: ge['International Research Network'] ?? null,
    international_faculty: ge['International Faculty Ratio'] ?? null,
    international_student_diversity: ge['International Student Diversity'] ?? null,
    sustainability_score: sus['Sustainability Score'] ?? null,
  }
}

onMounted(async () => {
  await loadRegions()
  const regionParam = route.query.region_id
  if (regionParam) {
    filterForm.value.region_id = Number(regionParam)
    await loadCountries(Number(regionParam))
    await applyFilters()
  } else {
    loadUniversities()
    loadCountries()
  }
})

const loadUniversities = async () => {
  loading.value = true
  try {
    const response = await universityAPI.getAll(2000)
    universities.value = response.map(u => normalizeUniversity(u.toPlainObject()))
  } catch (err) {
    const detail = err.response?.data?.detail || 'Cannot connect to the database. Please try again later.'
    message.error(detail)
  } finally { loading.value = false }
}

const loadRegions = async () => {
  try {
    const response = await universityAPI.getRegions()
    regionOptions.value = response.data
  } catch (err) { console.error('Failed to load regions', err) }
}

const loadCountries = async (region_id = null) => {
  try {
    const response = await universityAPI.getCountriesByRegion(region_id)
    countryOptions.value = response.data
  } catch (err) { console.error('Failed to load countries', err) }
}

const onRegionChange = () => {
  filterForm.value.country = ''
  loadCountries(filterForm.value.region_id || null)
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) { loadUniversities(); activeFilters.value = []; return }
  loading.value = true
  try {
    const response = await universityAPI.search(searchQuery.value)
    universities.value = response.map(u => normalizeUniversity(u.toPlainObject()))
    currentPage.value = 1
    activeFilters.value = []
  } catch (err) {
    const detail = err.response?.data?.detail || 'Cannot connect to the database. Please try again later.'
    message.error(detail)
  } finally { loading.value = false }
}

let searchDebounceTimer = null
const onSearchInput = () => {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => { handleSearch() }, 400)
}

const clearSearch = () => {
  searchQuery.value = ''
  loadUniversities()
  activeFilters.value = []
}

const applyFilters = async () => {
  loading.value = true
  try {
    const rng = rankingOptions.find(r => r.label === filterForm.value.rankingRange)
    const filters = {
      region_id: filterForm.value.region_id || undefined,
      country: filterForm.value.country || undefined,
      city: filterForm.value.city || undefined,
      min_rank: rng ? rng.min : (filterForm.value.minRank || undefined),
      max_rank: rng ? rng.max : (filterForm.value.maxRank || undefined),
      english_tests: filterForm.value.englishTests.length ? filterForm.value.englishTests : undefined,
      academic_tests: filterForm.value.academicTests.length ? filterForm.value.academicTests : undefined,
      min_international_pct: isAuthenticated.value && filterForm.value.studentMixMin > 0 ? filterForm.value.studentMixMin : undefined,
      fee_min: isAuthenticated.value && filterForm.value.feeMin != null ? filterForm.value.feeMin : undefined,
      fee_max: isAuthenticated.value && filterForm.value.feeMax != null ? filterForm.value.feeMax : undefined,
      scholarship: isAuthenticated.value && filterForm.value.scholarship ? filterForm.value.scholarship : undefined,
    }
    const response = await universityAPI.filter(filters)
    universities.value = response.map(u => normalizeUniversity(u.toPlainObject()))
    showFilterModal.value = false
    currentPage.value = 1
    activeFilters.value = []
    if (filters.region_id) activeFilters.value.push({ label: 'Region', value: regionOptions.value.find(r => r.id === filters.region_id)?.name || filters.region_id })
    if (filters.country) activeFilters.value.push({ label: 'Country', value: filters.country })
    if (filters.city) activeFilters.value.push({ label: 'City', value: filters.city })
    if (filters.min_rank) activeFilters.value.push({ label: 'Min Rank', value: filters.min_rank })
    if (filters.max_rank) activeFilters.value.push({ label: 'Max Rank', value: filters.max_rank })
    if (filters.english_tests) filters.english_tests.forEach(t => activeFilters.value.push({ label: 'English', value: t }))
    if (filters.academic_tests) filters.academic_tests.forEach(t => activeFilters.value.push({ label: 'Academic', value: t }))
    if (filters.min_international_pct) activeFilters.value.push({ label: 'International', value: `≥${filters.min_international_pct}%` })
    if (filters.fee_min != null) activeFilters.value.push({ label: 'Fee Min', value: `$${filters.fee_min}` })
    if (filters.fee_max != null) activeFilters.value.push({ label: 'Fee Max', value: `$${filters.fee_max}` })
    if (filters.scholarship) activeFilters.value.push({ label: 'Scholarship', value: filters.scholarship === 'yes' ? 'Yes' : 'No' })
  } catch (err) {
    const detail = err.response?.data?.detail || 'Cannot connect to the database. Please try again later.'
    message.error(detail)
  } finally { loading.value = false }
}

const sortUniversities = () => {
  const arr = [...universities.value]
  if (sortOrder.value === 'rank_asc') arr.sort((a, b) => (a.rank || 9999) - (b.rank || 9999))
  else if (sortOrder.value === 'rank_desc') arr.sort((a, b) => (b.rank || 0) - (a.rank || 0))
  else arr.sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0))
  universities.value = arr
}

const activeTabMap = reactive(new Map())
const setActiveTab = (id, ci) => { activeTabMap.set(id, ci) }

const quickViewCategories = [
  {
    name: 'Research & Discovery',
    cols: [
      { key: 'citations_per_faculty', label: 'Citations per Faculty' },
      { key: 'academic_reputation', label: 'Academic Reputation' },
    ]
  },
  {
    name: 'Learning Experience',
    cols: [
      { key: 'faculty_student_ratio', label: 'Faculty Student Ratio' },
    ]
  },
  {
    name: 'Employability',
    cols: [
      { key: 'employer_reputation', label: 'Employer Reputation' },
      { key: 'graduate_employment_rate', label: 'Employment Outcomes' },
    ]
  },
  {
    name: 'Global Engagement',
    cols: [
      { key: 'international_students', label: 'International Student Ratio' },
      { key: 'international_research_network', label: 'International Research Network' },
      { key: 'international_faculty', label: 'International Faculty Ratio' },
      { key: 'international_student_diversity', label: 'International Student Diversity' },
    ]
  },
  {
    name: 'Sustainability',
    cols: [
      { key: 'sustainability_score', label: 'Sustainability Score' },
    ]
  },
]

const getScore = (uni, key) => {
  const val = uni[key]
  return val != null ? Number(val).toFixed(1) : 0
}
const getScorePercent = (uni, key) => {
  const val = uni[key]
  if (val == null) return 0
  return Math.min(100, Math.max(0, Number(val)))
}
const getScoreDisplay = (uni, key) => {
  const val = uni[key]
  return val != null ? Number(val).toFixed(1) : '—'
}

const getMetricValue = (uni, type) => {
  if (type === 'citations') return uni.citations_per_faculty?.toFixed(1) || uni.overall_score?.toFixed(1) || '—'
  return uni.academic_reputation?.toFixed(1) || uni.overall_score?.toFixed(1) || '—'
}
const getMetricPercent = (uni, type) => {
  if (type === 'citations') return uni.citations_per_faculty || uni.overall_score || 0
  return uni.academic_reputation || uni.overall_score || 0
}

// Table view
const tableGroupStart = ref(0)
const tableGroupsPerPage = 3
const tableGroups = [
  {
    name: 'Research & Discovery',
    headerBg: '#dce8ff',
    borderColor: '#1f3ab0',
    cols: [
      { key: 'citations_per_faculty', label: 'Citations per Faculty' },
      { key: 'academic_reputation', label: 'Academic Reputation' },
    ]
  },
  {
    name: 'Learning Experience',
    headerBg: '#dce8ff',
    borderColor: '#1f3ab0',
    cols: [
      { key: 'faculty_student_ratio', label: 'Faculty Student Ratio' },
    ]
  },
  {
    name: 'Employability',
    headerBg: '#fff0d6',
    borderColor: '#e07800',
    cols: [
      { key: 'employer_reputation', label: 'Employer Reputation' },
      { key: 'graduate_employment_rate', label: 'Employment Outcomes' },
    ]
  },
  {
    name: 'Global Engagement',
    headerBg: '#d6f0e0',
    borderColor: '#2a9d5c',
    cols: [
      { key: 'international_students', label: 'International Students Ratio' },
      { key: 'international_research_network', label: 'International Research Network' },
      { key: 'international_faculty', label: 'International Faculty Ratio' },
      { key: 'international_student_diversity', label: 'International Student Diversity' },
    ]
  },
  {
    name: 'Sustainability',
    headerBg: '#e8f5e9',
    borderColor: '#388e3c',
    cols: [
      { key: 'sustainability_score', label: 'Sustainability Score' },
    ]
  },
]
const visibleTableGroups = computed(() => tableGroups.slice(tableGroupStart.value, tableGroupStart.value + tableGroupsPerPage))
const visibleColCount = computed(() => visibleTableGroups.value.reduce((s, g) => s + g.cols.length, 0))
const totalColCount = computed(() => tableGroups.reduce((s, g) => s + g.cols.length, 0))
const formatScore = (val) => (val != null ? Number(val).toFixed(1) : '—')

const failedLogos = ref(new Set())
const handleLogoError = (id) => {
  failedLogos.value = new Set([...failedLogos.value, id])
}

const comparedIds = ref(new Set())

const toggleCompare = (uni) => {
  if (comparedIds.value.has(uni.id)) {
    comparedIds.value.delete(uni.id)
    comparedIds.value = new Set(comparedIds.value)
  } else {
    if (comparedIds.value.size >= 5) {
      message.warning('You can compare up to 5 universities maximum')
      return
    }
    comparedIds.value.add(uni.id)
    comparedIds.value = new Set(comparedIds.value)
  }
}
const viewUniversity = (id) => { router.push(`/university/${id}`) }
const downloadExcel = () => { message.info('Download feature coming soon') }
const goToCompare = () => {
  if (comparedIds.value.size < 2) {
    message.warning('Please select at least 2 universities to compare')
    return
  }
  const ids = Array.from(comparedIds.value)
  router.push({ path: '/comparison', query: { ids: ids.join(',') } })
}
</script>

<style scoped>
* { box-sizing: border-box; }

.universities-page {
  width: 100%;
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hero */
.hero-section {
  background: #e8f0ff;
  padding: 40px 50px 30px;
  border-bottom: 1px solid #e8e8e8;
}
.hero-container { max-width: 1200px; margin: 0 auto; }
.hero-logo { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.hero-logo-img { width: 28px; height: 28px; object-fit: contain; }
.hero-logo-text { font-size: 20px; font-weight: 700; color: #1f3ab0; }
.hero-title { font-size: 24px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px; }
.hero-desc { font-size: 14px; color: #555; line-height: 1.6; margin-bottom: 4px; }
.read-more { color: #1f3ab0; font-size: 14px; text-decoration: none; display: inline-block; margin: 8px 0 20px; }
.read-more:hover { text-decoration: underline; }

.register-banner {
  display: flex; align-items: center; gap: 16px;
  background: linear-gradient(135deg, #1f3ab0, #2d4fcf);
  color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px;
}
.btn-register {
  background: #fff; color: #1f3ab0; border: none; padding: 8px 20px;
  border-radius: 4px; font-weight: 600; cursor: pointer; white-space: nowrap;
  transition: background 0.2s;
}
.btn-register:hover { background: #e8ecf6; }

/* Search Bar */
.search-bar-section { background: #fff; padding: 16px 50px; border-bottom: 1px solid #e8e8e8; }
.search-bar-container {
  max-width: 1200px; margin: 0 auto;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.view-toggle { display: flex; border: 1px solid #d9d9d9; border-radius: 6px; overflow: hidden; }
.toggle-btn {
  padding: 8px 16px; border: none; background: #fff; cursor: pointer;
  font-size: 13px; display: flex; align-items: center; gap: 6px;
  transition: all 0.2s; color: #555;
}
.toggle-btn.active { background: #1f3ab0; color: #fff; }
.toggle-btn:not(.active):hover { background: #f0f0f0; }

.search-input-wrap {
  display: flex; align-items: center; border: 1px solid #d9d9d9;
  border-radius: 6px; padding: 0 12px; flex: 1; max-width: 260px;
}
.search-icon-inner { width: 16px; height: 16px; object-fit: contain; margin-right: 8px; opacity: 0.6; flex-shrink: 0; }
.search-input-wrap input {
  border: none; outline: none; padding: 8px 0; font-size: 14px; width: 100%;
}
.search-clear-btn {
  background: none; border: none; cursor: pointer; color: #aaa;
  font-size: 18px; line-height: 1; padding: 0 0 0 6px; flex-shrink: 0;
}
.search-clear-btn:hover { color: #333; }

.results-count { font-size: 15px; font-weight: 600; color: #333; margin-left: auto; }
.btn-apply-filters {
  display: flex; align-items: center; gap: 8px;
  background: #1f3ab0; color: #fff; border: none; padding: 8px 20px;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;
  transition: background 0.2s;
}
.btn-apply-filters:hover { background: #1a2d8a; }
.filter-badge {
  background: #fff; color: #1f3ab0; border-radius: 4px;
  padding: 1px 7px; font-size: 12px; font-weight: 700;
}
.btn-compare-nav {
  display: flex; align-items: center; gap: 8px;
  background: #fff; color: #1f3ab0; border: 2px solid #1f3ab0; padding: 8px 20px;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600;
  transition: all 0.2s;
}
.btn-compare-nav:hover { background: #1f3ab0; color: #fff; }
.btn-compare-nav .filter-badge { background: #1f3ab0; color: #fff; }
.btn-compare-nav:hover .filter-badge { background: #fff; color: #1f3ab0; }

/* Toolbar */
.toolbar-section { background: #f9fafb; padding: 12px 50px; border-bottom: 1px solid #e8e8e8; }
.toolbar-container {
  max-width: 1200px; margin: 0 auto;
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
}
.btn-download {
  background: none; border: none; color: #1f3ab0; cursor: pointer;
  font-size: 13px; display: flex; align-items: center; gap: 6px;
}
.btn-download:hover { text-decoration: underline; }
.toolbar-right { display: flex; align-items: center; gap: 20px; }
.published-date { font-size: 13px; color: #888; }
.sort-select {
  border: 1px solid #d9d9d9; border-radius: 6px; padding: 6px 12px;
  font-size: 13px; color: #333; background: #fff; cursor: pointer;
}

/* Loading */
.loading-wrap {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 20px; gap: 16px; color: #666;
}
.spinner {
  width: 36px; height: 36px; border: 3px solid #e0e0e0;
  border-top-color: #1f3ab0; border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Cards */
.cards-section { padding: 24px 50px; }
.cards-container { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }

.empty-state {
  text-align: center; padding: 60px; color: #999; font-size: 16px;
  background: #fff; border-radius: 10px;
}

.uni-card {
  display: flex; background: #fff; border-radius: 10px;
  border: 1px solid #e0e7f1; overflow: hidden; cursor: pointer;
  transition: box-shadow 0.3s, transform 0.2s;
}
.uni-card:hover {
  box-shadow: 0 4px 20px rgba(31, 58, 176, 0.12);
  transform: translateY(-2px);
}

.card-left {
  width: 140px; min-width: 140px; border-right: 3px solid #1f3ab0;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  padding: 20px 16px; gap: 16px; background: #fafbff;
}
.rank-block, .score-block { text-align: center; }
.rank-label, .score-label { display: block; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
.rank-number { font-size: 32px; font-weight: 700; color: #1a1a2e; }
.score-number { font-size: 20px; font-weight: 700; color: #1f3ab0; }

.card-center { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.uni-header { display: flex; align-items: center; gap: 16px; }
.uni-logo-wrap { width: 80px; height: 80px; flex-shrink: 0; border: 1px solid #e0e7f1; border-radius: 6px; overflow: hidden; }
.uni-logo { width: 100%; height: 100%; object-fit: contain; border-radius: 4px; }
.uni-logo-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 4px;
  font-size: 24px;
}
.uni-info { flex: 1; }
.uni-name { font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 0; }
.uni-location { font-size: 13px; color: #777; margin: 4px 0 0; }
.card-actions { display: flex; align-items: center; gap: 20px; flex-shrink: 0; margin-left: auto; }

.category-tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.cat-tab {
  padding: 5px 14px; border: 1px solid #d0d8e8; border-radius: 20px;
  background: #fff; font-size: 12px; color: #555; cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.cat-tab.active { border-color: #1f3ab0; color: #1f3ab0; font-weight: 600; }
.cat-tab:hover { border-color: #1f3ab0; color: #1f3ab0; }
.cat-more { padding: 5px 10px; font-size: 16px; font-weight: 700; }

.score-bars { display: flex; gap: 32px; flex-wrap: wrap; }
.score-bar-item { display: flex; flex-direction: column; gap: 6px; min-width: 140px; }
.bar-label { font-size: 12px; color: #555; white-space: nowrap; }
.bar-row { display: flex; align-items: center; gap: 8px; }
.bar-track { width: 140px; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; flex-shrink: 0; }
.bar-fill { height: 100%; background: #4a90d9; border-radius: 4px; transition: width 0.5s ease; }
.bar-value { font-size: 13px; font-weight: 600; color: #333; white-space: nowrap; }

.btn-action {
  display: flex; align-items: center; gap: 6px;
  background: none; border: none; cursor: pointer;
  font-size: 13px; color: #333; font-weight: 500;
  padding: 4px 0; transition: all 0.2s; white-space: nowrap;
}
.btn-action:hover { color: #1f3ab0; }
.btn-action.active { color: #1a1a2e; font-weight: 600; }
.action-icon { font-size: 16px; }

/* Pagination */
.pagination-section { padding: 20px 50px 40px; }
.pagination-section.table-mode { padding: 20px 24px 40px; }
.pagination-section.table-mode .pagination-container { max-width: 1400px; }
.pagination-container {
  max-width: 1200px; margin: 0 auto;
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 24px; border-radius: 10px; border: 1px solid #e0e7f1;
}
.pagination-left { display: flex; align-items: center; gap: 12px; font-size: 13px; color: #555; }
.per-page-select {
  border: 1px solid #d9d9d9; border-radius: 4px; padding: 4px 8px;
  font-size: 13px; cursor: pointer;
}
.page-info { color: #888; }
.pagination-right { display: flex; align-items: center; gap: 4px; }
.page-btn {
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  border: 1px solid #d9d9d9; border-radius: 4px; background: #fff;
  font-size: 14px; cursor: pointer; color: #333; transition: all 0.2s;
}
.page-btn.active { background: #1f3ab0; color: #fff; border-color: #1f3ab0; }
.page-btn.dots { border: none; cursor: default; }
.page-btn:not(.active):not(.dots):hover { border-color: #1f3ab0; color: #1f3ab0; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Table View */
.table-section { padding: 24px 24px; }
.table-outer { max-width: 1400px; margin: 0 auto; }
.table-wrap { background: #fff; border-radius: 10px; border: 1px solid #e0e7f1; overflow: hidden; }
.rank-table { width: 100%; border-collapse: collapse; font-size: 11px; table-layout: fixed; }

.thead-group th, .thead-sub th { background: #f0f4ff; font-weight: 600; color: #1a1a2e; text-align: center; padding: 7px 6px; border: 1px solid #d8e2f3; white-space: normal; word-break: break-word; }
.th-rank, .th-university { background: #e8edf8; vertical-align: middle; }
.th-university { width: 18%; text-align: left; padding-left: 10px; }
.th-group { font-weight: 700; font-size: 13px; }
.th-col { font-size: 11px; font-weight: 500; color: #444; background: #f9fbff; word-break: break-word; white-space: normal; }
.sort-arrow { font-size: 10px; color: #999; margin-left: 4px; }

.tr-uni { cursor: pointer; transition: background 0.15s; }
.tr-uni:hover { background: #f0f5ff; }
.tr-uni:nth-child(even) { background: #fafbff; }
.tr-uni:nth-child(even):hover { background: #edf2ff; }
.td-rank { text-align: center; font-size: 18px; font-weight: 700; color: #1a1a2e; padding: 10px 6px; border: 1px solid #e8edf3; width: 6%; }
.td-uni { padding: 10px 10px; border: 1px solid #e8edf3; width: 18%; }
.tbl-uni-info { display: flex; align-items: center; gap: 10px; }
.tbl-logo-wrap { width: 40px; height: 40px; flex-shrink: 0; border: 1px solid #e0e7f1; border-radius: 4px; overflow: hidden; }
.tbl-logo { width: 100%; height: 100%; object-fit: contain; }
.tbl-logo-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2); font-size: 16px;
}

.tbl-uni-name { font-weight: 600; color: #1f3ab0; font-size: 13px; }
.tbl-uni-loc { font-size: 11px; color: #888; margin-top: 2px; }
.td-score { text-align: center; font-size: 13px; font-weight: 500; color: #333; padding: 10px 4px; border: 1px solid #e8edf3; }
.empty-td { text-align: center; padding: 60px; color: #999; font-size: 15px; }

/* Responsive */
@media (max-width: 900px) {
  .hero-section, .search-bar-section, .toolbar-section, .cards-section, .pagination-section {
    padding-left: 20px; padding-right: 20px;
  }
  .uni-card { flex-direction: column; }
  .card-left {
    width: 100%; min-width: unset; flex-direction: row;
    border-right: none; border-bottom: 3px solid #1f3ab0; padding: 12px 20px;
  }
  .card-right { width: 100%; min-width: unset; flex-direction: row; padding: 12px 20px; }
  .pagination-container { flex-direction: column; gap: 16px; }
}

/* Filter Drawer */
.filter-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.35);
  display: flex; justify-content: flex-end; align-items: stretch;
}
/* .filter-drawer {
  width: 360px; height: 100vh; max-height: 100vh; background: #fff;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: -4px 0 20px rgba(0,0,0,0.15);
} */
 .filter-drawer {
  width: 360px;
  height: 100vh; /* Chiếm trọn chiều cao màn hình */
  background: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Header và Footer sẽ cố định, chỉ Body được cuộn */
}
.filter-drawer-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.filter-drawer-title { font-size: 20px; font-weight: 700; color: #1f3ab0; }
.filter-drawer-close {
  background: none; border: none; font-size: 22px; cursor: pointer;
  color: #888; line-height: 1; padding: 0;
}
.filter-drawer-close:hover { color: #333; }
.filter-drawer-body {
  flex: 1;
  min-height: 0; /* Quan trọng để overflow hoạt động trong flexbox */
  overflow-y: auto; /* Tạo thanh cuộn khi nội dung quá dài */
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px; /* Tăng khoảng cách giữa các cụm filter (Region, Country, City...) */
}
.filter-drawer-footer {
  padding: 16px 24px; border-top: 1px solid #f0f0f0;
  display: flex; gap: 12px;
}
.filter-btn-reset {
  flex: 1; padding: 10px; border: 1px solid #d0d0d0; border-radius: 6px;
  background: #fff; color: #1f3ab0; font-size: 14px; font-weight: 600; cursor: pointer;
}
.filter-btn-reset:hover { background: #f0f4ff; }
.filter-btn-apply {
  flex: 1; padding: 10px; border: none; border-radius: 6px;
  background: #1f3ab0; color: #fff; font-size: 14px; font-weight: 600; cursor: pointer;
}
.filter-btn-apply:hover { background: #1a2d8a; }

/* .filter-group { display: flex; flex-direction: column; gap: 8px; min-height: 40px; } */
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px; 
  margin-top: 0px; 
}

.filter-group:first-child {
  margin-top: 0;
}
.filter-label { font-size: 14px; font-weight: 600; color: #1a1a2e; line-height: 1.6; }
.filter-input {
  width: 100%; padding: 9px 12px; border: 1px solid #d0d0d0;
  border-radius: 6px; font-size: 14px; outline: none;
  background: #fff; cursor: pointer; appearance: auto;
}
.filter-input:focus { border-color: #1f3ab0; }
.filter-input:disabled { background: #f5f5f5; color: #aaa; cursor: not-allowed; }

/* .filter-toggle-group { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-toggle-btn {
  padding: 6px 14px; border: 1px solid #d0d0d0; border-radius: 4px;
  background: #fff; font-size: 13px; color: #333; cursor: pointer;
  transition: all 0.15s;
} */
 /* Tìm đến class này trong phần <style> */
.filter-toggle-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* Khoảng cách giữa các nút */
}

/* Thêm hoặc sửa thuộc tính cho button bên trong */
.filter-toggle-btn {
  /* Tính toán để 2 button nằm vừa 1 hàng: (100% - gap) / 2 */
  width: calc(50% - 5px); 
  padding: 10px 5px; /* Điều chỉnh padding cho cân đối */
  text-align: center;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  
  /* Đảm bảo text không bị vỡ hàng nếu quá dài */
  /* white-space: nowrap;  */
}
.filter-toggle-btn:hover { border-color: #1f3ab0; color: #1f3ab0; }
.filter-toggle-btn.active { border-color: #1f3ab0; background: #1f3ab0; color: #fff; }

/* .filter-divider { border: none; border-top: 1px solid #ebebeb; margin: 4px 0; } */

/* Advanced filter lock */
.filter-advanced-wrap {
  position: relative;
}
/* .filter-unlock-banner {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
  line-height: 1.5;
} */
.filter-divider {
  border: none;
  border-top: 1px solid #ebebeb;
  margin: 8px 0; /* Đảm bảo đường kẻ có khoảng cách trên dưới */
}
.filter-unlock-banner {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
  font-size: 13px;
  margin-top: 2px; /* Đẩy banner xuống một chút */
  margin-bottom: 8px;
  line-height: 1.5;
  color: #333;
}
.filter-unlock-link {
  color: #1f3ab0;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}
.filter-unlock-link:hover { color: #0d2480; }
.filter-lock-icon { font-size: 13px; margin-left: 4px; }

.filter-fee-row { display: flex; gap: 12px; }
.filter-fee-input-wrap {
  flex: 1; display: flex; flex-direction: column; gap: 4px;
  border: 1px solid #d0d0d0; border-radius: 6px; padding: 8px 12px;
}
.fee-prefix { font-size: 14px; color: #333; }
.filter-fee-input {
  border: none; outline: none; font-size: 14px; width: 100%; padding: 0;
}
.fee-suffix { font-size: 12px; color: #888; }

.filter-radio-group { display: flex; gap: 20px; }
.filter-radio-label { display: flex; align-items: center; gap: 6px; font-size: 14px; color: #333; cursor: pointer; }
.filter-radio-label input { accent-color: #1f3ab0; width: 16px; height: 16px; cursor: pointer; }

/* Student Mix slider */
.student-mix-display {
  display: flex; justify-content: space-between;
  font-size: 13px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px;
}
.mix-label-domestic { color: #555; }
.mix-label-intl { color: #1f3ab0; }
.student-mix-slider {
  width: 100%; -webkit-appearance: none; appearance: none;
  height: 4px; border-radius: 2px; outline: none; cursor: pointer;
}
.student-mix-slider::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 18px; height: 18px; border-radius: 50%;
  background: #fff; border: 2px solid #1a1a2e; cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.student-mix-slider::-moz-range-thumb {
  width: 18px; height: 18px; border-radius: 50%;
  background: #fff; border: 2px solid #1a1a2e; cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.student-mix-hint {
  font-size: 12px; color: #1f3ab0; margin-top: 6px; font-style: italic;
}

/* Drawer transition */
.drawer-enter-active, .drawer-leave-active { transition: opacity 0.25s ease; }
.drawer-enter-active .filter-drawer, .drawer-leave-active .filter-drawer { transition: transform 0.25s ease; }
.drawer-enter-from, .drawer-leave-to { opacity: 0; }
.drawer-enter-from .filter-drawer, .drawer-leave-to .filter-drawer { transform: translateX(100%); }
</style>
