<template>
  <div class="form-wrapper">
    <Header />

    <div class="form-content">
      <!-- Page Header -->
      <div class="page-header">
        <button class="btn-back" @click="router.push('/admin?tab=accounts')">← Back to System Management</button>
        <h1 class="page-title">{{ isEdit ? 'Edit Account' : 'Add New Account' }}</h1>
      </div>

      <form @submit.prevent="handleSubmit" class="sections-wrap">

        <!-- ── SECTION 1: Account Information ──────────────────────── -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-num">1</span>
            <h2 class="section-title">Account Information</h2>
          </div>

          <!-- Avatar -->
          <div class="avatar-row">
            <div class="avatar-box">
              <img
                v-if="form.image"
                :src="form.image"
                class="avatar-img"
                @error="e => e.target.style.display='none'"
              />
              <div v-else class="avatar-placeholder">👤</div>
            </div>
            <div class="avatar-fields">
              <div class="field" style="flex:1">
                <label>Profile Image URL</label>
                <input v-model="form.image" placeholder="https://..." />
              </div>
            </div>
          </div>

          <div class="grid-2">
            <div class="field">
              <label>First Name <span class="req">*</span></label>
              <input v-model="form.first_name" required placeholder="e.g. Alice" />
            </div>
            <div class="field">
              <label>Last Name <span class="req">*</span></label>
              <input v-model="form.last_name" required placeholder="e.g. Nguyen" />
            </div>
            <div class="field">
              <label>Email <span class="req">*</span></label>
              <input v-model="form.email" type="email" required placeholder="e.g. alice@example.com" />
            </div>
            <div class="field">
              <label>{{ isEdit ? 'New Password (leave blank to keep)' : 'Password' }} {{ isEdit ? '' : '*' }}</label>
              <div class="password-wrap">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  :required="!isEdit"
                  placeholder="••••••••"
                />
                <button type="button" class="toggle-eye" @click="showPassword = !showPassword" tabindex="-1">
                  <!-- eye-open -->
                  <svg v-if="showPassword" viewBox="64 64 896 896" width="1em" height="1em" fill="currentColor">
                    <path d="M942.2 486.2C847.4 286.5 704.1 186 512 186c-192.2 0-335.4 100.5-430.2 300.3a60.3 60.3 0 000 51.5C176.6 737.5 319.9 838 512 838c192.2 0 335.4-100.5 430.2-300.3 7.7-16.2 7.7-35 0-51.5zM512 766c-161.3 0-279.4-81.8-362.7-254C232.6 339.8 350.7 258 512 258c161.3 0 279.4 81.8 362.7 254C791.5 684.2 673.4 766 512 766zm-4-430c-97.2 0-176 78.8-176 176s78.8 176 176 176 176-78.8 176-176-78.8-176-176-176zm0 288c-61.9 0-112-50.1-112-112s50.1-112 112-112 112 50.1 112 112-50.1 112-112 112z"/>
                  </svg>
                  <!-- eye-closed -->
                  <svg v-else viewBox="64 64 896 896" width="1em" height="1em" fill="currentColor">
                    <path d="M942.2 486.2Q889.47 375.11 816.7 305l-50.89 50.89C807.31 395.53 843.45 447.4 874.7 512 791.5 684.2 673.4 766 512 766q-72.67 0-133.87-22.38L323 798.75Q408 838 512 838q288.3 0 430.2-300.3a60.29 60.29 0 000-51.5zm-63.57-320.64L836 122.88a8 8 0 00-11.32 0L715.31 232.2Q624.86 186 512 186q-288.3 0-430.2 300.3a60.3 60.3 0 000 51.5q56.69 119.4 136.5 191.41L112.48 835a8 8 0 000 11.31L155.17 889a8 8 0 0011.31 0l712.15-712.12a8 8 0 000-11.32zM149.3 512C232.6 339.8 350.7 258 512 258c54.54 0 104.13 9.36 149.12 27.33L589.87 357a176 176 0 00-237.28 237.29l-60.58 60.58C235.41 608.93 190.58 562.61 149.3 512zm248.38 131.72l94.72-94.72a48 48 0 1160.44 60.44l-94.72 94.72a176 176 0 01-60.44-60.44z"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="field">
              <label>Phone Number</label>
              <input v-model="form.phone_number" placeholder="e.g. +84 90 123 4567" />
            </div>
            <div class="field">
              <label>Gender</label>
              <select v-model="form.gender">
                <option :value="null">-- Select --</option>
                <option :value="1">Male</option>
                <option :value="0">Female</option>
              </select>
            </div>
            <div class="field">
              <label>Date of Birth</label>
              <input v-model="form.dob" type="date" />
            </div>
            <div class="field">
              <label>Country</label>
              <select v-model.number="form.country_id">
                <option :value="null">-- Select country --</option>
                <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="field">
              <label>Main Language</label>
              <input v-model="form.main_lang" placeholder="e.g. Vietnamese" />
            </div>
            <div class="field">
              <label>Additional Language</label>
              <input v-model="form.add_lang" placeholder="e.g. English, French" />
            </div>
            <div class="field">
              <label>Ethnic Group</label>
              <input v-model="form.ethnic_group" placeholder="e.g. Kinh" />
            </div>
            <div class="field field-full">
              <label>Special Notes</label>
              <textarea v-model="form.special" rows="2" placeholder="e.g. Disability, scholarship history..." />
            </div>
            <div class="field">
              <label>Role</label>
              <select v-model.number="form.role_id">
                <option :value="1">User</option>
                <option :value="2">Admin</option>
              </select>
            </div>
          </div>
        </div>

        <!-- ── SECTION 2: Study Background ────────────────────────── -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-num">2</span>
            <h2 class="section-title">Study Background</h2>
          </div>
          <div class="grid-2">
            <div class="field">
              <label>Education Level</label>
              <select v-model="form.study.level">
                <option value="">-- Select --</option>
                <option>High School</option>
                <option>Bachelor</option>
                <option>Master</option>
                <option>PhD</option>
              </select>
            </div>
            <div class="field">
              <label>Major</label>
              <input v-model="form.study.major" placeholder="e.g. Computer Science" />
            </div>
            <div class="field">
              <label>Academic Rate (%)</label>
              <input v-model.number="form.study.academic_rate" type="number" step="0.1" min="0" max="100" placeholder="e.g. 8.5" />
            </div>
            <div class="field">
              <label>GPA</label>
              <input v-model.number="form.study.gpa" type="number" step="0.01" min="0" max="4" placeholder="e.g. 3.85" />
            </div>
            <div class="field">
              <label>Graduation Year</label>
              <input v-model.number="form.study.graduate_year" type="number" min="1990" max="2040" placeholder="e.g. 2024" />
            </div>
          </div>

          <!-- Test Scores -->
          <div class="test-scores-wrap">
            <div class="test-scores-title">Standardized Test Scores</div>
            <div class="grid-4">
              <div v-for="t in testScoreFields" :key="t.key" class="field">
                <label>{{ t.label }}</label>
                <input
                  v-model.number="form.study[t.key]"
                  type="number"
                  :step="t.step || 1"
                  :placeholder="t.placeholder"
                  min="0"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- ── Submit ──────────────────────────────────────────────── -->
        <div class="form-footer">
          <button type="button" class="btn-cancel" @click="router.push('/admin?tab=accounts')">Cancel</button>
          <button type="submit" class="btn-submit" :disabled="submitting">
            <span v-if="submitting" class="btn-spinner"></span>
            {{ submitting ? 'Saving...' : (isEdit ? 'Update Account' : 'Add Account') }}
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
import { userAPI, countryAPI } from '@/services/api'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const router = useRouter()

