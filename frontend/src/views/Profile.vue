<template>
  <div class="profile-layout">
    <Header />

    <div class="profile-main-container">
      <div class="profile-page-wrapper">
        <aside class="profile-sidebar">
          <div class="sidebar-inner">
            <div class="sidebar-header">
              <h3 class="sidebar-title">My Account</h3>
            </div>
            <nav class="sidebar-menu">
              <div 
                class="sidebar-item" 
                :class="{ active: activeTab === 'info' }"
                @click="activeTab = 'info'"
              >
                <user-outlined /> Personal Information
              </div>
              <div 
                class="sidebar-item" 
                :class="{ active: activeTab === 'study' }"
                @click="activeTab = 'study'"
              >
                <book-outlined /> Study Background
              </div>
              <div 
                class="sidebar-item" 
                :class="{ active: activeTab === 'password' }"
                @click="activeTab = 'password'"
              >
                <setting-outlined /> Account Settings
              </div>
            </nav>
          </div>
        </aside>

        <main class="profile-content">
          <div v-if="activeTab === 'info'" class="content-section">
            <h2 class="section-title">Personal Information</h2>
            
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <img v-if="avatarPreview" :src="avatarPreview" class="avatar-img" />
                <a-avatar v-else :size="120" icon="user" class="profile-avatar" />
                <div class="avatar-upload" @click="triggerFileInput">
                  <camera-outlined />
                </div>
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="onAvatarChange"
                />
              </div>
            </div>

            <a-form :model="profileForm" layout="vertical" class="profile-form">
              <!-- Row 1: Last Name | First Name -->
              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="Last Name" required>
                    <a-input v-model:value="profileForm.last_name" placeholder="Last name" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="First Name" required>
                    <a-input v-model:value="profileForm.first_name" placeholder="First name" />
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- Row 2: Country Code | Phone Number -->
              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="Country">
                    <a-select
                      v-model:value="profileForm.country_id"
                      placeholder="Select country"
                      :options="countryOptions"
                      show-search
                      option-filter-prop="label"
                    />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Phone Number">
                    <a-input v-model:value="profileForm.phone_number" placeholder="Phone number" />
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- Row 3: Email (full width) -->
              <a-row :gutter="24">
                <a-col :span="24">
                  <a-form-item label="Email" required>
                    <a-input v-model:value="profileForm.email" disabled />
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- Gender section -->
              <div class="form-section-label">GENDER</div>
              <a-row :gutter="24">
                <a-col :span="24">
                  <a-form-item>
                    <a-radio-group v-model:value="profileForm.gender">
                      <a-radio value="M">Male</a-radio>
                      <a-radio value="F">Female</a-radio>
                    </a-radio-group>
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- Row 4: Date of Birth | Postal Code -->
              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="Date of Birth (dd-mm-yyyy)">
                    <a-date-picker
                      v-model:value="profileForm.dob"
                      format="DD-MM-YYYY"
                      placeholder="dd-mm-yyyy"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Postal Code">
                    <a-input v-model:value="profileForm.postal_code" placeholder="Postal code" />
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- Ethnicity / Language section -->
              <div class="form-section-label">ETHNICITY / LANGUAGE</div>
              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="Ethnicity">
                    <a-input v-model:value="profileForm.ethnicity" placeholder="Ethnicity" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Main Language">
                    <a-input v-model:value="profileForm.main_lang" placeholder="Main language" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="Second Language">
                    <a-input v-model:value="profileForm.second_lang" placeholder="Second language" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Special">
                    <a-checkbox v-model:checked="profileForm.is_special">
                      Special admission status
                    </a-checkbox>
                  </a-form-item>
                </a-col>
              </a-row>

              <div class="form-actions">
                <a-button type="primary" class="btn-save" :loading="savingProfile" @click="saveProfile">Save changes</a-button>
              </div>
            </a-form>
          </div>

          <!-- Study Background Tab -->
          <div v-if="activeTab === 'study'" class="content-section">
            <h2 class="section-title">Study Background</h2>

            <a-form ref="studyFormRef" :model="studyForm" layout="vertical" class="profile-form">
              <!-- PREVIOUS QUALIFICATIONS -->
              <div class="form-section-label">PREVIOUS QUALIFICATION</div>

              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item label="Highest Qualification">
                    <a-select v-model:value="studyForm.highest_level" placeholder="Please Select" style="width:100%">
                      <a-select-option value="HS">High School</a-select-option>
                      <a-select-option value="AS">Associate</a-select-option>
                      <a-select-option value="BA">Bachelor</a-select-option>
                      <a-select-option value="MA">Master</a-select-option>
                      <a-select-option value="PhD">PhD</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Subjects Studied">
                    <a-input v-model:value="studyForm.major" placeholder="e.g. IT, Computer Science" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="24">
                <a-col :span="8">
                  <a-form-item label="Grading">
                    <a-select v-model:value="studyForm.classification" placeholder="Please Select" style="width:100%">
                      <a-select-option value="Excellent">Excellent</a-select-option>
                      <a-select-option value="Good">Good</a-select-option>
                      <a-select-option value="Average">Average</a-select-option>
                      <a-select-option value="Pass">Pass</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="Score" name="gpa" :rules="studyRules.gpa">
                    <a-input-number v-model:value="studyForm.gpa" :min="0" :step="0.1" placeholder="Score" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="Graduation year">
                    <a-select v-model:value="studyForm.graduation_year" placeholder="Please select" style="width:100%">
                      <a-select-option v-for="y in graduationYears" :key="y" :value="y">{{ y }}</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- ACADEMIC TEST SCORES -->
              <div class="form-section-label">ACADEMIC TEST SCORES</div>

              <a-row :gutter="12">
                <a-col :span="4">
                  <a-form-item label="ACT" name="act" :rules="studyRules.act">
                    <a-input-number v-model:value="studyForm.act" :min="1" :max="36" :step="1" :precision="0" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="4">
                  <a-form-item label="GMAT" name="gmat" :rules="studyRules.gmat">
                    <a-input-number v-model:value="studyForm.gmat" :min="200" :max="800" :step="1" :precision="0" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="4">
                  <a-form-item label="SAT" name="sat" :rules="studyRules.sat">
                    <a-input-number v-model:value="studyForm.sat" :min="400" :max="1600" :step="1" :precision="0" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="4">
                  <a-form-item label="CAT" name="cat" :rules="studyRules.cat">
                    <a-input-number v-model:value="studyForm.cat" :min="0" :max="300" :step="1" :precision="0" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="4">
                  <a-form-item label="GRE" name="gre" :rules="studyRules.gre">
                    <a-input-number v-model:value="studyForm.gre" :min="260" :max="340" :step="1" :precision="0" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="4">
                  <a-form-item label="STAT" name="stat" :rules="studyRules.stat">
                    <a-input-number v-model:value="studyForm.stat" :min="0" :max="300" :step="1" :precision="0" style="width:100%" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="24">
                <a-col :span="8">
                  <a-form-item label="International Baccalaureate">
                    <a-input-number v-model:value="studyForm.ib" :min="0" :max="45" :step="0.1" style="width:100%" />
                  </a-form-item>
                </a-col>
              </a-row>

              <!-- ENGLISH TEST SCORES -->
              <div class="form-section-label">ENGLISH TEST SCORES</div>

              <a-row :gutter="12">
                <a-col :span="6">
                  <a-form-item label="IELTS" name="ielts" :rules="studyRules.ielts">
                    <a-input-number v-model:value="studyForm.ielts" :min="0" :max="9" :step="0.5" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="6">
                  <a-form-item label="TOEFL" name="toefl" :rules="studyRules.toefl">
                    <a-input-number v-model:value="studyForm.toefl" :min="0" :max="120" :step="1" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="6">
                  <a-form-item label="Pearson Test" name="pearson" :rules="studyRules.pearson">
                    <a-input-number v-model:value="studyForm.pearson" :min="0" :max="90" :step="1" style="width:100%" />
                  </a-form-item>
                </a-col>
                <a-col :span="6">
                  <a-form-item label="Cambridge Advanced Test" name="cambridge" :rules="studyRules.cambridge">
                    <a-input-number v-model:value="studyForm.cambridge" :min="0" :max="210" :step="1" style="width:100%" />
                  </a-form-item>
                </a-col>
              </a-row>

              <div class="form-actions">
                <a-button type="primary" class="btn-save" :loading="savingStudy" @click="saveStudy">Save changes</a-button>
              </div>
            </a-form>
          </div>

          <!-- Account Settings Tab -->
          <div v-if="activeTab === 'password'" class="content-section">
            <h2 class="section-title">Account Settings</h2>

            <a-form :model="passwordForm" layout="vertical" class="profile-form" @finish="changePassword">
              <div class="form-section-label">CHANGE PASSWORD</div>

              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item name="current_password">
                    <a-input-password
                      v-model:value="passwordForm.current_password"
                      placeholder="Current Password"
                    />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="24">
                <a-col :span="12">
                  <a-form-item name="new_password">
                    <a-input-password
                      v-model:value="passwordForm.new_password"
                      placeholder="New Password"
                    />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item name="confirm_password">
                    <a-input-password
                      v-model:value="passwordForm.confirm_password"
                      placeholder="Confirm New Password"
                    />
                  </a-form-item>
                </a-col>
              </a-row>

              <div class="form-actions" style="text-align: left">
                <a-button type="primary" html-type="submit" class="btn-save" :loading="savingPassword">Change Password</a-button>
              </div>
            </a-form>

            <a-divider class="account-divider" />

            <div class="close-account-section">
              <a-button class="btn-close-account" @click="confirmCloseAccount">Close Your Account</a-button>
            </div>
          </div>
        </main>
      </div>
    </div>

    <!-- Account Closure Modal -->
    <a-modal
      v-model:open="closeAccountModal.visible"
      title="Account Closure"
      :footer="null"
      width="480px"
      @cancel="resetCloseAccountModal"
    >
      <div class="close-modal-body">
        <p class="close-modal-desc">Please confirm your password to close the account.</p>
        <a-input-password
          v-model:value="closeAccountModal.password"
          placeholder="Password"
          class="close-modal-input"
        />
        <p class="close-modal-reason-label">Tell us why you're closing your account:</p>
        <a-radio-group v-model:value="closeAccountModal.reason" class="close-modal-radio-group">
          <a-radio value="duplicate">I have a duplicate account</a-radio>
          <a-radio value="privacy">I have a privacy concern</a-radio>
          <a-radio value="no_value">I am not getting any value from my account</a-radio>
          <a-radio value="others">Others</a-radio>
        </a-radio-group>
        <a-button class="close-modal-btn" block @click="submitCloseAccount">Close Your Account</a-button>
      </div>
    </a-modal>

    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import dayjs from 'dayjs'
