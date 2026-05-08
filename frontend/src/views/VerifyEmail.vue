<template>
  <div class="verify-wrapper">
    <!-- Header Component -->
    <Header />

    <!-- Main Content -->
    <div class="verify-container">
      <div class="verify-card">
        <div class="verify-header">
          <h1 class="verify-title">Verify Your Email</h1>
          <p class="verify-subtitle" v-if="userEmail">
            We've sent a verification link to <strong>{{ userEmail }}</strong>
          </p>
          <p class="verify-subtitle" v-else>
            Please check your email for the verification link
          </p>
        </div>

        <!-- Verification Form -->
        <div class="verify-form">
          <!-- Token Input -->
          <div class="form-group">
            <label class="form-label">Verification Token</label>
            <a-input
              v-model:value="token"
              placeholder="Enter verification token from email"
              class="form-input"
              :disabled="loading"
            />
            <p class="form-hint">
              Copy the verification link from your email or paste the token here
            </p>
          </div>

          <!-- Verify Button -->
          <a-button
            type="primary"
            block
            :loading="loading"
            @click="verifyEmail"
            class="verify-btn"
          >
            Verify Email
          </a-button>

          <!-- Error Message -->
          <a-alert
            v-if="error"
            :message="error"
            type="error"
            show-icon
            closable
            @close="error = null"
            class="error-alert"
          />

          <!-- Success Message -->
          <a-alert
            v-if="success"
            :message="success"
            type="success"
            show-icon
            class="success-alert"
          />
        </div>

        <!-- Resend Section -->
        <div class="resend-section">
          <p class="resend-label">Didn't receive the email?</p>
          <button
            type="button"
            class="resend-btn"
            @click="resendVerification"
            :disabled="loading || resendCountdown > 0"
          >
            {{ resendCountdown > 0 ? `Resend in ${resendCountdown}s` : 'Resend verification email' }}
          </button>
        </div>

        <!-- Back to Login -->
        <div class="back-to-login">
          <span>Already verified?</span>
          <router-link to="/login">Back to Login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import { api } from '@/services/api'

const router = useRouter()
const route = useRoute()

const token = ref('')
const userEmail = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const resendCountdown = ref(0)

// Auto-detect token from URL if present
onMounted(() => {
  const urlToken = route.query.token
  if (urlToken) {
    token.value = urlToken
    // Auto-verify if token is in URL
    verifyEmail()
  }

  // Get email from route params if available
  if (route.query.email) {
    userEmail.value = route.query.email
  }
})

const verifyEmail = async () => {
  // Validate token
  if (!token.value.trim()) {
    error.value = 'Please enter or paste the verification token'
    return
  }

  loading.value = true
  error.value = null
  success.value = null

  try {
    const response = await api.post('/auth/verify-email', {
      token: token.value.trim()
    })

    success.value = response.data.message
    message.success('Email verified successfully!')

    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Verification failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const resendVerification = async () => {
  if (!userEmail.value) {
    error.value = 'Please enter your email address'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await api.post('/auth/resend-verification', {
      email: userEmail.value
    })

    message.success(response.data.message)

    // Start countdown
    resendCountdown.value = 60
    const countdownInterval = setInterval(() => {
      resendCountdown.value--
      if (resendCountdown.value <= 0) {
        clearInterval(countdownInterval)
      }
    }, 1000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to resend verification email'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.verify-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #5B8FDE 0%, #4A7FD1 100%);
  display: flex;
  flex-direction: column;
}

.verify-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.verify-card {
  background: white;
  border-radius: 8px;
  padding: 50px 40px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.verify-header {
  text-align: center;
  margin-bottom: 40px;
}

.verify-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.verify-subtitle {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.verify-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-input {
  height: 40px;
  font-size: 14px;
}

:deep(.ant-input) {
  border-radius: 4px;
}

:deep(.ant-input:focus) {
  border-color: #1f3ab0 !important;
  box-shadow: 0 0 0 2px rgba(31, 58, 176, 0.1) !important;
}

.form-hint {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

.verify-btn {
  height: 40px !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  background: #1f3ab0 !important;
}

:deep(.verify-btn:hover) {
  background: #1a2d8a !important;
}

.error-alert {
  margin-top: 20px;
}

.success-alert {
  margin-top: 20px;
}

.resend-section {
  text-align: center;
  padding-top: 30px;
  border-top: 1px solid #eee;
}

.resend-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.resend-btn {
  background: none;
  border: none;
  color: #1f3ab0;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  transition: opacity 0.3s;
}

.resend-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.resend-btn:disabled {
  color: #999;
  cursor: not-allowed;
  text-decoration: none;
}

.back-to-login {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: #666;
}

.back-to-login a {
  color: #1f3ab0;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
}

.back-to-login a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .verify-card {
    padding: 30px 20px;
  }

  .verify-title {
    font-size: 22px;
  }

  .verify-container {
    padding: 20px;
  }
}
</style>