const userId = computed(() => route.params.id ? Number(route.params.id) : null)
const isEdit = computed(() => !!userId.value)
const submitting = ref(false)
const showPassword = ref(false)
const countries = ref([])

const testScoreFields = [
  { key: 'sat',          label: 'SAT',              step: 1,    placeholder: 'e.g. 1500' },
  { key: 'act',          label: 'ACT',              step: 0.1,  placeholder: 'e.g. 34' },
  { key: 'gre',          label: 'GRE',              step: 1,    placeholder: 'e.g. 320' },
  { key: 'gmat',         label: 'GMAT',             step: 1,    placeholder: 'e.g. 650' },
  { key: 'cat',          label: 'CAT',              step: 0.1,  placeholder: 'e.g. 95' },
  { key: 'stat',         label: 'STAT',             step: 0.1,  placeholder: 'e.g. 180' },
  { key: 'ielts',        label: 'IELTS',            step: 0.5,  placeholder: 'e.g. 7.0' },
  { key: 'toefl',        label: 'TOEFL',            step: 1,    placeholder: 'e.g. 100' },
  { key: 'pearson_test', label: 'Pearson Test',     step: 0.1,  placeholder: 'e.g. 65' },
  { key: 'cam_adv_test', label: 'Cambridge Adv.',   step: 0.1,  placeholder: 'e.g. 200' },
  { key: 'inter_bac',    label: 'Int\'l Baccalaureate', step: 0.1, placeholder: 'e.g. 38' }
]

