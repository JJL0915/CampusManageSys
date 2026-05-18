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
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/courses">
          <el-icon><School /></el-icon>
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item index="/assignments">
          <el-icon><Notebook /></el-icon>
          <span>作业管理</span>
        </el-menu-item>
        <el-menu-item index="/submissions">
          <el-icon><DocumentChecked /></el-icon>
          <span>提交与批改</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'admin'" index="/admin">
          <el-icon><User /></el-icon>
          <span>账号维护</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <p>{{ roleLabel }}</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="user-box">
          <el-tag effect="dark" type="success">{{ auth.user?.real_name }}</el-tag>
          <el-button :icon="SwitchButton" circle title="退出登录" @click="handleLogout" />
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataAnalysis, DocumentChecked, Notebook, School, SwitchButton, User } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

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

const pageTitle = computed(() => titleMap[route.path] || '工作台')
const roleLabel = computed(() => roleText[auth.user?.role || 'student'])

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

