import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const adminAllowedPaths = new Set(['/dashboard', '/courses'])
const adminBlockedPaths = ['/assignments', '/submissions', '/admin']

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue')
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('../views/dashboard/DashboardView.vue') },
        { path: 'courses', name: 'courses', component: () => import('../views/courses/CourseListView.vue') },
        { path: 'assignments', name: 'assignments', component: () => import('../views/assignments/AssignmentListView.vue') },
        { path: 'assignments/:id/submit', name: 'assignment-submit', component: () => import('../views/assignments/AssignmentSubmitView.vue') },
        { path: 'assignments/:id', name: 'assignment-detail', component: () => import('../views/assignments/AssignmentDetailView.vue') },
        { path: 'submissions', name: 'submissions', component: () => import('../views/assignments/SubmissionListView.vue') },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('../views/admin/AdminConsoleView.vue'),
          meta: { roles: ['admin'] }
        }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthed) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  const roles = to.meta.roles as Array<'student' | 'teacher' | 'admin'> | undefined
  if (!auth.hasRole(roles)) {
    return { path: '/dashboard' }
  }
  if (
    auth.user?.role === 'admin' &&
    !adminAllowedPaths.has(to.path) &&
    adminBlockedPaths.some((path) => to.path === path || to.path.startsWith(`${path}/`))
  ) {
    return { path: '/dashboard' }
  }
  if (to.path === '/login' && auth.isAuthed) {
    return { path: '/dashboard' }
  }
})

export default router
