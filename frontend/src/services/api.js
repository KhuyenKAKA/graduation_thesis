import axios from 'axios'
import { User } from '@/entities/User.js'
import { University } from '@/entities/University.js'
import { Country } from '@/entities/Country.js'
import { StudyBackground } from '@/entities/StudyBackground.js'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 / 403-closed errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    const isLoginRequest = error.config?.url?.includes('/auth/login')

    if (status === 401 && !isLoginRequest) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else if (status === 403 && detail === 'This account has been closed' && !isLoginRequest) {
      // Account was closed while user was logged in — force logout
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  signup(data) {
    return api.post('/auth/signup', data)
  },
  verifySignupCode(data) {
    return api.post('/auth/verify-signup-code', data)
  },
  login(data) {
    return api.post('/auth/login', data)
  },
  refresh(refreshToken) {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },
  logout(refreshToken) {
    return api.post('/auth/logout', { refresh_token: refreshToken })
  },
  forgotPasswordSendCode(email) {
    return api.post('/auth/forgot-password/send-code', { email })
  },
  forgotPasswordReset(data) {
    return api.post('/auth/forgot-password/reset', data)
  }
}

export const userAPI = {
  getAll(limit = 1000) {
    return api.get('/users', { params: { limit } }).then(res => res.data || [])
  },
  getProfile() {
    return api.get('/users/me').then(res => User.fromAPI(res.data))
  },
  updateProfile(data) {
    return api.put('/users/me', data).then(res => User.fromAPI(res.data))
  },
  changePassword(data) {
    return api.put('/users/me/password', data)
  },
  closeAccount(data) {
    return api.post('/users/me/close', data)
  },
  uploadAvatar(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data)
  },
  getUser(userId) {
    return api.get(`/users/${userId}`).then(res => res.data)
  },
  createUser(data) {
    return api.post('/users', data).then(res => res.data)
  },
  updateUser(userId, data) {
    return api.put(`/users/${userId}`, data).then(res => res.data)
  },
  deleteUser(userId) {
    return api.delete(`/users/${userId}`)
  }
}

export const universityAPI = {
  getAll(limit = 50) {
    return api.get('/universities', { params: { limit } })
      .then(res => (res.data || []).map(u => University.fromAPI(u)))
  },
  search(query) {
    return api.get('/universities/search', { params: { q: query } })
      .then(res => (res.data || []).map(u => University.fromAPI(u)))
  },
  filter(filters) {
    // Serialize array params as repeated keys for FastAPI List[str]
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, val]) => {
      if (val === undefined || val === null) return
      if (Array.isArray(val)) {
        val.forEach(v => params.append(key, v))
      } else {
        params.append(key, val)
      }
    })
    return api.get('/universities/filter', { params })
      .then(res => (res.data || []).map(u => University.fromAPI(u)))
  },
  getById(id) {
    return api.get(`/universities/${id}`).then(res => res.data)
  },
  getRankingScores(id) {
    return api.get(`/universities/${id}/ranking-scores`).then(res => res.data)
  },
  getRegions() {
    return api.get('/universities/regions')
  },
  getCountriesByRegion(region_id = null) {
    return api.get('/universities/countries-by-region', { params: region_id ? { region_id } : {} })
  },
  getEntryRequirements(id, degreeType = 1) {
    return api.get(`/universities/${id}/entry-requirements`, { params: { degree_type: degreeType } })
  },
  compare(universityIds) {
    return api.post('/universities/compare', { university_ids: universityIds })
  },
  getChartData(universityIds) {
    return api.post('/universities/chart-data', { university_ids: universityIds })
  },
  create(data) {
    return api.post('/universities', data)
  },
  update(id, data) {
    return api.put(`/universities/${id}`, data)
  },
  delete(id) {
    return api.delete(`/universities/${id}`)
  }
}

export const countryAPI = {
  getAll() {
    return api.get('/countries').then(res => (res.data || []).map(c => Country.fromAPI(c)))
  }
}

export const studyBGAPI = {
  get() {
    return api.get('/study-bg/me').then(res => StudyBackground.fromAPI(res.data))
  },
  getByUserId(userId) {
    return api.get(`/study-bg/${userId}`).then(res => res.data)
  },
  update(data) {
    return api.put('/study-bg/me', data).then(res => StudyBackground.fromAPI(res.data))
  },
  save(data) {
    // POST = upsert (deletes existing and creates new)
    return api.post('/study-bg/me', data).then(res => StudyBackground.fromAPI(res.data))
  }
}

export const chatbotAPI = {
  /**
   * Send a message and receive an AI reply grounded in the database.
   * @param {{ message: string, session_id?: string, user_id?: number }} payload
   */
  chat(payload) {
    return api.post('/chatbot/chat', payload)
  },

  /** List all sessions for the authenticated user. */
  getSessions() {
    return api.get('/chatbot/sessions')
  },

  /** Load full message history for a session. */
  getMessages(sessionId) {
    return api.get(`/chatbot/sessions/${sessionId}/messages`)
  },

  /** Delete a session and all its messages. */
  deleteSession(sessionId) {
    return api.delete(`/chatbot/sessions/${sessionId}`)
  },

  /**
   * Trigger an online search via Tavily + Gemini (non-streaming fallback).
   * For SSE streaming, use native fetch in the component directly.
   * @param {{ message: string, session_id?: string, search_hint?: string }} payload
   */
  searchOnline(payload) {
    return api.post('/chatbot/chat/search-online', payload)
  }
}

export const scholarshipsAPI = {
  getAll(limit = 200) {
    return api.get('/scholarships', { params: { limit } }).then(res => res.data || [])
  }
}

export default api
