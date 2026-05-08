<template>
  <div class="detail-page">
    <AppHeader />

    <div v-if="loading" class="loading-state">
      <a-spin size="large" />
    </div>
    <template v-else>
      <!-- Hero -->
      <div class="uni-hero">
        <div class="hero-inner">
          <div class="hero-main">
            <div class="hero-logo">
              <img v-if="university.logo" :src="university.logo" :alt="university.name" class="logo-img" />
              <div v-else class="logo-placeholder">
                <span>{{ university.name?.charAt(0) }}</span>
              </div>
            </div>
            <div class="hero-content">
              <h1 class="hero-name">{{ university.name }}</h1>
              <p class="hero-location">{{ university.city }}, {{ university.country }}</p>
              <div class="hero-badges">
                <span v-if="university.rank_int" class="hero-rank-badge">
                  #{{ university.rank_int }} UC World Ranking
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Body: sidebar + content -->
      <div class="body-wrap">
        <!-- Sidebar TOC -->
        <aside class="toc-sidebar">
          <div class="toc-card">
            <p class="toc-title">Table of contents</p>
            <ul class="toc-list">
              <li
                v-for="sec in sections"
                :key="sec.key"
                :class="['toc-item', { active: activeSection === sec.key }]"
                @click="scrollTo(sec.key)"
              >
                {{ sec.label }}
              </li>
            </ul>
          </div>
        </aside>

        <!-- Main content: all sections stacked -->
        <div class="main-content">

          <!-- Entry Requirements -->
          <section :id="'sec-entry'" class="content-section" ref="el_entry">
            <h2 class="sec-heading">Entry Requirements</h2>
            <div class="degree-block">
              <h3 class="degree-heading">Bachelor's Degree</h3>
              <div v-if="bachelorCards.length" class="req-cards">
                <div v-for="card in bachelorCards" :key="card.label" class="req-card">
                  <div class="req-label">{{ card.label }}</div>
                  <div class="req-value">{{ card.value }}</div>
                  <div class="req-plus">+</div>
                </div>
              </div>
              <p v-else class="no-data">No data available</p>
            </div>
            <div class="degree-block">
              <h3 class="degree-heading">Master's Degree</h3>
              <div v-if="masterCards.length" class="req-cards">
                <div v-for="card in masterCards" :key="card.label" class="req-card">
                  <div class="req-label">{{ card.label }}</div>
                  <div class="req-value">{{ card.value }}</div>
                  <div class="req-plus">+</div>
                </div>
              </div>
              <p v-else class="no-data">No data available</p>
            </div>
          </section>

          <!-- Student Information -->
          <section :id="'sec-students'" class="content-section" ref="el_students">
            <h2 class="sec-heading">Student Information</h2>
            <div class="student-grid">
              <div class="student-card">
                <p class="stu-label">Total Students</p>
                <p class="stu-value">{{ formatNumber(detailInfo?.total_stu) }}</p>
                <div class="stu-bar-track">
                  <div class="stu-bar-ug" :style="{ width: toPercent(detailInfo?.ug_rate) }"></div>
                  <div class="stu-bar-pg" :style="{ width: toPercent(detailInfo?.pg_rate) }"></div>
                </div>
                <p class="stu-legend">
                  <span><span class="dot dot-ug"></span> UG students {{ detailInfo?.ug_rate || '0%' }}</span>
                  <span><span class="dot dot-pg"></span> PG students {{ detailInfo?.pg_rate || '0%' }}</span>
                </p>
              </div>
              <div class="student-card">
                <p class="stu-label">Total International Students</p>
                <p class="stu-value">{{ formatNumber(detailInfo?.inter_total) }}</p>
                <div class="stu-bar-track">
                  <div class="stu-bar-ug" :style="{ width: toPercent(detailInfo?.inter_ug_rate) }"></div>
                  <div class="stu-bar-pg" :style="{ width: toPercent(detailInfo?.inter_pg_rate) }"></div>
                </div>
                <p class="stu-legend">
                  <span><span class="dot dot-ug"></span> UG students {{ detailInfo?.inter_ug_rate || '0%' }}</span>
                  <span><span class="dot dot-pg"></span> PG students {{ detailInfo?.inter_pg_rate || '0%' }}</span>
                </p>
              </div>
            </div>
          </section>

          <!-- Scholarships -->
          <section :id="'sec-scholarship'" class="content-section" ref="el_scholarship">
            <h2 class="sec-heading">Scholarships</h2>
            <div v-if="scholarships.length === 0" class="empty-scholarships">
              No scholarships available for this university.
            </div>
            <div v-else class="scholarship-list">
              <div v-for="sch in scholarships" :key="sch.id" class="scholarship-card">
                <div class="sch-header">
                  <span class="sch-name">{{ sch.name }}</span>
                  <span :class="['sch-criteria-badge', sch.criteria == '1' ? 'bachelor' : 'master']">
                    {{ sch.criteria == '1' ? 'Bachelor' : sch.criteria == '2' ? 'Master' : sch.criteria }}
                  </span>
                </div>
                <div class="sch-details">
                  <div class="sch-detail-item" v-if="sch.value">
                    <span class="sch-detail-label">Value</span>
                    <span class="sch-detail-val">${{ Number(sch.value).toLocaleString() }}</span>
                  </div>
                  <div class="sch-detail-item" v-if="sch.duration">
                    <span class="sch-detail-label">Duration</span>
                    <span class="sch-detail-val">{{ sch.duration }} years</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Tuition Fees -->
          <section :id="'sec-fee'" class="content-section" ref="el_fee">
            <h2 class="sec-heading">Tuition Fees</h2>
            <div class="info-list">
              <div class="info-item">
                <span class="info-key">International Tuition Fee:</span>
                <span class="info-val highlight">{{ detailInfo?.fee || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-key">Domestic Acceptance Rate:</span>
                <span class="info-val">{{ detailInfo?.domestic || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-key">International Acceptance Rate:</span>
                <span class="info-val">{{ detailInfo?.international || 'N/A' }}</span>
              </div>
            </div>
          </section>

          <!-- Ranking -->
          <section :id="'sec-ranking'" class="content-section" ref="el_ranking">
            <h2 class="sec-heading">Ranking</h2>
            <div v-if="rankingScores.length" class="ranking-categories">
              <div v-for="cat in rankingScores" :key="cat.category" class="ranking-cat-card">
                <div class="ranking-cat-header">{{ cat.category }}</div>
                <table class="ranking-table">
                  <thead>
                    <tr>
                      <th>Indicator</th>
                      <th>Score</th>
                      <th>World Rank</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ind in cat.indicators" :key="ind.name">
                      <td>{{ ind.name }}</td>
                      <td>{{ ind.score != null ? Number(ind.score).toFixed(1) : 'N/A' }}</td>
                      <td>
                        <span v-if="ind.rank != null" class="rank-badge">#{{ ind.rank }}</span>
                        <span v-else class="rank-na">N/A</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else class="scores-grid">
              <div v-for="cat in scoreCategories" :key="cat.key" class="score-box">
                <div class="score-label">{{ cat.label }}</div>
                <div class="score-num">{{ getCategoryScore(cat.key) }}</div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </template>

    <AppFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { universityAPI } from '@/services/api'
import { message } from 'ant-design-vue'
import AppHeader from '@/components/Header.vue'
import AppFooter from '@/components/Footer.vue'

const router = useRouter()
const route = useRoute()

const MOCK_UNIVERSITY = {
  name: 'Massachusetts Institute of Technology (MIT)',
  city: 'Cambridge',
  country: 'United States',
  rank: 1,
  logo: null,
  scores: {
    research_discovery: { a: 99.2, b: 97.5 },
    learning_experience: { a: 95.1, b: 93.4 },
    employability: { a: 100, b: 98.7 },
    global_engagement: { a: 92.3, b: 90.1 },
    sustainability: { a: 85.6, b: 83.2 },
  },
  detail_info: {
    fee: '$57,986 / year',
    scholarship: true,
    domestic: '7.3%',
    international: '4.1%',
    english_test: 'TOEFL / IELTS',
    academic_test: 'SAT / ACT',
    total_stu: '11,934',
    ug_rate: '44%',
    pg_rate: '56%',
    inter_total: '3,848',
    inter_ug_rate: '38%',
    inter_pg_rate: '62%',
  },
}

const MOCK_BACH_REQ = { sat: '1500', gpa: '4.0', toefl: '100', ielts: '7.5' }
const MOCK_MASTER_REQ = { gre: '330', gmat: '730', toefl: '100', ielts: '7.0' }

const university = ref({})
const detailInfo = ref(null)
const entryRequirements = ref(null)
const masterRequirements = ref(null)
const rankingScores = ref([])
const scholarships = ref([])
const loading = ref(true)
const activeSection = ref('entry')

const sections = [
  { key: 'entry', label: 'Entry Requirements' },
  { key: 'students', label: 'Student Information' },
  { key: 'scholarship', label: 'Scholarships' },
  { key: 'fee', label: 'Tuition Fees' },
  { key: 'ranking', label: 'Ranking' },
]

const scoreCategories = [
  { key: 'research_discovery', label: 'Research & Discovery' },
  { key: 'learning_experience', label: 'Learning Experience' },
  { key: 'employability', label: 'Employability' },
  { key: 'global_engagement', label: 'Global Engagement' },
  { key: 'sustainability', label: 'Sustainability' },
]

const REQ_KEYS = new Set(['SAT', 'GRE', 'GMAT', 'ACT', 'ATAR', 'GPA', 'TOEFL', 'IELTS',
                          'sat', 'gre', 'gmat', 'act', 'atar', 'gpa', 'toefl', 'ielts'])

const REQ_LABELS = {
  sat: 'SAT', gre: 'GRE', gmat: 'GMAT', act: 'ACT',
  atar: 'ATAR', gpa: 'GPA', toefl: 'TOEFL', ielts: 'IELTS',
}

const buildReqCards = (data) => {
  if (!data) return []
  return Object.entries(data)
    .filter(([k, v]) =>
      REQ_KEYS.has(k) &&
      v != null && v !== '' && String(v) !== '0' && String(v).toUpperCase() !== 'N/A'
    )
    .map(([k, v]) => ({ label: REQ_LABELS[k.toLowerCase()] || k.toUpperCase(), value: v }))
}

const bachelorCards = computed(() => buildReqCards(entryRequirements.value))

const masterCards = computed(() => buildReqCards(masterRequirements.value))

const getCategoryScore = (key) => {
  const cat = university.value.scores?.[key]
  if (!cat) return 'N/A'
  const vals = Object.values(cat).filter(v => v != null)
  return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 'N/A'
}

const formatNumber = (val) => {
  if (!val) return '0'
  const n = parseInt(String(val).replace(/,/g, ''))
  return isNaN(n) ? val : n.toLocaleString()
}

const toPercent = (rate) => {
  if (!rate) return '0%'
  return String(rate).includes('%') ? rate : rate + '%'
}

// Scroll to section
const scrollTo = (key) => {
  const el = document.getElementById(`sec-${key}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeSection.value = key
  }
}

// Update active section on scroll
const handleScroll = () => {
  for (const sec of [...sections].reverse()) {
    const el = document.getElementById(`sec-${sec.key}`)
    if (el && el.getBoundingClientRect().top <= 120) {
      activeSection.value = sec.key
      return
    }
  }
  activeSection.value = sections[0].key
}

onMounted(async () => {
  loading.value = true
  try {
    const uniId = route.params.id
    const [uniRes, rankingRes] = await Promise.allSettled([
      universityAPI.getById(uniId),
      universityAPI.getRankingScores(uniId),
    ])
    if (uniRes.status === 'fulfilled') {
      university.value = uniRes.value
      detailInfo.value = uniRes.value.detail_info
      // Entry requirements are already embedded in the university detail response
      const entryList = uniRes.value?.entry_requirements || []
      entryRequirements.value = entryList.find(r => r.degree_type === 1) || null
      masterRequirements.value = entryList.find(r => r.degree_type === 2) || null
      scholarships.value = uniRes.value.scholarships || []
    } else {
      const err = uniRes.reason
      const detail = err?.response?.data?.detail || 'Cannot connect to the database. Please try again later.'
      message.error(detail)
    }
    rankingScores.value = rankingRes.status === 'fulfilled' ? (rankingRes.value || []) : []
  } catch (err) {
    const detail = err?.response?.data?.detail || 'Cannot connect to the database. Please try again later.'
    message.error(detail)
  } finally {
    loading.value = false
  }
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const goBack = () => router.back()
const compareThis = () => message.success('Added to comparison')
</script>

<style scoped>
.detail-page { background: #f5f7fa; min-height: 100vh; font-family: sans-serif; display: flex; flex-direction: column; }

/* Hero */
.uni-hero { background: linear-gradient(135deg, #0a1628 0%, #0d2144 40%, #0a3060 70%, #0d4a8a 100%); color: #fff; padding: 28px 0; }
.hero-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.hero-main { display: flex; align-items: center; gap: 24px; }
.hero-logo {
  flex-shrink: 0; width: 90px; height: 90px;
  background: #fff; border-radius: 8px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
}
.logo-img { width: 100%; height: 100%; object-fit: contain; padding: 6px; }
.logo-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  font-size: 36px; font-weight: 700; color: #1a39ac;
}
.hero-content { flex: 1; }
.hero-name { font-size: 26px; font-weight: 700; margin: 0 0 5px; }
.hero-location { font-size: 14px; opacity: 0.85; margin-bottom: 12px; }
.hero-rank-badge {
  background: #fff; color: #1a39ac; padding: 4px 14px;
  border-radius: 4px; font-weight: 600; font-size: 13px; display: inline-block;
}
.btn-back { background: transparent; border: 1px solid #fff; color: #fff; padding: 8px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; }
.btn-compare { background: #fff; border: none; color: #1a39ac; padding: 8px 20px; border-radius: 4px; font-weight: 600; cursor: pointer; font-size: 14px; }

/* Body layout */
.body-wrap {
  max-width: 1200px; margin: 32px auto 48px; padding: 0 24px;
  display: flex; gap: 28px; align-items: flex-start; flex: 1;
}

/* Sidebar TOC */
.toc-sidebar { width: 240px; flex-shrink: 0; position: sticky; top: 24px; }
.toc-card {
  background: #fff; border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07); padding: 20px 0;
}
.toc-title { font-weight: 700; font-size: 15px; color: #222; margin: 0 0 12px; padding: 0 20px; }
.toc-list { list-style: none; margin: 0; padding: 0; }
.toc-item {
  padding: 10px 20px; font-size: 14px; color: #555;
  cursor: pointer; border-left: 3px solid transparent;
  transition: all 0.15s;
}
.toc-item:hover { color: #1a39ac; background: #f0f4ff; }
.toc-item.active { color: #1a39ac; font-weight: 600; border-left-color: #1a39ac; background: #f0f4ff; }

/* Main content */
.main-content { flex: 1; display: flex; flex-direction: column; gap: 28px; }
.content-section {
  background: #fff; border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07); padding: 36px 40px;
  scroll-margin-top: 24px;
}
.sec-heading { font-size: 20px; font-weight: 700; color: #222; margin: 0 0 28px; }

/* Entry Requirements */
.degree-block { margin-bottom: 28px; }
.degree-heading { font-size: 15px; font-weight: 600; color: #444; margin-bottom: 14px; }
.req-cards { display: flex; gap: 14px; flex-wrap: wrap; }
.req-card {
  background: #f4f4f4; width: 100px; height: 110px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border-radius: 6px;
}
.req-label { font-size: 12px; color: #777; margin-bottom: 8px; }
.req-value { font-size: 22px; font-weight: 700; color: #333; }
.req-plus { color: #999; font-size: 13px; margin-top: 4px; }
.no-data { color: #999; font-size: 14px; }

/* Student Stats */
.student-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.student-card { border: 1px solid #eee; padding: 22px; border-radius: 8px; }
.stu-label { color: #666; font-size: 14px; margin: 0 0 4px; }
.stu-value { font-size: 30px; font-weight: 700; margin: 8px 0; }
.stu-bar-track { height: 8px; background: #e0e0e0; border-radius: 4px; display: flex; margin: 14px 0; overflow: hidden; }
.stu-bar-ug { background: #a5b4fc; }
.stu-bar-pg { background: #312e81; }
.stu-legend { display: flex; gap: 20px; font-size: 13px; color: #666; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
.dot-ug { background: #a5b4fc; }
.dot-pg { background: #312e81; }

/* Info list */
.info-list { max-width: 580px; }
.info-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #f0f0f0; }
.info-key { color: #666; font-size: 14px; }
.info-val { font-weight: 600; font-size: 14px; }
.info-val.highlight { color: #1a39ac; font-size: 17px; }
.status-tag { padding: 3px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.status-tag.yes { background: #ecfdf5; color: #059669; }
.status-tag.no { background: #fef2f2; color: #dc2626; }

/* Scholarships */
.empty-scholarships { color: #888; font-size: 14px; padding: 12px 0; }
.scholarship-list { display: flex; flex-direction: column; gap: 16px; }
.scholarship-card { border: 1px solid #e0e7f5; border-radius: 8px; padding: 18px 20px; background: #f8faff; }
.sch-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.sch-name { font-weight: 600; font-size: 15px; color: #222; }
.sch-criteria-badge { padding: 3px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.sch-criteria-badge.bachelor { background: #eff6ff; color: #1a56db; }
.sch-criteria-badge.master { background: #f0fdf4; color: #16a34a; }
.sch-details { display: flex; gap: 32px; }
.sch-detail-item { display: flex; flex-direction: column; gap: 2px; }
.sch-detail-label { font-size: 12px; color: #888; }
.sch-detail-val { font-size: 14px; font-weight: 600; color: #333; }

/* Ranking */
.scores-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 36px; }
.score-label { color: #888; font-size: 14px; margin-bottom: 8px; }
.score-num { font-size: 34px; font-weight: 700; color: #333; }

.ranking-categories { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.ranking-cat-card { background: #f8faff; border: 1px solid #dce6f7; border-radius: 10px; overflow: hidden; }
.ranking-cat-header { background: #0487d9; color: #fff; font-weight: 700; font-size: 14px; padding: 10px 16px; }
.ranking-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.ranking-table thead tr { background: #eef3fb; }
.ranking-table th { padding: 8px 14px; text-align: left; color: #555; font-weight: 600; border-bottom: 1px solid #dce6f7; }
.ranking-table td { padding: 8px 14px; border-bottom: 1px solid #eef3fb; color: #333; }
.ranking-table tbody tr:last-child td { border-bottom: none; }
.ranking-table tbody tr:hover { background: #f0f5ff; }
.rank-badge { display: inline-block; background: #0487d9; color: #fff; font-weight: 700; font-size: 12px; padding: 2px 9px; border-radius: 12px; }
.rank-na { color: #aaa; font-style: italic; }

/* Loading */
.loading-state { display: flex; justify-content: center; align-items: center; height: 300px; }
</style>