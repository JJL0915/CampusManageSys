<template>
  <main class="login-page">
    <section class="login-visual">
      <div>
        <p>在线选课 + 作业管理系统</p>
        <h1>课程、作业、提交、批改和成绩统计集中处理。</h1>
      </div>
      <p>学生完成选课和提交，教师发布与批改，管理员维护课程和账号。数据统计使用 ECharts 展示提交状态和成绩分布。</p>
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