import { countryAPI, userAPI, studyBGAPI } from '@/services/api'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { UserOutlined, BookOutlined, SettingOutlined, CameraOutlined } from '@ant-design/icons-vue'

const activeTab = ref('info')
const avatarPreview = ref(null)
const fileInputRef = ref(null)
const studyFormRef = ref(null)
const savingProfile = ref(false)
const savingStudy = ref(false)
const savingPassword = ref(false)

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const onAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    message.error('Please select a valid image file')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    message.error('Image size must be less than 5MB')
    return
  }
  // Show preview immediately
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)

  // Upload to backend
  try {
    const updated = await userAPI.uploadAvatar(file)
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const imageUrl = updated.image?.startsWith('http') ? updated.image : apiBase + updated.image
    avatarPreview.value = imageUrl
    localStorage.setItem('userAvatar', imageUrl)
    message.success('Avatar updated successfully')
  } catch (err) {
    message.error('Failed to upload avatar')
  }
}

const profileForm = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  dob: null,
  gender: null,
  country_id: null,
  postal_code: '',
  ethnicity: '',
  main_lang: '',
  second_lang: '',
  is_special: false
})

const studyForm = reactive({
  highest_level: null,
  major: null,
  classification: null,
  gpa: null,
  graduation_year: null,
  act: null,
  gmat: null,
  sat: null,
  cat: null,
  gre: null,
  stat: null,
  ib: null,
  ielts: null,
  toefl: null,
  pearson: null,
  cambridge: null
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// ── Load profile ──────────────────────────────────────────
const loadProfile = async () => {
  try {
    const user = await userAPI.getProfile()
    profileForm.first_name = user.firstName ?? ''
    profileForm.last_name = user.lastName ?? ''
    profileForm.email = user.email ?? ''
    profileForm.phone_number = user.phoneNumber ?? ''
    // gender: API returns bool (true=M, false=F)
    profileForm.gender = user.gender === true || user.gender === 1
      ? 'M'
      : (user.gender === false || user.gender === 0 ? 'F' : null)
    profileForm.dob = user.dob ? dayjs(user.dob) : null
    profileForm.country_id = user.countryId ?? null
    profileForm.postal_code = ''   // not in UserResponse, kept as editable field
    profileForm.ethnicity = user.ethnicGroup ?? ''
    profileForm.main_lang = user.mainLang ?? ''
    profileForm.second_lang = user.addLang ?? ''
    profileForm.is_special = !!user.special
    if (user.image) avatarPreview.value = user.image
  } catch (err) {
    console.error('Failed to load profile', err)
  }
}

// ── Load study background ─────────────────────────────────
const GRADE_TO_RATE = { Excellent: 4.0, Good: 3.0, Average: 2.0, Pass: 1.0 }
const RATE_TO_GRADE = { 4.0: 'Excellent', 3.0: 'Good', 2.0: 'Average', 1.0: 'Pass' }

const studyRules = {
  gpa:       [{ validator: async (_, v) => { if (v == null) return; if (v < 0 || v > 4) throw new Error('Score (GPA) must be between 0 and 4') }, trigger: 'change' }],
  act:       [{ validator: async (_, v) => { if (v == null) return; if (v < 1 || v > 36) throw new Error('ACT must be between 1 and 36') }, trigger: 'change' }],
  gmat:      [{ validator: async (_, v) => { if (v == null) return; if (v < 200 || v > 800) throw new Error('GMAT must be between 200 and 800') }, trigger: 'change' }],
  sat:       [{ validator: async (_, v) => { if (v == null) return; if (v < 400 || v > 1600) throw new Error('SAT must be between 400 and 1600') }, trigger: 'change' }],
  cat:       [{ validator: async (_, v) => { if (v == null) return; if (v < 0 || v > 300) throw new Error('CAT must be between 0 and 300') }, trigger: 'change' }],
  gre:       [{ validator: async (_, v) => { if (v == null) return; if (v < 260 || v > 340) throw new Error('GRE must be between 260 and 340') }, trigger: 'change' }],
  stat:      [{ validator: async (_, v) => { if (v == null) return; if (v < 0 || v > 300) throw new Error('STAT must be between 0 and 300') }, trigger: 'change' }],
  ielts:     [{ validator: async (_, v) => { if (v == null) return; if (v < 0 || v > 9) throw new Error('IELTS must be between 0 and 9') }, trigger: 'change' }],
  toefl:     [{ validator: async (_, v) => { if (v == null) return; if (v < 0 || v > 120) throw new Error('TOEFL must be between 0 and 120') }, trigger: 'change' }],
  pearson:   [{ validator: async (_, v) => { if (v == null) return; if (v < 10 || v > 90) throw new Error('Pearson Test must be between 10 and 90') }, trigger: 'change' }],
  cambridge: [{ validator: async (_, v) => { if (v == null) return; if (v < 0 || v > 230) throw new Error('Cambridge Advanced Test must be between 0 and 230') }, trigger: 'change' }],
}

const loadStudyBg = async () => {
  try {
    const bg = await studyBGAPI.get()
    studyForm.highest_level = bg.level
    studyForm.major = bg.major
    studyForm.classification = RATE_TO_GRADE[bg.academicRate] ?? bg.academicRate ?? null
    studyForm.gpa = bg.gpa
    studyForm.graduation_year = bg.graduateYear
    studyForm.act = bg.act
    studyForm.gmat = bg.gmat
    studyForm.sat = bg.sat
    studyForm.cat = bg.cat
    studyForm.gre = bg.gre
    studyForm.stat = bg.stat
    studyForm.ib = bg.interBac != null ? parseFloat(bg.interBac) : null
    studyForm.ielts = bg.ielts
    studyForm.toefl = bg.toefl
    studyForm.pearson = bg.pearsonTest
    studyForm.cambridge = bg.camAdvTest
  } catch (err) {
    if (err.response?.status !== 404) {
      console.error('Failed to load study background', err)
    }
  }
}

// ── Save profile ──────────────────────────────────────────
const saveProfile = async () => {
  savingProfile.value = true
  try {
    await userAPI.updateProfile({
      first_name: profileForm.first_name || undefined,
      last_name: profileForm.last_name || undefined,
      phone_number: profileForm.phone_number || undefined,
      country_id: profileForm.country_id ?? undefined,
      gender: profileForm.gender === 'M' ? true : (profileForm.gender === 'F' ? false : undefined),
      dob: profileForm.dob ? dayjs(profileForm.dob).format('YYYY-MM-DD') : undefined,
      postal_code: profileForm.postal_code || undefined,
      ethnic_group: profileForm.ethnicity || undefined,
      main_lang: profileForm.main_lang || undefined,
      add_lang: profileForm.second_lang || undefined,
      special: profileForm.is_special ? '1' : undefined,
    })
    message.success('Profile updated successfully')
  } catch (err) {
    const detail = err.response?.data?.detail || 'Failed to update profile'
    message.error(detail)
  } finally {
    savingProfile.value = false
  }
}

// ── Save study background ─────────────────────────────────
const saveStudy = async () => {
  try {
    await studyFormRef.value.validate()
  } catch {
    message.error('Please fix the validation errors before saving')
    return
  }
  savingStudy.value = true
  try {
    await studyBGAPI.save({
      level: studyForm.highest_level ?? undefined,
      major: studyForm.major ?? undefined,
      academic_rate: studyForm.classification != null ? (GRADE_TO_RATE[studyForm.classification] ?? undefined) : undefined,
      gpa: studyForm.gpa ?? undefined,
      graduate_year: studyForm.graduation_year ?? undefined,
      act: studyForm.act ?? undefined,
      gmat: studyForm.gmat ?? undefined,
      sat: studyForm.sat ?? undefined,
      cat: studyForm.cat ?? undefined,
      gre: studyForm.gre ?? undefined,
      stat: studyForm.stat ?? undefined,
      inter_bac: studyForm.ib != null ? studyForm.ib : undefined,
      ielts: studyForm.ielts ?? undefined,
      toefl: studyForm.toefl ?? undefined,
      pearson_test: studyForm.pearson ?? undefined,
      cam_adv_test: studyForm.cambridge ?? undefined,
    })
    message.success('Study background saved successfully')
  } catch (err) {
    const detail = err.response?.data?.detail || 'Failed to save study background'
    message.error(detail)
  } finally {
    savingStudy.value = false
  }
}

// ── Change password ───────────────────────────────────────
const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    message.error('New passwords do not match')
    return
  }
  if (passwordForm.new_password.length < 6) {
    message.error('Password must be at least 6 characters')
    return
  }
  savingPassword.value = true
  try {
    await userAPI.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    })
    message.success('Password changed successfully')
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (err) {
    const detail = err.response?.data?.detail || 'Failed to change password'
    message.error(detail)
  } finally {
    savingPassword.value = false
  }
}

