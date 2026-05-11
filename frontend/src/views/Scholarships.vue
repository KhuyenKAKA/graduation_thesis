<template>
  <div class="scholarships-page">
    <Header />

    <!-- Hero -->
    <section class="hero-section">
      <div class="hero-container">
        <p class="hero-label">Funding Opportunities</p>
        <h1 class="hero-title">Discover Scholarships at Top Universities</h1>
        <p class="hero-subtitle">
          Explore scholarships offered by leading universities around the world.
          Find the right funding to support your academic journey.
        </p>

        <!-- Search bar -->
        <div class="search-wrap">
          <span class="search-icon">
            <img src="/assets/search.png" alt="Search" class="icon-img" />
          </span>
          <input
            v-model="searchQuery"
            class="search-input"
            placeholder="Search by university or scholarship name..."
          />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">×</button>
        </div>
      </div>
    </section>

    <!-- Stats bar -->
    <div class="stats-bar">
      <div class="stats-container">
        <span class="stats-count">
          <strong>{{ filteredScholarships.length }}</strong> scholarships found
        </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-wrap">
      <div class="spinner"></div>
      <span>Loading scholarships...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-wrap">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="load">Retry</button>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredScholarships.length === 0" class="empty-wrap">
      <p>No scholarships match your search.</p>
    </div>

    <!-- Cards grid -->
    <section v-else class="cards-section">
      <div class="cards-grid">
        <div
          v-for="s in filteredScholarships"
          :key="s.id"
          class="scholarship-card"
          @click="s.university_id && $router.push(`/university/${s.university_id}`)"
          :class="{ clickable: !!s.university_id }"
        >
          <!-- Top: logo -->
          <div class="card-logo-area">
            <img
              v-if="s.university_logo && !failedLogos.has(s.id)"
              :src="s.university_logo"
              :alt="s.university_name"
              class="uni-logo"
              referrerpolicy="no-referrer"
              @error="failedLogos.add(s.id)"
            />
            <div v-else class="logo-placeholder">🎓</div>
          </div>

          <!-- Bottom: info -->
          <div class="card-info">
            <p class="uni-name">{{ s.university_name || 'Unknown University' }}</p>
            <h3 class="scholarship-name">{{ s.name }}</h3>

            <div class="info-row" v-if="s.criteria">
              <span class="info-label">Type</span>
              <span class="info-chip">{{ s.criteria == 1 || s.criteria == '1' ? 'Bachelor' : s.criteria == 2 || s.criteria == '2' ? 'Master' : s.criteria }}</span>
            </div>

            <div class="info-row" v-if="s.value != null">
              <span class="info-label">Value</span>
              <span class="info-value value-highlight">
                {{ formatValue(s.value) }}
              </span>
            </div>

            <div class="info-row" v-if="s.duration">
              <span class="info-label">Duration</span>
              <span class="info-value">{{ s.duration }} years</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { scholarshipsAPI } from '@/services/api.js'

const scholarships = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const failedLogos = reactive(new Set())

const filteredScholarships = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return scholarships.value
  return scholarships.value.filter(s =>
    s.name?.toLowerCase().includes(q) ||
    s.university_name?.toLowerCase().includes(q) ||
    s.criteria?.toLowerCase().includes(q)
  )
})

