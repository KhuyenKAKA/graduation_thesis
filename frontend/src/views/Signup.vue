<template>
  <div class="signup-wrapper">
    <!-- Header Component -->
    <Header />

    <!-- Main Content -->
    <div class="main-container">
      <!-- Left Panel -->
      <div class="left-panel">
        <div class="left-content">
          <h1 class="title">Time to take charge of your future</h1>
          <ul class="benefits">
            <li>Get personalised guidance for your university search</li>
            <li>Be the first to know when new rankings launch</li>
            <li>Gain exclusive access to all our tools and resources to find your perfect course</li>
          </ul>
          <img src="/assets/signup.avif" alt="Student signup" class="signup-image" />
        </div>
      </div>

      <!-- Right Panel - Sign Up Form -->
      <div class="right-panel">
        <div class="signup-content">

          <!-- Sign Up Title -->
          <h1 class="signup-title">Sign up</h1>

          <!-- Form -->
          <a-form
            ref="formRef"
            :model="formData"
            layout="vertical"
            @finish="handleSignup"
            :loading="loading"
          >
            <!-- First Name -->
            <a-form-item
              label="What's your first name?"
              name="first_name"
              :rules="[{ required: true, message: 'Please enter first name' }]"
            >
              <a-input
                v-model:value="formData.first_name"
                placeholder=" First name"
                class="form-input"
              />
            </a-form-item>

            <!-- Last Name -->
            <a-form-item
              label="What's your last name?"
              name="last_name"
              :rules="[{ required: true, message: 'Please enter last name' }]"
            >
              <a-input
                v-model:value="formData.last_name"
                placeholder=" Last name"
                class="form-input"
              />
            </a-form-item>

            <!-- Email -->
            <a-form-item
              label="What's your email?"
              name="email"
              :rules="[
                { required: true, message: 'Please enter email' },
                { type: 'email', message: 'Please enter valid email' }
              ]"
            >
              <a-input
                v-model:value="formData.email"
                placeholder=" Email"
                class="form-input"
              />
            </a-form-item>

            <!-- Password -->
            <a-form-item
              label="Choose a password?"
              name="password"
              :rules="[
                { required: true, message: 'Please enter password' },
                { min: 6, message: 'Password must be at least 6 characters' }
              ]"
            >
              <a-input-password
                v-model:value="formData.password"
                placeholder=" Password"
                class="form-input"
              />
            </a-form-item>
            <!-- Confirm Password -->
            <a-form-item
              label="Confirm your password"
              name="confirm_password"
              :rules="[
                { required: true, message: 'Please confirm your password' },
                { validator: validateConfirmPassword, trigger: 'change' }
              ]"
            >
              <a-input-password
                v-model:value="formData.confirm_password"
                placeholder="Confirm Password"
                class="form-input"
              />
            </a-form-item>
            <!-- Checkboxes -->
            <a-form-item
              name="marketing_consent"
              :rules="[{ required: true, message: 'Please check this box' }]"
            >
              <a-checkbox v-model:checked="formData.marketing_consent">
                I am happy to receive useful information and resources from UC that are related to my study preferences 
              </a-checkbox>
            </a-form-item>
            <!-- Error Message -->
            <a-form-item v-if="error">
              <a-alert
                :message="error"
                type="error"
                show-icon
                closable
                @close="error = null"
              />
            </a-form-item>

            <!-- Submit Button -->
            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                block
                :loading="loading"
                class="submit-btn"
              >
                Continue to Sign Up
              </a-button>
            </a-form-item>

            <!-- Sign In Link -->
            <div class="signin-link">
              <span>Already have an account?</span>
              <router-link to="/login">Sign in</router-link>
            </div>
          </a-form>
        </div>
      </div>
    </div>

    <!-- Verification Code Modal -->
    <a-modal
      v-model:visible="showVerificationModal"
      title="Verify Account"
      :closable="!loading"
      :mask-closable="false"
      :footer="null"
      centered
      class="verification-modal"
    >
      <div class="modal-content">
        <p class="modal-subtitle">
          We sent a 6-digit verification code to <strong>{{ formData.email }}</strong>
        </p>

        <!-- Code Input -->
        <div class="code-input-group">
          <label class="code-label">Verification Code</label>
          <input
            v-model="verificationCode"
            type="text"
            placeholder="Enter 6 digits"
            class="code-input"
            maxlength="6"
            :disabled="loading"
            @keyup.enter="confirmVerificationCode"
          />
          <p class="code-hint">Please check your email (including spam folder)</p>
        </div>

        <!-- Error Message -->
        <a-alert
          v-if="verificationError"
          :message="verificationError"
          type="error"
          show-icon
          closable
          @close="verificationError = null"
          class="verification-error"
        />

        <!-- Submit Button -->
        <a-button
          type="primary"
          block
          :loading="loading"
          @click="confirmVerificationCode"
          class="verify-btn"
        >
          Confirm
        </a-button>

        <!-- Back Button -->
        <a-button
          block
          @click="cancelVerification"
          :disabled="loading"
          class="back-btn"
        >
          Go Back
        </a-button>
      </div>
    </a-modal>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()

