<template>
  <el-container class="shell">
    <el-aside width="248px" class="sidebar">
      <div class="brand">
        <span>CM</span>
        <div>
          <strong>课程作业管理</strong>
          <small>CourseOps Console</small>
        </div>
      </div>
      <el-menu router :default-active="$route.path" class="side-menu">
        <el-menu-item v-if="canShowMenu('/dashboard')" index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据仪表盘</span>
        </el-menu-item>
        <el-menu-item v-if="canShowMenu('/courses')" index="/courses">
          <el-icon><School /></el-icon>
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role !== 'admin' && canShowMenu('/assignments')" index="/assignments">
          <el-icon><Notebook /></el-icon>
          <span>作业管理</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role !== 'admin' && canShowMenu('/submissions')" index="/submissions">
          <el-icon><DocumentChecked /></el-icon>
          <span>提交与批改</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'admin'" index="/admin">
          <el-icon><User /></el-icon>
          <span>账号维护</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-user">
        <span>{{ auth.user?.real_name?.slice(0, 1) || 'U' }}</span>
        <div>
          <strong>{{ auth.user?.real_name }}</strong>
          <small>{{ roleLabel }}</small>
        </div>
        <el-button :icon="SwitchButton" class="sidebar-logout" circle title="退出登录" @click="handleLogout" />
      </div>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <p>{{ roleLabel }}</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="user-box">
          <el-popover
            v-model:visible="notificationVisible"
            placement="bottom-end"
            width="360"
            trigger="click"
            popper-class="notification-popover"
          >
            <template #reference>
              <el-button class="glass-icon-button notification-button" :class="{ 'has-notice': notifications.length }" circle title="通知">
                <el-icon><Bell /></el-icon>
                <span v-if="notifications.length" class="notice-count">{{ notifications.length }}</span>
              </el-button>
            </template>
            <section class="notification-panel">
              <header>
                <div>
                  <strong>新消息</strong>
                  <small>来自作业与成绩接口</small>
                </div>
                <el-button text size="small" @click="loadNotifications">刷新</el-button>
              </header>
              <button
                v-for="item in notifications"
                :key="item.id"
                class="notification-item"
                :class="`tone-${item.tone}`"
                type="button"
                @click="openNotification(item)"
              >
                <span></span>
                <div>
                  <strong>{{ item.title }}</strong>
                  <small>{{ item.description }}</small>
                </div>
              </button>
              <div v-if="!notifications.length" class="notification-empty">
                <strong>暂无新消息</strong>
                <small>新作业、待批改提交和成绩会显示在这里。</small>
              </div>
            </section>
          </el-popover>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, DataAnalysis, DocumentChecked, Notebook, School, SwitchButton, User } from '@element-plus/icons-vue'
import { getAssignments } from '../api/assignments'
import { getSubmissions } from '../api/submissions'
import type { Assignment, Submission } from '../api/types'
import { useAuthStore } from '../stores/auth'
import { formatDateTime } from '../utils/time'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const titleMap: Record<string, string> = {
  '/dashboard': '数据仪表盘',
  '/courses': '课程管理',
  '/assignments': '作业管理',
  '/submissions': '提交与批改',
  '/admin': '账号维护'
}

const roleText: Record<string, string> = {
  student: '学生端',
  teacher: '教师端',
  admin: '管理端'
}

const adminAllowedMenuPaths = new Set(['/dashboard', '/courses', '/admin'])
const pageTitle = computed(() => titleMap[route.path] || '工作台')
const roleLabel = computed(() => roleText[auth.user?.role || 'student'])
const notifications = ref<NotificationItem[]>([])
const notificationVisible = ref(false)

interface NotificationItem {
  id: string
  title: string
  description: string
  route: NotificationRoute
  tone: 'blue' | 'green' | 'orange'
}

interface NotificationDateSource {
  created_at?: string
  submit_time?: string
  graded_at?: string | null
}

interface NotificationRoute {
  path: string
  query?: Record<string, string>
}

function byNewest(left: NotificationDateSource, right: NotificationDateSource) {
  const leftTime = left.graded_at || left.submit_time || left.created_at || ''
  const rightTime = right.graded_at || right.submit_time || right.created_at || ''
  return new Date(rightTime).getTime() - new Date(leftTime).getTime()
}

function noticeRoute(path: string, noticeId: string, query: Record<string, string> = {}): NotificationRoute {
  return {
    path,
    query: {
      ...query,
      notice: noticeId
    }
  }
}

function isCurrentNotificationRoute(target: NotificationRoute) {
  if (route.path !== target.path) return false
  return Object.entries(target.query || {}).every(([key, value]) => route.query[key] === value)
}

function withNavigationRefresh(target: NotificationRoute): NotificationRoute {
  return {
    path: target.path,
    query: {
      ...target.query,
      refresh: Date.now().toString(36)
    }
  }
}

function canShowMenu(path: string) {
  if (path === '/admin') return auth.user?.role === 'admin'
  return auth.user?.role !== 'admin' || adminAllowedMenuPaths.has(path)
}

function assignmentNotice(item: Assignment): NotificationItem {
  const id = `assignment-${item.id}`
  return {
    id,
    title: `新作业：${item.title}`,
    description: `${item.course_name} · 截止 ${formatDateTime(item.deadline)}`,
    route: noticeRoute(`/assignments/${item.id}`, id),
    tone: 'blue'
  }
}

function gradeNotice(item: Submission): NotificationItem {
  const id = `grade-${item.id}`
  return {
    id,
    title: `成绩已发布：${item.assignment_title}`,
    description: `${item.course_name} · ${item.grade ?? '-'} 分`,
    route: noticeRoute(`/assignments/${item.assignment_id}`, id, { submission_id: String(item.id) }),
    tone: 'green'
  }
}

function submissionNotice(item: Submission): NotificationItem {
  const id = `submission-${item.id}`
  return {
    id,
    title: `${item.student_name} 提交了作业`,
    description: `${item.course_name} · ${item.assignment_title}`,
    route: noticeRoute('/submissions', id, { status: 'submitted', submission_id: String(item.id) }),
    tone: 'orange'
  }
}

async function loadNotifications() {
  if (!auth.isAuthed) {
    notifications.value = []
    return
  }
  if (auth.user?.role === 'admin') {
    notifications.value = []
    return
  }
  try {
    if (auth.user?.role === 'teacher') {
      const submissions = await getSubmissions({ status: 'submitted' })
      notifications.value = submissions.sort(byNewest).slice(0, 6).map(submissionNotice)
      return
    }

    const [assignments, submissions] = await Promise.all([
      getAssignments({ only_mine: true }),
      getSubmissions({ status: 'graded' })
    ])
    const newAssignments = assignments
      .filter((item) => item.status === 'open' && !item.submitted)
      .sort(byNewest)
      .slice(0, 3)
      .map(assignmentNotice)
    const gradeItems = submissions.sort(byNewest).slice(0, 3).map(gradeNotice)
    notifications.value = [...newAssignments, ...gradeItems].slice(0, 6)
  } catch {
    notifications.value = []
  }
}

async function openNotification(item: NotificationItem) {
  notificationVisible.value = false
  if (isCurrentNotificationRoute(item.route)) {
    await router.replace(withNavigationRefresh(item.route))
    return
  }
  await router.push(item.route)
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(loadNotifications)

watch(
  () => route.fullPath,
  () => {
    loadNotifications()
  }
)
</script>
