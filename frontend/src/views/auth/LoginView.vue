<template>
  <main class="login-page">
    <section class="login-visual">
      <div class="login-visual-copy">
        <p class="login-visual-kicker">课程管理 · 作业协同平台</p>
        <h1>
          <span>课程、作业与成绩</span>
          <span>一站式高效管理</span>
        </h1>
        <span class="login-visual-line"></span>
        <p class="login-visual-desc">面向学生、教师与管理员，统一完成课程管理、作业发布、提交批改与成绩查看。</p>
      </div>
    </section>

    <section class="panel login-card">
      <h2>登录系统</h2>
      <p>使用演示账号进入对应角色工作台。</p>
      <el-form :model="form" label-position="top" @keyup.enter="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" size="large" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleLogin">
          登录
        </el-button>
      </el-form>
      <div class="quick-login">
        <el-button @click="fill('student1', '123456')">学生</el-button>
        <el-button @click="fill('teacher1', '123456')">教师</el-button>
        <el-button @click="fill('admin', 'admin123')">管理员</el-button>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const loading = ref(false)
const form = reactive({ username: 'student1', password: '123456' })

function fill(username: string, password: string) {
  form.username = username
  form.password = password
}

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push((route.query.redirect as string) || '/dashboard')
  } finally {
    loading.value = false
  }
}
</script>
