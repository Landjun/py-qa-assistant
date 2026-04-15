import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        { path: '/dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
        { path: '/students', name: 'students', component: () => import('@/views/StudentList.vue') },
        { path: '/students/:id', name: 'student-detail', component: () => import('@/views/StudentDetail.vue') },
        { path: '/ai-analysis', name: 'ai-analysis', component: () => import('@/views/AIAnalysis.vue') },
        { path: '/assets', name: 'assets', component: () => import('@/views/AssetLibrary.vue') }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (to.path === '/login' && auth.isLogin) return '/dashboard'
    return true
  }
  if (!auth.isLogin) return '/login'
  return true
})

export default router