function formatValue(val) {
  if (val === null || val === undefined || val === '') return 'N/A'
  // Strip non-numeric characters (e.g. "$", ",") to get the raw number
  const numeric = typeof val === 'string' ? Number(val.replace(/[^0-9.]/g, '')) : Number(val)
  if (isNaN(numeric)) return val // Return original string if unparseable
  // If value looks like a percentage (0–100), show as %
  if (numeric <= 100) return `${numeric}% tuition coverage`
  // Otherwise format as currency
  return `$${numeric.toLocaleString('en-US')}`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    scholarships.value = await scholarshipsAPI.getAll()
  } catch (e) {
    error.value = 'Failed to load scholarships. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.scholarships-page {
  min-height: 100vh;
  background: #f5f6fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ── Hero ─────────────────────────────────────────────── */
.hero-section {
  background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 60%, #1e5799 100%);
  padding: 64px 24px 56px;
}

.hero-container {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero-label {
  color: #7ecbff;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin: 0 0 12px;
}

.hero-title {
  color: #fff;
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px;
  line-height: 1.25;
}

.hero-subtitle {
  color: #b8d4f0;
  font-size: 16px;
  line-height: 1.6;
  margin: 0 0 32px;
}

.search-wrap {
  position: relative;
  max-width: 560px;
  margin: 0 auto;
  /* Chuyển backdrop-filter sang lớp nền để tránh làm mờ icon */
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border-radius: 32px;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}
.search-wrap:focus-within {
  background: rgba(255, 255, 255, 0.25); 
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.search-icon {
  padding-left: 18px;
  display: flex;
  align-items: center;
  z-index: 2; /* Đảm bảo icon luôn nằm trên lớp filter */
}

.icon-img {
  width: 18px;
  height: 18px;
  object-fit: contain;
  /* Nếu ảnh gốc là màu đen, dùng filter dưới để chuyển sang trắng cho rõ */
  filter: brightness(0) invert(1); 
  opacity: 0.9;
}

.search-input {
  width: 100%;
  padding: 14px 16px 14px 12px; /* Giảm padding-left vì đã có search-icon padding */
  border: none;
  background: transparent; /* Quan trọng: để trong suốt để thấy nền của search-wrap */
  color: #fff;
  font-size: 15px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}



.search-clear {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: rgba(255,255,255,0.7);
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

/* ── Stats bar ─────────────────────────────────────────── */
.stats-bar {
  background: #fff;
  border-bottom: 1px solid #e8eaed;
  padding: 12px 24px;
}

.stats-container {
  max-width: 1300px;
  margin: 0 auto;
}

.stats-count {
  font-size: 14px;
  color: #666;
}

.stats-count strong {
  color: #1a3a5c;
  font-size: 16px;
}

/* ── Loading / Error / Empty ───────────────────────────── */
.loading-wrap,
.error-wrap,
.empty-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 24px;
  color: #666;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #1a3a5c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.btn-retry {
  padding: 10px 24px;
  background: #1a3a5c;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

/* ── Cards grid ────────────────────────────────────────── */
.cards-section {
  padding: 40px 24px 60px;
}

.cards-grid {
  max-width: 1300px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

@media (max-width: 1100px) { .cards-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 760px)  { .cards-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px)  { .cards-grid { grid-template-columns: 1fr; } }

/* ── Card ──────────────────────────────────────────────── */
.scholarship-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.scholarship-card.clickable {
  cursor: pointer;
}

.scholarship-card.clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 28px rgba(26, 58, 92, 0.15);
}

/* Top half — logo area */
.card-logo-area {
  background: linear-gradient(145deg, #f0f4f9 0%, #e3ecf7 100%);
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.uni-logo {
  max-width: 120px;
  max-height: 90px;
  object-fit: contain;
  border-radius: 6px;
}

.logo-placeholder {
  font-size: 52px;
  opacity: 0.5;
}

/* Bottom half — info */
.card-info {
  padding: 18px 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.uni-name {
  font-size: 11px;
  font-weight: 600;
  color: #1a73e8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scholarship-name {
  font-size: 15px;
  font-weight: 700;
  color: #1a3a5c;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.info-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.info-label {
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  min-width: 52px;
  flex-shrink: 0;
}

.info-chip {
  background: #e8f0fe;
  color: #1a3a5c;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 160px;
}

.info-value {
  font-size: 13px;
  color: #444;
}

.value-highlight {
  font-weight: 700;
  color: #2e7d32;
  font-size: 14px;
}
</style>
