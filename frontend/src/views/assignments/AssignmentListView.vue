<template>
  <section>
    <div class="page-head">
      <div>
        <h2>作业列表</h2>
        <p>{{ hintText }}</p>
      </div>
      <div class="toolbar">
        <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 160px">
          <el-option label="开放中" value="open" />
          <el-option label="未提交" value="unsubmitted" />
          <el-option label="待批改" value="submitted" />
          <el-option label="已批改" value="graded" />
          <el-option label="已截止" value="closed" />
        </el-select>
        <el-input v-model="keyword" clearable placeholder="搜索作业标题" style="width: 260px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
        <el-button v-if="auth.user?.role === 'teacher'" type="primary" :icon="Plus" @click="openCreate">发布作业</el-button>
      </div>
    </div>

    <div class="assignment-list">
      <article v-for="item in filteredAssignments" :key="item.id" class="assignment-card" @click="openDetail(item.id)">
        <div class="assignment-icon"><el-icon><Document /></el-icon></div>
        <div class="assignment-main">
          <h3>{{ item.title }}</h3>
          <div class="assignment-meta">
            <span>{{ item.course_name }}</span>
            <span>截止时间：{{ formatDateTime(item.deadline) }}</span>
            <span>{{ item.max_score }}分</span>
            <span v-if="item.attachments.length">附件 {{ item.attachments.length }}</span>
          </div>
        </div>
        <el-tag :type="tagType(item)">{{ assignmentStateText(item) }}</el-tag>
        <el-icon><ArrowRight /></el-icon>
      </article>
    </div>

    <el-dialog v-model="assignmentDialog" title="发布作业" width="680px">
      <el-form label-position="top">
        <el-form-item label="所属课程">
          <el-select v-model="assignmentForm.course_id" style="width: 100%">
            <el-option v-for="course in courses" :key="course.id" :label="course.name" :value="course.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="作业标题">
          <el-input v-model="assignmentForm.title" />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-input v-model="assignmentForm.deadline" type="datetime-local" />
        </el-form-item>
        <el-form-item label="作业说明">
          <el-input v-model="assignmentForm.description" type="textarea" :rows="5" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="作业附件">
          <AttachmentUploader ref="assignmentUploader" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignmentDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAssignment">保存并发布</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Document, Plus, Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createAssignmentWithFiles, getAssignments } from '../../api/assignments'
import { getCourses } from '../../api/courses'
import type { Assignment, AssignmentPayload, Course } from '../../api/types'
import AttachmentUploader from '../../components/AttachmentUploader.vue'
import { useAuthStore } from '../../stores/auth'
import { formatDateTime, toDatetimeLocal } from '../../utils/time'

const auth = useAuthStore()
const router = useRouter()
const courses = ref<Course[]>([])
const assignments = ref<Assignment[]>([])
const statusFilter = ref('')
const keyword = ref('')
const assignmentDialog = ref(false)
const assignmentUploader = ref<InstanceType<typeof AttachmentUploader> | null>(null)

const assignmentForm = reactive<AssignmentPayload>({
  course_id: 0,
  title: '',
  description: '',
  deadline: ''
})

const hintText = computed(() => {
  if (auth.user?.role === 'student') return '查看并提交已选课程作业，点击条目进入详情。'
  if (auth.user?.role === 'teacher') return '发布作业并查看学生提交情况。'
  return '查看全局作业发布情况。'
})

const filteredAssignments = computed(() => {
  return assignments.value.filter((item) => {
    const matchesKeyword = !keyword.value || item.title.includes(keyword.value) || item.course_name.includes(keyword.value)
    const matchesStatus =
      !statusFilter.value ||
      (statusFilter.value === 'open' && item.status === 'open') ||
      (statusFilter.value === 'closed' && item.status === 'closed') ||
      (statusFilter.value === 'unsubmitted' && !item.submitted) ||
      (statusFilter.value === 'submitted' && item.submission_status === 'submitted') ||
      (statusFilter.value === 'graded' && item.submission_status === 'graded')
    return matchesKeyword && matchesStatus
  })
})

function assignmentStateText(item: Assignment) {
  if (item.submission_status === 'graded') return `已批改 ${item.grade ?? ''}`
  if (item.submission_status === 'submitted') return '待批改'
  if (item.status === 'closed') return '已截止'
  return item.submitted ? '已提交' : '进行中'
}

function tagType(item: Assignment) {
  if (item.submission_status === 'graded') return 'success'
  if (item.submission_status === 'submitted') return 'warning'
  if (item.status === 'closed') return 'danger'
  return 'success'
}

async function loadCourses() {
  courses.value = await getCourses({ only_mine: auth.user?.role === 'teacher' })
}

async function loadData() {
  assignments.value = await getAssignments({ only_mine: auth.user?.role !== 'admin' })
}

function openCreate() {
  Object.assign(assignmentForm, {
    course_id: courses.value[0]?.id || 0,
    title: '',
    description: '',
    deadline: toDatetimeLocal(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString())
  })
  assignmentDialog.value = true
  nextTick(() => assignmentUploader.value?.reset())
}

async function saveAssignment() {
  if (!assignmentForm.title || !assignmentForm.deadline || !assignmentForm.course_id) {
    ElMessage.warning('请填写课程、标题和截止时间')
    return
  }
  const files = assignmentUploader.value?.getFiles() || []
  await createAssignmentWithFiles(assignmentForm, files)
  assignmentDialog.value = false
  await loadData()
}

function openDetail(id: number) {
  router.push(`/assignments/${id}`)
}

onMounted(async () => {
  await loadCourses()
  await loadData()
})
</script>