const closeAccountModal = reactive({
  visible: false,
  password: '',
  reason: null
})

const confirmCloseAccount = () => {
  closeAccountModal.visible = true
}

const resetCloseAccountModal = () => {
  closeAccountModal.password = ''
  closeAccountModal.reason = null
}

const submitCloseAccount = async () => {
  if (!closeAccountModal.password) {
    message.error('Please enter your password')
    return
  }
  if (!closeAccountModal.reason) {
    message.error('Please select a reason')
    return
  }
  try {
    await userAPI.closeAccount({
      password: closeAccountModal.password,
      reason: closeAccountModal.reason,
    })
    message.success('Your account has been closed.')
    // Clear session and redirect to login
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    closeAccountModal.visible = false
    resetCloseAccountModal()
    window.location.href = '/login'
  } catch (err) {
    const detail = err.response?.data?.detail
    message.error(detail || 'Failed to close account')
  }
}

const graduationYears = Array.from({ length: 2030 - 1990 + 1 }, (_, i) => 2030 - i)

const countryOptions = ref([])

const loadCountries = async () => {
  try {
    const response = await countryAPI.getAll()
    countryOptions.value = response.map(c => ({
      label: c.name,
      value: c.id
    }))
  } catch (err) {
    console.error('Failed to load countries', err)
  }
}

