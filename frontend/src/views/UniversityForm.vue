<template>
  <div class="form-wrapper">
    <Header :adminMode="true" />

    <div class="form-content">
      <!-- Page Header -->
      <div class="page-header">
        <button class="btn-back" @click="router.push('/admin')">← Back to System Management</button>
        <h1 class="page-title">{{ isEdit ? 'Edit University' : 'Add New University' }}</h1>
      </div>

      <form @submit.prevent="handleSubmit" class="sections-wrap">

        <!-- ── SECTION 1: Basic Information ─────────────────────────── -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-num">1</span>
            <h2 class="section-title">Basic Information</h2>
          </div>
          <div class="grid-2">
            <div class="field">
              <label>University Name <span class="req">*</span></label>
              <input v-model="form.name" required placeholder="" />
            </div>
            <div class="field">
              <label>City</label>
              <input v-model="form.city" placeholder="" />
            </div>
            <div class="field">
              <label>Region</label>
              <select v-model.number="form.region_id">
                <option :value="null">-- Select Region --</option>
                <option :value="1">Asia</option>
                <option :value="2">Europe</option>
                <option :value="3">North America</option>
                <option :value="4">Latin America</option>
                <option :value="5">Oceania</option>
                <option :value="6">Africa</option>
              </select>
            </div>
            <div class="field">
              <label>Country <span class="req">*</span></label>
              <select v-model.number="form.country_id" required>
                <option value="" disabled>-- Select Country --</option>
                <option v-for="c in filteredCountries" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
              <span v-if="form.region_id && filteredCountries.length === 0" class="field-hint">No countries found for this region</span>
            </div>
            <div class="field">
              <label>Logo URL</label>
              <input v-model="form.logo" placeholder="https://..." />
            </div>
            <div class="field">
              <label>Path / Slug</label>
              <input v-model="form.path" placeholder="" />
            </div>
            <div class="field">
              <label>World Rank</label>
              <input v-model.number="form.rank_int" type="number" min="1" placeholder="" />
            </div>
            <div class="field">
              <label>Overall Score</label>
              <input v-model.number="form.overall_score" type="number" step="0.01" min="0" max="100" placeholder="" />
            </div>
          </div>
          <!-- Logo preview -->
          <div v-if="form.logo" class="logo-preview">
            <span class="preview-label">Logo preview:</span>
            <img :src="form.logo" alt="Logo" @error="e => e.target.style.display='none'" class="logo-img" />
          </div>
        </div>

        <!-- ── SECTION 2: Detail Information ───────────────────────── -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-num">2</span>
            <h2 class="section-title">Detail Information</h2>
          </div>
          <div class="grid-2">
            <div class="field">
              <label>Tuition Fee (USD/year)</label>
              <input v-model="form.detail.fee" type="number" step="0.01" min="0" placeholder="" />
            </div>
            <div class="field field-checkbox">
              <label>Scholarship Available</label>
              <div class="toggle-wrap">
                <input id="scholarship" v-model="form.detail.scholarship" type="checkbox" class="toggle-input" />
                <label for="scholarship" class="toggle-label">
                  <span>{{ form.detail.scholarship ? 'Yes' : 'No' }}</span>
                </label>
              </div>
            </div>
            <div class="field">
              <label>Domestic Student Rate (%)</label>
              <input v-model="form.detail.domestic" type="number" step="0.1" min="0" max="100" placeholder="" />
            </div>
            <div class="field">
              <label>International Student Rate (%)</label>
              <input v-model="form.detail.international" type="number" step="0.1" min="0" max="100" placeholder="" />
            </div>
            <div class="field">
              <label>English Test Requirements</label>
              <input v-model="form.detail.english_test" placeholder="" />
            </div>
            <div class="field">
              <label>Academic Test Requirements</label>
              <input v-model="form.detail.academic_test" placeholder="" />
            </div>
            <div class="field">
              <label>Total Students</label>
              <input v-model.number="form.detail.total_stu" type="number" min="0" placeholder="" />
            </div>
            <div class="field">
              <label>Undergraduate Rate (%)</label>
              <input v-model="form.detail.ug_rate" type="number" step="0.1" min="0" max="100" placeholder="" />
            </div>
            <div class="field">
              <label>Postgraduate Rate (%)</label>
              <input v-model="form.detail.pg_rate" type="number" step="0.1" min="0" max="100" placeholder="" />
            </div>
            <div class="field">
              <label>Total International Students</label>
              <input v-model.number="form.detail.inter_total" type="number" min="0" placeholder="" />
            </div>
            <div class="field">
              <label>Intl Undergraduate Rate (%)</label>
              <input v-model="form.detail.inter_ug_rate" type="number" step="0.1" min="0" max="100" placeholder="" />
            </div>
            <div class="field">
              <label>Intl Postgraduate Rate (%)</label>
              <input v-model="form.detail.inter_pg_rate" type="number" step="0.1" min="0" max="100" placeholder="" />
            </div>
          </div>
        </div>

        <!-- ── SECTION 3: Entry Requirements ──────────────────────── -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-num">3</span>
            <h2 class="section-title">Entry Requirements</h2>
          </div>
          <div class="degree-tabs">
            <button
              v-for="tab in degreeTabs"
              :key="tab.value"
              type="button"
              :class="['degree-tab', { active: activeDegree === tab.value }]"
              @click="activeDegree = tab.value"
            >{{ tab.label }}</button>
          </div>
          <div class="grid-4">
            <div v-for="test in testFields" :key="test.key" class="field">
              <label>{{ test.label }}</label>
              <input
                v-model="form.entry[activeDegree][test.key]"
                :placeholder="test.placeholder"
              />
            </div>
          </div>
        </div>

        <!-- ── SECTION 4: Ranking Scores ───────────────────────────── -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-num">4</span>
            <h2 class="section-title">Ranking Scores</h2>
          </div>

          <div v-for="cat in scoreCategories" :key="cat.key" class="score-category">
            <div class="score-cat-header">{{ cat.label }}</div>
            <div class="score-grid">
              <div v-for="ind in cat.indicators" :key="ind.key" class="score-field">
                <div class="score-ind-label">{{ ind.label }}</div>
                <div class="score-inputs">
                  <div class="score-input-group">
                    <span class="score-input-prefix">Score</span>
                    <input
                      v-model="form.scores[cat.key][ind.key + '_score']"
                      type="number" step="0.1" min="0" max="100"
                      placeholder="0–100"
                      class="score-input"
                    />
                  </div>
                  <div class="score-input-group">
                    <span class="score-input-prefix">Rank</span>
                    <input
                      v-model="form.scores[cat.key][ind.key + '_rank']"
                      type="number" min="1"
                      placeholder=""
                      class="score-input"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Submit ──────────────────────────────────────────────── -->
        <div class="form-footer">
          <button type="button" class="btn-cancel" @click="router.push('/admin')">Cancel</button>
          <button type="submit" class="btn-submit" :disabled="submitting">
            <span v-if="submitting" class="btn-spinner"></span>
            {{ submitting ? 'Saving...' : (isEdit ? 'Update University' : 'Add University') }}
          </button>
        </div>

      </form>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { universityAPI, countryAPI } from '@/services/api'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const router = useRouter()