const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
  marketing_consent: false,
})

const loading = ref(false)
const error = ref(null)

const validateConfirmPassword = async (_rule, value) => {
  if (!value) {
    return Promise.reject('Please confirm your password')
  }
  if (value !== formData.value.password) {
    return Promise.reject('Passwords do not match')
  }
  return Promise.resolve()
}

// Modal states
const showVerificationModal = ref(false)
const verificationCode = ref('')
const verificationError = ref(null)

const handleSignup = async () => {
  if (!formData.value.marketing_consent) {
    error.value = 'Please check the consent box to continue'
    return
  }
  if (formData.value.password !== formData.value.confirm_password) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  error.value = null

  try {
    await authStore.signup({
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      email: formData.value.email,
      password: formData.value.password
    })
    // Show verification modal instead of redirecting
    showVerificationModal.value = true
    verificationCode.value = ''
    verificationError.value = null
  } catch (err) {
    error.value = err.response?.data?.detail || 'Signup failed'
  } finally {
    loading.value = false
  }
}

const confirmVerificationCode = async () => {
  if (!verificationCode.value || verificationCode.value.length !== 6) {
    verificationError.value = 'Please enter a valid 6-digit code'
    return
  }

  loading.value = true
  verificationError.value = null

  try {
    const response = await authStore.verifySignupCode(
      formData.value.email,
      verificationCode.value
    )
    message.success(response.message)
    // Redirect to login after successful verification
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    verificationError.value = err.response?.data?.detail || 'Verification failed'
  } finally {
    loading.value = false
  }
}