onMounted(() => {
  loadProfile()
  loadStudyBg()
  loadCountries()
})</script>

<style scoped>
.profile-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.profile-main-container {
  background-color: #f8f9fa;
  flex: 1;
  padding: 0;
}

.profile-page-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: stretch;
  gap: 0;
  background: white;
  border-radius: 12px 12px 0 0;
  min-height: 80vh;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* Sidebar Styling */
.profile-sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #f0f0f0; /* Đường kẻ dọc chia đôi */
  display: flex;
  flex-direction: column;
}

.sidebar-inner {
  background-color: #E7EFFE;
  padding: 40px 0;
  height: 100%;
}

.sidebar-header {
  padding: 0 24px 20px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
}

.sidebar-item {
  padding: 16px 24px;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s;
  font-size: 15px;
}

.sidebar-item:hover {
  color: #1890ff;
  background: #f0f7ff;
}

.sidebar-item.active {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: 600;
  border-right: 3px solid #1890ff; /* Tạo điểm nhấn bên phải */
}

/* Content Styling */
.profile-content {
  flex: 1;
  padding: 40px;
  background: #f5f7fa;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 30px;
}

.avatar-section {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 35px;
}

.avatar-wrapper {
  position: relative;
}

.avatar-upload {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: #1890ff;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  cursor: pointer;
  transition: background 0.2s;
}