const uniId = computed(() => route.params.id ? Number(route.params.id) : null)
const isEdit = computed(() => !!uniId.value)
const submitting = ref(false)
const activeDegree = ref(1)
const countries = ref([])

const filteredCountries = computed(() => countries.value)

const degreeTabs = [
  { value: 1, label: 'Bachelor (UG)' },
  { value: 2, label: 'Master / PhD (PG)' }
]

const testFields = [
  { key: 'SAT',   label: 'SAT',   placeholder: '' },
  { key: 'ACT',   label: 'ACT',   placeholder: '' },
  { key: 'GRE',   label: 'GRE',   placeholder: '' },
  { key: 'GMAT',  label: 'GMAT',  placeholder: '' },
  { key: 'ATAR',  label: 'ATAR',  placeholder: '' },
  { key: 'GPA',   label: 'GPA',   placeholder: '' },
  { key: 'TOEFL', label: 'TOEFL', placeholder: '' },
  { key: 'IELTS', label: 'IELTS', placeholder: '' }
]

const scoreCategories = [
  {
    key: 'research_discovery',
    label: 'Research & Discovery',
    indicators: [
      { key: 'academic_reputation',  label: 'Academic Reputation' },
      { key: 'citations_per_faculty', label: 'Citations per Faculty' },
      { key: 'intl_research_network', label: 'International Research Network' }
    ]
  },
  {
    key: 'learning_experience',
    label: 'Learning Experience',
    indicators: [
      { key: 'faculty_student_ratio', label: 'Faculty Student Ratio' }
    ]
  },
  {
    key: 'employability',
    label: 'Employability',
    indicators: [
      { key: 'employer_reputation',   label: 'Employer Reputation' },
      { key: 'employment_outcomes',   label: 'Employment Outcomes' }
    ]
  },
  {
    key: 'global_engagement',
    label: 'Global Engagement',
    indicators: [
      { key: 'intl_student_ratio',    label: 'International Student Ratio' },
      { key: 'intl_faculty_ratio',    label: 'International Faculty Ratio' },
      { key: 'intl_student_diversity', label: 'International Student Diversity' }
    ]
  },
  {
    key: 'sustainability',
    label: 'Sustainability',
    indicators: [
      { key: 'sustainability_score',  label: 'Sustainability Score' }
    ]
  }
]