const cancelVerification = () => {
  showVerificationModal.value = false
  verificationCode.value = ''
  verificationError.value = null
  // Reset form
  formData.value.first_name = ''
  formData.value.last_name = ''
  formData.value.email = ''
  formData.value.password = ''
  formData.value.confirm_password = ''
  formData.value.marketing_consent = false
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.signup-wrapper {
  min-height: 100vh;
  background: #f5f5f5;
}

/* Main Container */
.main-container {
  display: grid;
  grid-template-columns: 0.9fr 1fr;
  min-height: calc(100vh - 50px);
  max-width: 1000px;
  margin: 0 auto 60px auto;
}

.left-panel {
  background: linear-gradient(135deg, #5B8FDE 0%, #4A7FD1 100%);
  padding: 50px 35px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.left-content {
  color: #1a3a6b;
  max-width: 280px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 25px;
  line-height: 1.3;
  color: #1a3a6b;
}

.benefits {
  list-style: none;
  margin-bottom: 40px;
}

.benefits li {
  font-size: 13px;
  margin-bottom: 14px;
  line-height: 1.5;
  padding-left: 0;
  color: #2d5aa8;
}

.illustration-placeholder {
  font-size: 80px;
  text-align: center;
  margin-top: 40px;
  opacity: 0.9;
}

.signup-image {
  width: 100%;
  max-width: 300px;
  margin-top: 25px;
  margin-left: auto;
  margin-right: auto;
  display: block;
  border-radius: 8px;
}

/* Right Panel */
.right-panel {
  background: white;
  padding: 35px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  overflow-y: auto;
}

.signup-content {
  max-width: 380px;
  width: 100%;
}

/* Social Buttons */
.social-btn {
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 12px;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.social-btn:hover {
  border-color: #999;
  background: #f9f9f9;
}

.google-icon {
  font-weight: bold;
  color: #ea4335;
}

.facebook-icon {
  color: #1877f2;
  font-weight: bold;
}

/* Agreement Text */
.agreement-text {
  font-size: 12px;
  color: #666;
  text-align: center;
  margin: 20px 0;
  line-height: 1.5;
}

.agreement-text a {
  color: #1e90ff;
  text-decoration: none;
}

.agreement-text a:hover {
  text-decoration: underline;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  gap: 16px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #ddd;
}

.divider span {
  color: #999;
  font-size: 12px;
  font-weight: 600;
}

/* Sign Up Title */
.signup-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #1a1a1a;
}

/* Form */
:deep(.ant-form) {
  width: 100%;
}

:deep(.ant-form-item) {
  margin-bottom: 16px;
}

:deep(.ant-form-item-label) {
  padding-bottom: 6px;
}

:deep(.ant-form-item-label > label) {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.form-input {
  height: 48px !important;
  border: 1px solid #ddd !important;
  font-size: 14px;
  padding: 0 11px !important;
}

:deep(.ant-input) {
  height: 48px;
  padding: 0 11px;
  font-size: 14px;
  border-radius: 4px !important;
}

:deep(.ant-input-password) {
  padding: 0 11px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  border: 1px solid #d9d9d9;
  height: 48px;
}

:deep(.ant-input-password .ant-input) {
  height: 46px;
  font-size: 14px;
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 0 !important;
}

:deep(.ant-input:hover),
:deep(.ant-input-password input:hover) {
  border-color: #b3b3b3 !important;
}

:deep(.ant-input:focus),
:deep(.ant-input-password input:focus) {
  border-color: #1e90ff !important;
  box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.1) !important;
}

:deep(.ant-input-password-icon) {
  right: 12px !important;
}

/* Age Check */
.age-check {
  margin-bottom: 20px;
}

.age-check label {
  display: block;
  font-size: 13px;
  color: #666;
  font-weight: 500;
  margin-bottom: 10px;
}

.age-buttons {
  display: flex;
  gap: 12px;
}

.age-btn {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.age-btn:hover {
  border-color: #999;
}

.age-btn.active {
  background: #1e90ff;
  color: white;
  border-color: #1e90ff;
}

/* Checkboxes */
:deep(.ant-checkbox) {
  font-size: 13px;
}

:deep(.ant-checkbox-wrapper) {
  color: #666;
  line-height: 1.5;
}

:deep(.ant-checkbox-inner) {
  border-color: #ddd;
}

:deep(.ant-checkbox:hover .ant-checkbox-inner) {
  border-color: #1e90ff;
}

:deep(.ant-checkbox-checked .ant-checkbox-inner) {
  background-color: #1e90ff;
  border-color: #1e90ff;
}

/* Buttons */
.submit-btn {
  height: 40px !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  background: #2d5aa8 !important;
}

:deep(.submit-btn) {
  background: #2d5aa8 !important;
}

:deep(.submit-btn:hover) {
  background: #1e3f6e !important;
}

/* Sign In Link */
.signin-link {
  text-align: center;
  font-size: 13px;
  color: #666;
  margin-top: 16px;
}

.signin-link a {
  color: #1e90ff;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 600;
}

.signin-link a:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 1024px) {
  .main-container {
    grid-template-columns: 1fr;
  }

  .left-panel {
    display: none;
  }

  .right-panel {
    padding: 40px 30px;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 12px 20px;
  }

  .nav-menu {
    display: none;
  }

  .header-right {
    gap: 10px;
  }

  .right-panel {
    padding: 30px 20px;
  }

  .signup-content {
    max-width: 100%;
  }
}

/* Verification Modal Styles */
:deep(.verification-modal .ant-modal-content) {
  padding: 30px;
}

:deep(.verification-modal .ant-modal-header) {
  border-bottom: none;
  padding: 0 0 20px 0;
}

:deep(.verification-modal .ant-modal-title) {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.modal-content {
  width: 100%;
}

.modal-subtitle {
  font-size: 13px;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.code-input-group {
  margin-bottom: 20px;
}

.code-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.code-input {
  width: 100%;
  height: 50px;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 12px;
  text-align: center;
  border: 2px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  font-family: monospace;
  transition: border-color 0.3s;
}

.code-input:focus {
  outline: none;
  border-color: #1f3ab0;
  box-shadow: 0 0 0 2px rgba(31, 58, 176, 0.1);
}

.code-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.code-hint {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

.verification-error {
  margin-bottom: 16px;
}

.verify-btn {
  height: 40px !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  background: #1f3ab0 !important;
  margin-bottom: 12px;
}

:deep(.verify-btn:hover) {
  background: #1a2d8a !important;
}

.back-btn {
  height: 40px !important;
  font-size: 14px !important;
  color: #666 !important;
}
</style>
