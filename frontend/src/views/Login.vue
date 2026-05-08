<template>
  <div class="login-wrapper">
    <!-- Header Component -->
    <Header />

    <!-- Main Content -->
    <div class="main-container">
      <!-- Left Panel -->
      <div class="left-panel">
        <div class="left-content">
          <h1 class="title">Time to take control of your future</h1>
          <ul class="benefits">
            <li>Get personalised guidance for your university search</li>
            <li>Be the first to know when new rankings launch</li>
            <li>Gain exclusive access to all our tools and resources to find your perfect course</li>
          </ul>
          <img src="/assets/signup.avif" alt="Student signup" class="signup-image" />
        </div>
      </div>

      <!-- Right Panel - Sign In Form -->
      <div class="right-panel">
        <div class="login-content">
          <!-- Sign In Title -->
          <h1 class="login-title">Sign in</h1>
          <p class="login-subtitle">Enter your email and password to sign in or create an account. Don't worry if it's wrong.</p>

          <!-- Form -->
          <a-form
            ref="formRef"
            :model="formData"
            layout="vertical"
            @finish="handleLogin"
            :loading="loading"
          >
            <!-- Email -->
            <a-form-item
              label="Email"
              name="email"
              :rules="[
                { required: true, message: 'Please enter email' },
                { type: 'email', message: 'Please enter valid email' }
              ]"
            >
              <a-input
                v-model:value="formData.email"
                placeholder="Email"
                class="form-input"
              />
            </a-form-item>

            <!-- Password -->
            <a-form-item
              label="Password"
              name="password"
              :rules="[
                { required: true, message: 'Please enter password' }
              ]"
            >
              <a-input-password
                v-model:value="formData.password"
                placeholder="Password"
                class="form-input"
              />
              <div class="forgot-password">
                <a href="#" @click.prevent="handleForgotPassword">Forgot password?</a>
              </div>
            </a-form-item>

            <!-- Email Not Verified Modal -->
            <a-modal
              v-model:open="showVerifyModal"
              title="Email Not Verified"
              :footer="null"
              centered
            >
              <div class="verify-modal-content">
                <p>Your email address has not been verified yet.</p>
                <p>Please check your inbox and verify your email before signing in.</p>
                <div class="verify-modal-actions">
                  <router-link
                    :to="{ name: 'VerifyEmail', query: { email: formData.email } }"
                  >
                    <a-button type="primary" block @click="showVerifyModal = false">
                      Go to Email Verification
                    </a-button>
                  </router-link>
                </div>
              </div>
            </a-modal>

            <!-- Forgot Password Modal -->
            <a-modal
              v-model:open="showForgotModal"
              title="Reset Password"
              :footer="null"
              centered
              :width="440"
              @cancel="resetForgotForm"
            >
              <div class="forgot-modal-content">
                <a-form layout="vertical" :model="forgotData" @finish="handleResetPassword">
                  <!-- Email -->
                  <a-form-item label="Email" name="email" :rules="[{ required: true, type: 'email', message: 'Please enter a valid email' }]">
                    <div class="send-code-row">
                      <a-input
                        v-model:value="forgotData.email"
                        placeholder="Enter your registered email"
                        class="form-input"
                        style="flex: 1"
                      />
                      <a-button
                        :loading="sendingCode"
                        :disabled="codeSent && codeCountdown > 0"
                        class="btn-send-code"
                        @click="handleSendForgotCode"
                      >
                        {{ codeSent && codeCountdown > 0 ? `Resend (${codeCountdown}s)` : 'Send Code' }}
                      </a-button>
                    </div>
                  </a-form-item>

                  <!-- New Password -->
                  <a-form-item label="New Password" name="new_password" :rules="[{ required: true, min: 6, message: 'At least 6 characters' }]">
                    <a-input-password
                      v-model:value="forgotData.new_password"
                      placeholder="Enter new password"
                      class="form-input"
                    />
                  </a-form-item>

                  <!-- Confirm Password -->
                  <a-form-item label="Confirm Password" name="confirm_password" :rules="[{ required: true, message: 'Please confirm your password' }]">
                    <a-input-password
                      v-model:value="forgotData.confirm_password"
                      placeholder="Re-enter new password"
                      class="form-input"
                    />
                  </a-form-item>

                  <!-- Verification Code -->
                  <a-form-item label="Verification Code" name="code" :rules="[{ required: true, message: 'Enter the 6-digit code' }]">
                    <a-input
                      v-model:value="forgotData.code"
                      placeholder="Enter 6-digit code from email"
                      class="form-input"
                      maxlength="6"
                    />
                  </a-form-item>

                  <a-button
                    type="primary"
                    block
                    :loading="resettingPassword"
                    class="submit-btn"
                    style="margin-top: 4px"
                    @click="handleResetPassword"
                  >
                    Confirm Reset Password
                  </a-button>
                </a-form>
              </div>
            </a-modal>

            <!-- Submit Button -->
            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                block
                :loading="loading"
                class="submit-btn"
              >
                Sign in
              </a-button>
            </a-form-item>

            <!-- Divider -->
            <div class="divider">
              <span>OR</span>
            </div>

            <!-- Sign Up Link -->
            <div class="signup-link">
              <span>Don't have an account?</span>
              <router-link to="/signup">Sign up</router-link>
            </div>
          </a-form>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'