const makeEntryTemplate = () => ({ SAT: '', ACT: '', GRE: '', GMAT: '', ATAR: '', GPA: '', TOEFL: '', IELTS: '' })
const makeScoreTemplate = () => {
  const s = {}
  scoreCategories.forEach(cat => {
    s[cat.key] = {}
    cat.indicators.forEach(ind => {
      s[cat.key][ind.key + '_score'] = ''
      s[cat.key][ind.key + '_rank'] = ''
    })
  })
  return s
}

const form = ref({
  name: '',
  city: '',
  country_id: '',
  region_id: null,
  logo: '',
  path: '',
  rank_int: '',
  overall_score: '',
  detail: {
    fee: '',
    scholarship: false,
    domestic: '',
    international: '',
    english_test: '',
    academic_test: '',
    total_stu: '',
    ug_rate: '',
    pg_rate: '',
    inter_total: '',
    inter_ug_rate: '',
    inter_pg_rate: ''
  },
  entry: {
    1: makeEntryTemplate(),
    2: makeEntryTemplate()
  },
  scores: makeScoreTemplate()
})

const populateForm = (data) => {
  form.value.name = data.name || ''
  form.value.city = data.city || ''
  form.value.country_id = data.country_id || ''
  form.value.region_id = data.region_id || null
  form.value.logo = data.logo || ''
  form.value.path = data.path || ''
  form.value.rank_int = data.rank_int || ''
  form.value.overall_score = data.overall_score || ''

  if (data.detail_info) {
    const d = data.detail_info
    Object.keys(form.value.detail).forEach(k => {
      if (d[k] !== undefined) form.value.detail[k] = d[k]
    })
  }

  if (data.entry_requirements) {
    data.entry_requirements.forEach(er => {
      const deg = er.degree_type
      if (form.value.entry[deg]) {
        testFields.forEach(t => {
          form.value.entry[deg][t.key] = er[t.key] || ''
        })
      }
    })
  }

  const scoreSrc = data.edit_scores || data.scores
  if (scoreSrc) {
    scoreCategories.forEach(cat => {
      const catData = scoreSrc[cat.key]
      if (catData) {
        cat.indicators.forEach(ind => {
          form.value.scores[cat.key][ind.key + '_score'] = catData[ind.key]?.score ?? ''
          form.value.scores[cat.key][ind.key + '_rank'] = catData[ind.key]?.rank ?? ''
        })
      }
    })
  }
}

