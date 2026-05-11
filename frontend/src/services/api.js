import axios from 'axios'
import { User } from '@/entities/User'
import { StudyBackground } from '@/entities/StudyBackground'

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

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if already on login page (let the page handle the error)
      const isLoginRequest = error.config?.url?.includes('/auth/login')
      if (!isLoginRequest) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
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
  getProfile() {
    return api.get('/users/me').then(r => new User(r.data))
  },
  updateProfile(data) {
    return api.put('/users/me', data).then(r => r.data)
  },
  changePassword(data) {
    return api.put('/users/me/password', data).then(r => r.data)
  },
  getAll() {
    return api.get('/users').then(r => r.data)
  },
  getUser(userId) {
    return api.get(`/users/${userId}`).then(r => r.data)
  },
  createUser(payload) {
    return api.post('/users', payload).then(r => r.data)
  },
  updateUser(userId, payload) {
    return api.put(`/users/${userId}`, payload).then(r => r.data)
  },
  deleteUser(userId) {
    return api.delete(`/users/${userId}`).then(r => r.data)
  },
  uploadAvatar(file) {
    const form = new FormData()
    form.append('file', file)
    return api.post('/users/me/avatar', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
  },
  closeAccount(data) {
    return api.post('/users/me/close', data).then(r => r.data)
  }
}

export const universityAPI = {
  getAll({ page = 1, limit = 20 } = {}) {
    return api.get('/universities', { params: { page, limit } })
  },
  search(query, { page = 1, limit = 20 } = {}) {
    return api.get('/universities/search', { params: { q: query, page, limit } })
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
  },
  getById(id) {
    return api.get(`/universities/${id}`).then(r => r.data)
  },
  getRankingScores(id) {
    return api.get(`/universities/${id}/ranking-scores`).then(r => r.data)
  },
  getRegions() {
    return api.get('/universities/regions')
  },
  getCountriesByRegion(region = null) {
    return api.get('/universities/countries-by-region', { params: region ? { region } : {} })
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
  create(payload) {
    return api.post('/universities', payload).then(r => r.data)
  },
  update(id, payload) {
    return api.put(`/universities/${id}`, payload).then(r => r.data)
  },
  delete(id) {
    return api.delete(`/universities/${id}`).then(r => r.data)
  }
}

export const countryAPI = {
  getAll() {
    return api.get('/countries').then(r => r.data)
  }
}

export const studyBGAPI = {
  get() {
    return api.get('/study-bg/me').then(r => new StudyBackground(r.data))
  },
  save(data) {
    return api.post('/study-bg/me', data).then(r => r.data)
  },
  update(data) {
    return api.put('/study-bg/me', data).then(r => r.data)
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

  /** List all sessions for a user. */
  getSessions(userId) {
    return api.get('/chatbot/sessions', { params: { user_id: userId } })
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
    return api.get('/scholarships', { params: { limit } }).then(r => r.data)
  }
}

export default api