.avatar-upload:hover {
  background: #1062c0;
}

.avatar-img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e0e0e0;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

.btn-save {
  background-color: #1f3ab0;
  height: 45px;
  padding: 0 35px;
  border-radius: 6px;
  font-weight: 600;
}

.account-divider {
  margin: 32px 0;
  border-color: #e0e0e0;
  max-width: 400px;
  min-width: unset;
}

.close-account-section {
  padding-bottom: 8px;
}

.btn-close-account {
  color: #eb2f96;
  border-color: #eb2f96;
  border-radius: 8px;
  height: 44px;
  padding: 0 28px;
  font-weight: 500;
  background: transparent;
}

.btn-close-account:hover {
  color: #fff;
  background: #eb2f96;
  border-color: #eb2f96;
}

.form-section-label {
  font-size: 13px;
  font-weight: 700;
  color: #555;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  margin-top: 8px;
}

/* Account Closure Modal */
.close-modal-body {
  padding: 8px 0 4px;
}

.close-modal-desc {
  font-size: 14px;
  color: #333;
  margin-bottom: 14px;
}

.close-modal-input {
  margin-bottom: 20px;
}

.close-modal-reason-label {
  font-size: 14px;
  color: #333;
  margin-bottom: 12px;
}

.close-modal-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.close-modal-radio-group .ant-radio-wrapper {
  font-size: 14px;
  color: #333;
}

.close-modal-btn {
  border: 1.5px solid #eb2f96;
  color: #eb2f96;
  background: #fff;
  font-weight: 500;
  height: 40px;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-modal-btn:hover {
  background: #eb2f96 !important;
  color: #fff !important;
  border-color: #eb2f96 !important;
}
</style>