onMounted(async () => {
  try {
    countries.value = await countryAPI.getAll()
  } catch {
    // countries stays empty — user can still type manually if needed
  }
  if (!isEdit.value) return
  try {
    const res = await universityAPI.getById(uniId.value)
    populateForm(res)
  } catch {
    message.warning('Could not load university data')
  }
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    // Flatten nested scores: {cat: {key_score, key_rank}} → {key: {score, rank}}
    const scoresFlat = {}
    scoreCategories.forEach(cat => {
      cat.indicators.forEach(ind => {
        const sc = form.value.scores[cat.key]?.[ind.key + '_score']
        const rk = form.value.scores[cat.key]?.[ind.key + '_rank']
        if (sc !== '' || rk !== '') {
          scoresFlat[ind.key] = {
            score: sc !== '' ? Number(sc) : null,
            rank:  rk !== '' ? Number(rk) : null,
          }
        }
      })
    })

    const payload = {
      name:          form.value.name,
      city:          form.value.city || null,
      country_id:    form.value.country_id || null,
      logo:          form.value.logo || null,
      path:          form.value.path || null,
      rank_int:      form.value.rank_int !== '' ? Number(form.value.rank_int) : null,
      overall_score: form.value.overall_score !== '' ? Number(form.value.overall_score) : null,
      detail: (() => {
        const toStr = v => (v != null && v !== '') ? String(v) : null
        const d = form.value.detail
        return {
          fee:           toStr(d.fee),
          scholarship:   d.scholarship,
          domestic:      toStr(d.domestic),
          international: toStr(d.international),
          english_test:  d.english_test || null,
          academic_test: d.academic_test || null,
          total_stu:     toStr(d.total_stu),
          ug_rate:       toStr(d.ug_rate),
          pg_rate:       toStr(d.pg_rate),
          inter_total:   toStr(d.inter_total),
          inter_ug_rate: toStr(d.inter_ug_rate),
          inter_pg_rate: toStr(d.inter_pg_rate),
        }
      })(),
      entry: {
        '1': form.value.entry[1],
        '2': form.value.entry[2],
      },
      scores: scoresFlat,
    }

    if (isEdit.value) {
      await universityAPI.update(uniId.value, payload)
    } else {
      await universityAPI.create(payload)
    }
    message.success(isEdit.value ? 'University updated successfully!' : 'University added successfully!')
    router.push('/admin')
  } catch (err) {
    const detail = err.response?.data?.detail
    message.error(detail ? String(detail) : 'Failed to save. Please try again.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.form-content {
  flex: 1;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
  padding: 32px 24px 60px;
}

/* Page Header */
.page-header { margin-bottom: 28px; }
.btn-back {
  background: none; border: 1px solid #d0d5dd;
  border-radius: 6px; padding: 7px 14px;
  cursor: pointer; font-size: 13px; color: #374151;
  margin-bottom: 12px; transition: background 0.2s;
}
.btn-back:hover { background: #f0f4ff; }
.page-title { font-size: 24px; font-weight: 700; color: #1a1a2e; margin: 0; }

/* Sections */
.sections-wrap { display: flex; flex-direction: column; gap: 24px; }

.form-section {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: #f0f4ff;
  border-bottom: 1px solid #e0e7ff;
}
.section-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: #1a73e8; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin: 0; }

/* Grid layouts */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px 24px;
  padding: 24px;
}
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px 24px;
  padding: 24px;
}
@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

/* Fields */
.field { display: flex; flex-direction: column; gap: 6px; }
.field label {
  font-size: 13px; font-weight: 600; color: #374151;
}
.req { color: #e53e3e; }
.field-hint { font-size: 12px; color: #9ca3af; margin-top: 2px; }
.field input, .field select, .field textarea {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 9px 12px;
  font-size: 14px;
  color: #222;
  outline: none;
  background: #fff;
  transition: border 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.field input:focus, .field select:focus, .field textarea:focus {
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26,115,232,0.12);
}

/* Checkbox toggle */
.field-checkbox { justify-content: flex-start; }
.toggle-wrap { display: flex; align-items: center; gap: 10px; }
.toggle-input { width: 18px; height: 18px; cursor: pointer; accent-color: #1a73e8; }
.toggle-label { font-size: 14px; color: #555; cursor: pointer; }

/* Logo preview */
.logo-preview {
  display: flex; align-items: center; gap: 12px;
  padding: 0 24px 20px;
}
.preview-label { font-size: 13px; color: #888; }
.logo-img { max-height: 50px; max-width: 120px; object-fit: contain; border-radius: 4px; }

/* Degree tabs */
.degree-tabs {
  display: flex; gap: 0;
  padding: 20px 24px 0;
}
.degree-tab {
  padding: 8px 22px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: all 0.15s;
}
.degree-tab:first-child { border-radius: 6px 0 0 6px; }
.degree-tab:last-child  { border-radius: 0 6px 6px 0; border-left: none; }
.degree-tab.active { background: #1a73e8; color: #fff; border-color: #1a73e8; font-weight: 600; }

/* Score categories */
.score-category { padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.score-category:last-child { border-bottom: none; }
.score-cat-header {
  font-size: 13px; font-weight: 700; color: #1a73e8;
  text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 16px;
  padding-bottom: 6px;
  border-bottom: 2px solid #e0e7ff;
}
.score-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.score-field {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px 16px;
  min-width: 200px;
  flex: 1;
}
.score-ind-label {
  font-size: 13px; font-weight: 600; color: #374151;
  margin-bottom: 10px;
  text-align: center;
}
.score-inputs { display: flex; gap: 10px; }
.score-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.score-input-prefix {
  font-size: 11px; color: #888; font-weight: 600; text-transform: uppercase;
}
.score-input {
  border: 1px solid #d1d5db;
  border-radius: 5px;
  padding: 7px 8px;
  font-size: 13px;
  text-align: center;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border 0.2s, box-shadow 0.2s;
}
.score-input:focus {
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26,115,232,0.1);
}

/* Footer */
.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 14px;
  padding-top: 8px;
}
.btn-cancel {
  padding: 10px 28px;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  background: #fff;
  color: #555;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover { background: #f3f4f6; }
.btn-submit {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 32px;
  border: none;
  border-radius: 7px;
  background: #1a73e8;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-submit:hover:not(:disabled) { background: #1558b0; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