const makeStudyTemplate = () => ({
  level: '',
  major: '',
  academic_rate: '',
  gpa: '',
  graduate_year: '',
  act: '',
  gmat: '',
  sat: '',
  cat: '',
  gre: '',
  stat: '',
  ielts: '',
  toefl: '',
  pearson_test: '',
  cam_adv_test: '',
  inter_bac: ''
})

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  image: '',
  phone_number: '',
  gender: null,
  dob: '',
  country_id: '',
  main_lang: '',
  add_lang: '',
  ethnic_group: '',
  special: '',
  role_id: 1,
  study: makeStudyTemplate()
})

const populateForm = (data) => {
  const fields = ['first_name','last_name','email','image','phone_number','gender',
                  'dob','country_id','main_lang','add_lang','ethnic_group','special','role_id']
  fields.forEach(k => { if (data[k] !== undefined) form.value[k] = data[k] })

  if (data.dob) {
    // Normalize to YYYY-MM-DD for <input type="date">
    form.value.dob = data.dob.split('T')[0]
  }

  if (data.study_background) {
    const sb = data.study_background
    Object.keys(form.value.study).forEach(k => {
      if (sb[k] !== undefined) form.value.study[k] = sb[k]
    })
  }
}

onMounted(async () => {
  try {
    countries.value = await countryAPI.getAll()
  } catch {
    // ignore — country list is optional
  }
  if (!isEdit.value) return
  try {
    const res = await userAPI.getUser(userId.value)
    populateForm(res)
  } catch {
    message.warning('Could not load account data')
  }
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    const payload = {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      phone_number: form.value.phone_number || null,
      country_id: form.value.country_id || null,
      gender: form.value.gender,
      dob: form.value.dob || null,
      ethnic_group: form.value.ethnic_group || null,
      main_lang: form.value.main_lang || null,
      add_lang: form.value.add_lang || null,
      special: form.value.special || null,
      role_type: form.value.role_id ?? 1,
    }
    if (form.value.password) payload.password = form.value.password

    if (isEdit.value) {
      await userAPI.updateUser(userId.value, payload)
    } else {
      if (!form.value.password) {
        message.error('Password is required for new accounts')
        return
      }
      await userAPI.createUser(payload)
    }
    message.success(isEdit.value ? 'Account updated successfully!' : 'Account added successfully!')
    router.push('/admin?tab=accounts')
  } catch (err) {
    const detail = err.response?.data?.detail
    message.error(detail || 'Failed to save. Please try again.')
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
  display: flex; align-items: center; gap: 12px;
  padding: 16px 24px;
  background: #f0f4ff;
  border-bottom: 1px solid #e0e7ff;
}
.section-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: #1a73e8; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin: 0; }

/* Avatar row */
.avatar-row {
  display: flex; align-items: center; gap: 20px;
  padding: 20px 24px 0;
}
.avatar-box {
  width: 80px; height: 80px; border-radius: 50%;
  border: 2px solid #e5e7eb;
  overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  background: #f3f4f6; flex-shrink: 0;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder { font-size: 36px; }
.avatar-fields { flex: 1; }

/* Grids */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px 24px;
  padding: 20px 24px 24px;
}
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px 24px;
}
.field-full { grid-column: 1 / -1; }

@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

/* Fields */
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 13px; font-weight: 600; color: #374151; }
.req { color: #e53e3e; }
.field input,
.field select,
.field textarea {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 9px 12px;
  font-size: 14px;
  color: #222;
  outline: none;
  background: #fff;
  width: 100%;
  box-sizing: border-box;
  transition: border 0.2s, box-shadow 0.2s;
  font-family: inherit;
}
.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26,115,232,0.12);
}
.field textarea { resize: vertical; }

/* Password */
.password-wrap {
  position: relative; display: flex; align-items: center;
}
.password-wrap input { padding-right: 42px; }
.toggle-eye {
  position: absolute; right: 10px;
  background: none; border: none; cursor: pointer;
  padding: 0; line-height: 1;
  color: rgba(0,0,0,0.45);
  font-size: 16px;
  display: flex; align-items: center;
  transition: color 0.2s;
}
.toggle-eye:hover { color: rgba(0,0,0,0.85); }

/* Test scores */
.test-scores-wrap { padding: 0 24px 24px; }
.test-scores-title {
  font-size: 13px; font-weight: 700; color: #1a73e8;
  text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 14px; padding-bottom: 6px;
  border-bottom: 2px solid #e0e7ff;
}

/* Footer */
.form-footer {
  display: flex; justify-content: flex-end; gap: 14px;
  padding-top: 8px;
}
.btn-cancel {
  padding: 10px 28px;
  border: 1px solid #d1d5db; border-radius: 7px;
  background: #fff; color: #555; font-size: 14px;
  cursor: pointer; transition: background 0.15s;
}
.btn-cancel:hover { background: #f3f4f6; }
.btn-submit {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 32px;
  border: none; border-radius: 7px;
  background: #1a73e8; color: #fff;
  font-size: 14px; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
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