import { authAPI } from '@/services/api'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const showVerifyModal = ref(false)

// Forgot password state
const showForgotModal = ref(false)
const sendingCode = ref(false)
const resettingPassword = ref(false)
const codeSent = ref(false)
const codeCountdown = ref(0)
let countdownTimer = null

const forgotData = ref({
  email: '',
  new_password: '',
  confirm_password: '',
  code: ''
})

const resetForgotForm = () => {
  forgotData.value = { email: '', new_password: '', confirm_password: '', code: '' }
  codeSent.value = false
  codeCountdown.value = 0
  if (countdownTimer) clearInterval(countdownTimer)
}

const startCountdown = () => {
  codeCountdown.value = 60
  codeSent.value = true
  countdownTimer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) clearInterval(countdownTimer)
  }, 1000)
}

const handleSendForgotCode = async () => {
  if (!forgotData.value.email) {
    message.warning('Please enter your email first.')
    return
  }
  sendingCode.value = true
  try {
    await authAPI.forgotPasswordSendCode(forgotData.value.email)
    message.success('Verification code sent! Please check your email.')
    startCountdown()
  } catch (err) {
    const detail = err.response?.data?.detail
    const msg = Array.isArray(detail)
      ? detail.map(e => e.msg || JSON.stringify(e)).join('; ')
      : (detail || 'Failed to send code')
    message.error(msg)
  } finally {
    sendingCode.value = false
  }
}

const handleResetPassword = async () => {
  if (forgotData.value.new_password !== forgotData.value.confirm_password) {
    message.error('Passwords do not match.')
    return
  }
  resettingPassword.value = true
  try {
    await authAPI.forgotPasswordReset({
      email: forgotData.value.email,
      code: forgotData.value.code,
      new_password: forgotData.value.new_password,
      confirm_password: forgotData.value.confirm_password
    })
    message.success('Password reset successfully! Please sign in with your new password.')
    showForgotModal.value = false
    resetForgotForm()
  } catch (err) {
    console.error('Reset password error:', err.response?.status, err.response?.data)
    const detail = err.response?.data?.detail
    const msg = Array.isArray(detail)
      ? detail.map(e => e.msg || JSON.stringify(e)).join('; ')
      : (detail || 'Failed to reset password')
    message.error(msg)
  } finally {
    resettingPassword.value = false
  }
}

const handleLogin = async () => {
  loading.value = true

  try {
    await authStore.login(formData.value.email, formData.value.password)
    message.success('Login successful!')
    router.push(authStore.isAdmin ? '/admin' : '/')
  } catch (err) {
    const detail = err.response?.data?.detail || 'Login failed'
    const status = err.response?.status

    if (status === 403 && detail === 'This account has been closed') {
      message.error('This account has been closed. Please contact support or sign up again.')
    } else if (status === 403) {
      showVerifyModal.value = true
    } else if (status === 401) {
      message.error('Incorrect email or password. Please try again.')
    } else {
      message.error(detail)
    }
  } finally {
    loading.value = false
  }
}

