import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/universities',
    name: 'Universities',
    component: () => import('@/views/Universities.vue')
  },
  {
    path: '/comparison',
    name: 'Comparison',
    component: () => import('@/views/Comparison.vue')
  },
  {
    path: '/scholarships',
    name: 'Scholarships',
    component: () => import('@/views/Scholarships.vue')
  },
  {
    path: '/chatbot',
    name: 'Chatbot',
    component: () => import('@/views/Chatbot.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('@/views/Signup.vue')
  },
  {
    path: '/university/:id',
    name: 'UniversityDetail',
    component: () => import('@/views/UniversityDetail.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminManagement',
    component: () => import('@/views/AdminManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/university/new',
    name: 'UniversityFormNew',
    component: () => import('@/views/UniversityForm.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/university/:id/edit',
    name: 'UniversityFormEdit',
    component: () => import('@/views/UniversityForm.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/account/new',
    name: 'AccountFormNew',
    component: () => import('@/views/AccountForm.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/account/:id/edit',
    name: 'AccountFormEdit',
    component: () => import('@/views/AccountForm.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/Home.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Authentication guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiresAdmin && !authStore.isAdmin) {
    next('/')
  } else if ((to.path === '/login' || to.path === '/signup') && authStore.isAuthenticated) {
    next(authStore.isAdmin ? '/admin' : '/')
  } else {
    next()
  }
})

export default router
