<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-left">
        <router-link to="/" class="logo">
          <img src="/assets/logo.png" alt="UniCompare" class="logo-image" />
          <span class="logo-text">UniCompare</span>
        </router-link>

        <div v-if="!props.adminMode" class="nav-menu">
          <router-link to="/universities" class="nav-item">Rankings</router-link>
          <a href="#" class="nav-item">Events</a>
          <router-link to="/scholarships" class="nav-item">Scholarships</router-link>
          <router-link to="/chatbot" class="nav-item">Chat with Chatbot</router-link>
        </div>
      </div>

      <div class="nav-right">
        <button v-if="!props.adminMode" class="btn-counseling">Free Counselling</button>

        <template v-if="!isAuthenticated">
          <router-link to="/login">
            <button class="btn-login">Login</button>
          </router-link>
          <router-link to="/signup">
            <button class="btn-signup">Sign Up</button>
          </router-link>
        </template>

        <template v-else>
          <a-dropdown placement="bottomRight" :trigger="['click']">
            <div class="avatar-wrapper">
              <img :src="userAvatarImg" alt="User Avatar" class="user-avatar" />
            </div>
            <template #overlay>
              <a-menu>
                <a-menu-item v-if="!props.adminMode" key="profile" @click="router.push('/profile')">
                  <span class="menu-link">My Profile</span>
                </a-menu-item>
                <a-menu-item v-if="isAdmin" key="admin" @click="router.push('/admin')">
                  <span class="menu-link">System Management</span>
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout" @click="logout" class="menu-logout">
                  Sign out
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const DEFAULT_AVATAR = '/assets/user-avatar.webp'
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const props = defineProps({
  adminMode: { type: Boolean, default: false }
})

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => authStore.isAdmin)
const userName = computed(() => authStore.user?.first_name || 'Profile')
const userAvatarImg = computed(() => {
  const img = authStore.user?.image
  if (!img) return DEFAULT_AVATAR
  return img.startsWith('http') ? img : API_BASE + img
})

const logout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>

<style scoped>
/* Navigation */
.navbar {
  background: white;
  padding: 16px 50px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 50px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.logo-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.logo-text {
  color: #1f3ab0;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-item {
  text-decoration: none;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s;
}

.nav-item:hover {
  color: #1890ff;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-counseling {
  background: white;
  border: 2px solid #333;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.3s;
}

.btn-counseling:hover {
  background: #f5f5f5;
}

.btn-search {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.search-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  transition: opacity 0.3s;
}

.btn-search:hover .search-icon {
  opacity: 0.7;
}

.btn-login {
  background: white;
  border: none;
  padding: 8px 16px;
  color: #1f3ab0;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.3s;
}

.btn-login:hover {
  opacity: 0.8;
}

.btn-signup {
  background: #1f3ab0;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-signup:hover {
  background: #1a2d8a;
}

/* Avatar */
.avatar-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid #e0e0e0;
  transition: border-color 0.3s;
  flex-shrink: 0;
}

.avatar-wrapper:hover {
  border-color: #1f3ab0;
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.menu-link {
  color: #333;
  text-decoration: none;
  display: block;
}

.menu-logout {
  color: #e53935;
}

@media (max-width: 1024px) {
  .nav-menu {
    display: none;
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 12px 20px;
  }

  .nav-container {
    flex-wrap: wrap;
  }

  .nav-left {
    gap: 20px;
  }

  .nav-right {
    width: 100%;
    justify-content: flex-end;
    margin-top: 10px;
  }

  .btn-counseling {
    display: none;
  }
}
</style>