const handleForgotPassword = () => {
  showForgotModal.value = true
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Main Container */
.main-container {
  display: grid;
  grid-template-columns: 0.9fr 1fr;
  min-height: calc(100vh - 64px);
  max-width: 1000px;
  margin: 0 auto 60px auto;
  background-color: #f5f5f5;
}

/* Left Panel */
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
  padding: 0;
  margin: 0 0 40px 0;
}

.benefits li {
  font-size: 13px;
  margin-bottom: 14px;
  line-height: 1.5;
  padding-left: 0;
  color: #2d5aa8;
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
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.login-content {
  max-width: 380px;
  width: 100%;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

/* Form Styling */
:deep(.ant-form-item-label > label) {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 14px;
}

.form-input {
  min-height: 48px;
  border-radius: 4px;
  font-size: 15px;
}

:deep(.ant-input-password) {
  /* Đảm bảo khung bao ngoài ôm khít input bên trong */
  padding: 0 11px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  border: 1px solid #d9d9d9;
}

:deep(.ant-input-password .ant-input) {
  height: 46px;
  font-size: 15px;
  /* Xóa border và shadow của input bên trong để không tạo vạch trắng */
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.forgot-password {
  text-align: right;
  margin-top: 8px;
}

.forgot-password a {
  color: #1890ff;
  font-size: 14px;
  text-decoration: underline;
  transition: opacity 0.3s;
}

.forgot-password a:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.submit-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 4px;
  background-color: #3850d4;
  border-color: #3850d4;
  margin-top: 8px;
}

.submit-btn:hover {
  background-color: #2d3fb8;
  border-color: #2d3fb8;
}

/* Divider */
.divider {
  text-align: center;
  margin: 24px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 45%;
  height: 1px;
  background-color: #e0e0e0;
}

.divider::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  width: 45%;
  height: 1px;
  background-color: #e0e0e0;
}

.divider span {
  color: #999;
  font-size: 13px;
  background-color: white;
  padding: 0 10px;
}

/* Sign Up Link */
.signup-link {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.signup-link span {
  margin-right: 6px;
}

.signup-link a {
  color: #1890ff;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.3s;
}

.signup-link a:hover {
  opacity: 0.8;
  text-decoration: underline;
}

/* Verification Help */
.verification-help {
  margin-top: 12px;
  padding: 12px;
  background-color: #e6f7ff;
  border-radius: 4px;
  border-left: 4px solid #1890ff;
}

.verification-help p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #0050b3;
  font-weight: 500;
}

.verify-link {
  color: #0050b3;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.3s;
}

.verify-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.verify-modal-content {
  padding: 8px 0 16px;
}

.verify-modal-content p {
  font-size: 14px;
  color: #555;
  margin-bottom: 10px;
  line-height: 1.6;
}

.verify-modal-actions {
  margin-top: 20px;
}

/* Forgot Password Modal */
.forgot-modal-content {
  padding: 8px 0 8px;
}

.send-code-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-send-code {
  white-space: nowrap;
  background: #1f3ab0;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  height: 48px;
  padding: 0 14px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-send-code:hover:not(:disabled) {
  background: #1a2d8a;
}

.btn-send-code:disabled {
  background: #aaa;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 992px) {
  .main-container {
    grid-template-columns: 1fr;
    max-width: 100%;
  }

  .left-panel {
    display: none;
  }

  .right-panel {
    padding: 40px 30px;
  }

  .login-content {
    max-width: 100%;
  }
}

@media (max-width: 576px) {
  .right-panel {
    padding: 30px 20px;
  }

  .login-title {
    font-size: 24px;
  }
}

/* Đảm bảo vùng chứa input không có background đè lên */
:deep(.ant-form-item-control-input-content) {
  position: relative;
  z-index: 2;
}

/* Xử lý icon con mắt để không bị lệch */
:deep(.ant-input-password-icon) {
  color: rgba(0, 0, 0, 0.45);
  cursor: pointer;
  transition: all 0.3s;
}
</style>
