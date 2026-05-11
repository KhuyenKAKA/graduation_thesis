import { defineStore } from 'pinia'
import { ref, computed, markRaw } from 'vue'
import { authAPI, userAPI } from '@/services/api'
import { User } from '@/entities/User.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.isAdmin ?? false)

  const signup = async (data) => {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.signup(data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Signup failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const login = async (email, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.login({ email, password })
      accessToken.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      user.value = response.data.user ? markRaw(User.fromAPI(response.data.user)) : null

      localStorage.setItem('access_token', accessToken.value)
      localStorage.setItem('refresh_token', refreshToken.value)

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      if (refreshToken.value) {
        await authAPI.logout(refreshToken.value)
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      loading.value = false
    }
  }

  const setUser = (userData) => {
    user.value = userData instanceof User
      ? markRaw(userData)
      : (userData ? markRaw(User.fromAPI(userData)) : null)
  }

  const verifySignupCode = async (email, code) => {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.verifySignupCode({ email, code })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Verification failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const initUser = async () => {
    if (!accessToken.value || user.value) return
    try {
      const profile = await userAPI.getProfile()
      user.value = markRaw(profile)
    } catch {
      // token expired or invalid — leave as null, interceptor will handle redirect
    }
  }

  const updateAvatar = (imageUrl) => {
    if (!user.value) return
    const updated = new User({
      ...user.value.toPlainObject?.() ?? {},
      id: user.value.id,
      first_name: user.value.firstName,
      last_name: user.value.lastName,
      email: user.value.email,
      image: imageUrl,
      phone_number: user.value.phoneNumber,
      gender: user.value.gender,
      dob: user.value.dob,
      country_id: user.value.countryId,
      main_lang: user.value.mainLang,
      add_lang: user.value.addLang,
      ethnic_group: user.value.ethnicGroup,
      special: user.value.special,
      role_type: user.value.roleType,
    })
    user.value = markRaw(updated)
  }

  return {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    signup,
    verifySignupCode,
    login,
    logout,
    setUser,
    updateAvatar,
    initUser
  }
})
