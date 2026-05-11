<template>
  <div class="admin-wrapper">
    <Header />

    <div class="admin-content">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <button
            :class="['tab-btn', { active: activeTab === 'universities' }]"
            @click="activeTab = 'universities'"
          >
            University List
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'accounts' }]"
            @click="activeTab = 'accounts'"
          >
            Account List
          </button>
        </div>

        <div class="toolbar-center">
          <div class="search-wrap">
            <img src="/assets/search.png" alt="Search" class="search-icon" />
            <input
              v-model="searchQuery"
              class="search-input"
              placeholder="Search"
              @input="handleSearch"
            />
          </div>
        </div>

        <div class="toolbar-right">
          <span class="info-date">Information from: 19/06/2025</span>
          <span class="result-count">{{ activeTab === 'universities' ? filteredList.length : filteredAccounts.length }} results</span>
          <button v-if="activeTab === 'universities'" class="btn-add" @click="openAddModal">
            + Add University
          </button>
          <button v-else class="btn-add" @click="openAddAccountModal">
            + Add Account
          </button>
        </div>
      </div>

      <!-- University List -->
      <div v-if="activeTab === 'universities'" class="list-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <span>Loading...</span>
        </div>
        <div v-else-if="filteredList.length === 0" class="empty-state">
          No universities found.
        </div>
        <div v-else>
          <div v-for="(uni, index) in pagedList" :key="uni.id" class="uni-row">
            <div class="rank-col">{{ uni.rank || index + 1 }}</div>
            <div class="logo-col">
              <img
                v-if="uni.logo"
                :src="uni.logo"
                :alt="uni.name"
                class="uni-logo"
                @error="e => e.target.style.display='none'"
              />
              <div v-else class="logo-placeholder">🎓</div>
            </div>
            <div class="info-col">
              <span class="uni-name">{{ uni.name }}</span>
              <span class="uni-location">{{ uni.city }}, {{ uni.country }}</span>
            </div>
            <div class="actions-col">
              <button class="action-btn" title="View Details" @click="viewUniversity(uni.id)">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
              </button>
              <button class="action-btn" title="Edit" @click="editUniversity(uni)">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                  <path d="M12 20h9"/>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                </svg>
              </button>
              <button class="action-btn danger" title="Delete" @click="confirmDelete(uni)">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                  <path d="M10 11v6M14 11v6"/>
                  <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                </svg>
              </button>
            </div>
          </div>
          <!-- University Pagination -->
          <section class="pagination-section" v-if="filteredList.length > 0">
            <div class="pagination-container">
              <div class="pagination-left">
                <label>Results per page:</label>
                <select v-model.number="uniPageSize" class="per-page-select" @change="uniPage = 1">
                  <option :value="10">10</option>
                  <option :value="30">30</option>
                  <option :value="50">50</option>
                </select>
                <span class="page-info">{{ Math.min((uniPage - 1) * uniPageSize + 1, filteredList.length) }} - {{ Math.min(uniPage * uniPageSize, filteredList.length) }} of {{ filteredList.length }}</span>
              </div>
              <div class="pagination-right">
                <button class="page-btn" :disabled="uniPage === 1" @click="uniPage--">&#8249;</button>
                <button v-for="p in visibleUniPages" :key="p"
                  :class="['page-btn', { active: p === uniPage, dots: p === '...' }]"
                  :disabled="p === '...'" @click="p !== '...' && (uniPage = p)">
                  {{ p }}
                </button>
                <button class="page-btn" :disabled="uniPage === uniTotalPages" @click="uniPage++">&#8250;</button>
              </div>
            </div>
          </section>
        </div>
      </div>

      <!-- Account List -->
      <div v-else class="list-section">
        <div v-if="loadingAccounts" class="loading-state">
          <div class="spinner"></div>
          <span>Loading...</span>
        </div>
        <div v-else-if="filteredAccounts.length === 0" class="empty-state">
          No accounts found.
        </div>
        <div v-else>
          <table class="account-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(acc, i) in pagedAccounts" :key="acc.id">
                <td>{{ (accPage - 1) * accPageSize + i + 1 }}</td>
                <td>{{ acc.first_name }} {{ acc.last_name }}</td>
                <td>{{ acc.email }}</td>
                <td>
                  <span :class="['role-badge', acc.role_type === 2 ? 'role-admin' : 'role-user']">
                    {{ acc.role_type === 2 ? 'Admin' : 'User' }}
                  </span>
                </td>
                <td>
                  <span :class="['status-badge', acc.is_active ? 'status-active' : 'status-inactive']">
                    {{ acc.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <button class="action-btn" title="Edit" @click="editAccount(acc)">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                      <path d="M12 20h9"/>
                      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                    </svg>
                  </button>
                  <button class="action-btn danger" title="Delete" @click="confirmDeleteAccount(acc)">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                      <path d="M10 11v6M14 11v6"/>
                      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <!-- Account Pagination -->
          <section class="pagination-section" v-if="filteredAccounts.length > 0">
            <div class="pagination-container">
              <div class="pagination-left">
                <label>Results per page:</label>
                <select v-model.number="accPageSize" class="per-page-select" @change="accPage = 1">
                  <option :value="10">10</option>
                  <option :value="30">30</option>
                  <option :value="50">50</option>
                </select>
                <span class="page-info">{{ Math.min((accPage - 1) * accPageSize + 1, filteredAccounts.length) }} - {{ Math.min(accPage * accPageSize, filteredAccounts.length) }} of {{ filteredAccounts.length }}</span>
              </div>
              <div class="pagination-right">
                <button class="page-btn" :disabled="accPage === 1" @click="accPage--">&#8249;</button>
                <button v-for="p in visibleAccPages" :key="p"
                  :class="['page-btn', { active: p === accPage, dots: p === '...' }]"
                  :disabled="p === '...'" @click="p !== '...' && (accPage = p)">
                  {{ p }}
                </button>
                <button class="page-btn" :disabled="accPage === accTotalPages" @click="accPage++">&#8250;</button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-box">
        <h3 class="modal-title">Confirm Delete</h3>
        <p class="modal-desc">
          Are you sure you want to delete
          <strong>{{ deleteTarget.name || deleteTarget.email }}</strong>?
          This action cannot be undone.
        </p>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="deleteTarget = null">Cancel</button>
          <button class="modal-btn confirm" @click="executeDelete">Delete</button>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { universityAPI, userAPI } from '@/services/api'
import { message } from 'ant-design-vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()
const route = useRoute()

const activeTab = ref('universities')
const searchQuery = ref('')
const loading = ref(false)
const loadingAccounts = ref(false)
const universities = ref([])
const accounts = ref([])
const deleteTarget = ref(null)
const deleteType = ref('university')

// --- Mock data fallback ---
const MOCK_UNIS = [
  { id: 1, rank: 1, name: 'Massachusetts Institute of Technology (MIT)', city: 'Cambridge', country: 'United States', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/MIT_logo.svg/240px-MIT_logo.svg.png' },
  { id: 2, rank: 2, name: 'Imperial College London', city: 'London', country: 'United Kingdom', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Imperial_logo.svg/240px-Imperial_logo.svg.png' },
  { id: 3, rank: 3, name: 'Stanford University', city: 'Stanford', country: 'United States', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Seal_of_Leland_Stanford_Junior_University.svg/120px-Seal_of_Leland_Stanford_Junior_University.svg.png' },
  { id: 4, rank: 4, name: 'University of Oxford', city: 'Oxford', country: 'United Kingdom', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Oxford-University-Circlet.svg/120px-Oxford-University-Circlet.svg.png' },
  { id: 5, rank: 5, name: 'Harvard University', city: 'Cambridge', country: 'United States', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Harvard_University_logo.svg/240px-Harvard_University_logo.svg.png' },
  { id: 6, rank: 6, name: 'University of Cambridge', city: 'Cambridge', country: 'United Kingdom', logo: null },
  { id: 7, rank: 7, name: 'ETH Zurich', city: 'Zurich', country: 'Switzerland', logo: null },
  { id: 8, rank: 8, name: 'National University of Singapore', city: 'Singapore', country: 'Singapore', logo: null },
  { id: 9, rank: 9, name: 'UCL', city: 'London', country: 'United Kingdom', logo: null },
  { id: 10, rank: 10, name: 'University of Chicago', city: 'Chicago', country: 'United States', logo: null },
]

const MOCK_ACCOUNTS = [
  { id: 1, first_name: 'Alice', last_name: 'Nguyen', email: 'alice@example.com', role_id: 2, is_active: true },
  { id: 2, first_name: 'Bob', last_name: 'Tran', email: 'bob@example.com', role_id: 1, is_active: true },
  { id: 3, first_name: 'Carol', last_name: 'Le', email: 'carol@example.com', role_id: 1, is_active: false },
  { id: 4, first_name: 'David', last_name: 'Pham', email: 'david@example.com', role_id: 1, is_active: true },
]

// --- Computed ---
const filteredList = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return universities.value
  return universities.value.filter(u =>
    u.name?.toLowerCase().includes(q) ||
    u.city?.toLowerCase().includes(q) ||
    u.country?.toLowerCase().includes(q)
  )
})

const filteredAccounts = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return accounts.value
  return accounts.value.filter(a =>
    `${a.first_name} ${a.last_name}`.toLowerCase().includes(q) ||
    a.email?.toLowerCase().includes(q)
  )
})

// --- Pagination ---
const PAGE_SIZE_DEFAULT = 50

const uniPage = ref(1)
const uniPageSize = ref(PAGE_SIZE_DEFAULT)
const accPage = ref(1)
const accPageSize = ref(PAGE_SIZE_DEFAULT)

const uniTotalPages = computed(() => Math.max(1, Math.ceil(filteredList.value.length / uniPageSize.value)))
const accTotalPages = computed(() => Math.max(1, Math.ceil(filteredAccounts.value.length / accPageSize.value)))

const pagedList = computed(() => {
  const start = (uniPage.value - 1) * uniPageSize.value
  return filteredList.value.slice(start, start + uniPageSize.value)
})

const pagedAccounts = computed(() => {
  const start = (accPage.value - 1) * accPageSize.value
  return filteredAccounts.value.slice(start, start + accPageSize.value)
})

function getVisiblePages(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  if (current <= 4) return [1, 2, 3, 4, 5, '...', total]
  if (current >= total - 3) return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
  return [1, '...', current - 1, current, current + 1, '...', total]
}

const visibleUniPages = computed(() => getVisiblePages(uniPage.value, uniTotalPages.value))
const visibleAccPages = computed(() => getVisiblePages(accPage.value, accTotalPages.value))

watch(searchQuery, () => { uniPage.value = 1; accPage.value = 1 })
watch(activeTab,   () => { uniPage.value = 1; accPage.value = 1 })

// --- Fetch ---
const loadUniversities = async () => {
  loading.value = true
  try {
    const res = await universityAPI.getAll({ limit: 2000 })
    universities.value = res.data?.data || res.data || []
  } catch {
    universities.value = MOCK_UNIS
  } finally {
    loading.value = false
  }
}

const loadAccounts = async () => {
  loadingAccounts.value = true
  try {
    const res = await userAPI.getAll()
    accounts.value = Array.isArray(res) ? res : []
  } catch {
    accounts.value = MOCK_ACCOUNTS
  } finally {
    loadingAccounts.value = false
  }
}

// --- Actions ---
const handleSearch = () => {}

const viewUniversity = (id) => router.push(`/university/${id}`)

const editUniversity = (uni) => {
  router.push(`/admin/university/${uni.id}/edit`)
}

const confirmDelete = (uni) => {
  deleteType.value = 'university'
  deleteTarget.value = uni
}

const confirmDeleteAccount = (acc) => {
  deleteType.value = 'account'
  deleteTarget.value = acc
}

const executeDelete = async () => {
  if (!deleteTarget.value) return
  const target = deleteTarget.value
  deleteTarget.value = null
  try {
    if (deleteType.value === 'university') {
      await universityAPI.delete(target.id)
      universities.value = universities.value.filter(u => u.id !== target.id)
      message.success(`"${target.name}" has been removed`)
    } else {
      await userAPI.deleteUser(target.id)
      accounts.value = accounts.value.filter(a => a.id !== target.id)
      message.success(`Account "${target.email}" has been removed`)
    }
  } catch (err) {
    const detail = err.response?.data?.detail
    message.error(detail ? String(detail) : 'Failed to delete. Please try again.')
  }
}

const openAddModal = () => router.push('/admin/university/new')
const openAddAccountModal = () => router.push('/admin/account/new')
const editAccount = (acc) => router.push(`/admin/account/${acc.id}/edit`)

onMounted(() => {
  if (route.query.tab === 'accounts') activeTab.value = 'accounts'
  loadUniversities()
  loadAccounts()
})
</script>

<style scoped>
.admin-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.admin-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 32px 24px 48px;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: 0;
}

.tab-btn {
  padding: 7px 20px;
  border: 1px solid #bdbdbd;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  color: #444;
  transition: background 0.15s, color 0.15s;
}
.tab-btn:first-child { border-radius: 4px 0 0 4px; }
.tab-btn:last-child { border-radius: 0 4px 4px 0; border-left: none; }
.tab-btn.active {
  background: #e0e0e0;
  color: #111;
  font-weight: 600;
}

.toolbar-center { flex: 1; }

.search-wrap {
  display: flex;
  align-items: center;
  border: 1px solid #bdbdbd;
  border-radius: 4px;
  padding: 6px 12px;
  background: #fff;
  max-width: 300px;
}
.search-icon { width: 16px; height: 16px; object-fit: contain; margin-right: 6px; opacity: 0.6; }
.search-input {
  border: none;
  outline: none;
  font-size: 14px;
  width: 100%;
  background: transparent;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.info-date { font-size: 13px; color: #888; white-space: nowrap; }
.result-count { font-size: 16px; font-weight: 700; color: #222; white-space: nowrap; }

.btn-add {
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}
.btn-add:hover { background: #1558b0; }

/* University List */
.list-section {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.uni-row {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 16px 20px;
  margin-bottom: 8px;
  gap: 20px;
  transition: box-shadow 0.15s;
}
.uni-row:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.rank-col {
  width: 48px;
  font-size: 28px;
  font-weight: 700;
  color: #222;
  text-align: center;
  flex-shrink: 0;
}

.logo-col {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.uni-logo {
  max-width: 60px;
  max-height: 60px;
  object-fit: contain;
}
.logo-placeholder { font-size: 32px; }

.info-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.uni-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a73e8;
  cursor: pointer;
}
.uni-name:hover { text-decoration: underline; }
.uni-location { font-size: 13px; color: #666; }

.actions-col {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: color 0.15s, background 0.15s;
}
.action-btn:hover { color: #1a73e8; background: #e8f0fe; }
.action-btn.danger:hover { color: #d32f2f; background: #fce8e8; }

/* Account Table */
.account-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.account-table th {
  background: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e5e7eb;
}
.account-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}
.account-table tbody tr:last-child td { border-bottom: none; }
.account-table tbody tr:hover { background: #f9fafb; }

.role-badge, .status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.role-admin { background: #e8f0fe; color: #1a73e8; }
.role-user  { background: #f3f4f6; color: #555; }
.status-active   { background: #e6f4ea; color: #1e8e3e; }
.status-inactive { background: #fce8e8; color: #d32f2f; }

/* Loading / Empty */
.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  padding: 60px 0;
  color: #888;
}
.spinner {
  width: 24px; height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #1a73e8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state { text-align: center; padding: 60px 0; color: #aaa; font-size: 15px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  border-radius: 10px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.modal-title { font-size: 18px; font-weight: 700; margin: 0 0 12px; color: #222; }
.modal-desc  { font-size: 14px; color: #555; margin: 0 0 24px; line-height: 1.6; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.modal-btn {
  padding: 9px 24px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.modal-btn.cancel  { background: #f3f4f6; color: #444; }
.modal-btn.cancel:hover { background: #e5e7eb; }
.modal-btn.confirm { background: #d32f2f; color: #fff; }
.modal-btn.confirm:hover { background: #b71c1c; }

/* Pagination — same as Universities.vue */
.pagination-section { padding: 20px 0 8px; }
.pagination-container {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 24px; border-radius: 10px; border: 1px solid #e0e7f1;
}
.pagination-left { display: flex; align-items: center; gap: 12px; font-size: 13px; color: #555; }
.per-page-select {
  border: 1px solid #d9d9d9; border-radius: 4px; padding: 4px 8px;
  font-size: 13px; cursor: pointer;
}
.page-info { color: #888; }
.pagination-right { display: flex; align-items: center; gap: 4px; }
.page-btn {
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  border: 1px solid #d9d9d9; border-radius: 4px; background: #fff;
  font-size: 14px; cursor: pointer; color: #333; transition: all 0.2s;
}
.page-btn.active { background: #1f3ab0; color: #fff; border-color: #1f3ab0; }
.page-btn.dots { border: none; cursor: default; }
.page-btn:not(.active):not(.dots):hover { border-color: #1f3ab0; color: #1f3ab0; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
