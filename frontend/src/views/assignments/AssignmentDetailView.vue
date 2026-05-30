<template>
  <section>
    <div class="page-head">
      <div>
        <el-button text :icon="ArrowLeft" @click="$router.push('/assignments')">返回作业列表</el-button>
        <h2>{{ assignment?.title || '作业详情' }}</h2>
        <p>{{ assignment?.course_name }}</p>
      </div>
      <el-button v-if="canSubmit" type="primary" :icon="EditPen" @click="goSubmit">{{ submitButtonText }}</el-button>
    </div>

    <div v-if="assignment" class="assignment-detail-grid">
      <section class="panel">
        <h3>作业信息</h3>
        <div class="detail-list">
          <div class="detail-row"><span>截止时间</span><strong>{{ formatDateTime(assignment.deadline) }}</strong></div>
          <div class="detail-row"><span>总分</span><strong>{{ assignment.max_score }}分</strong></div>
          <div class="detail-row"><span>作业类型</span><strong>{{ assignment.assignment_type }}</strong></div>
          <div class="detail-row"><span>提交状态</span><el-tag :type="stateTagType">{{ stateText }}</el-tag></div>
          <div class="detail-row" v-if="assignment.grade !== null"><span>成绩</span><strong>{{ assignment.grade }}</strong></div>
        </div>
      </section>

      <section class="panel">
        <h3>作业描述</h3>
        <p style="white-space: pre-wrap; line-height: 1.8">{{ assignment.description || '暂无说明' }}</p>
        <template v-if="assignment.attachments.length">
          <el-divider />
          <h3>作业附件</h3>
          <div class="attachment-files">
            <article v-for="file in assignment.attachments" :key="file.id" class="attachment-file-row">
              <span class="attachment-file-kind" :class="{ image: file.is_image }">
                <el-icon><Picture v-if="file.is_image" /><Document v-else /></el-icon>
              </span>
              <a :href="file.url" target="_blank" rel="noreferrer">{{ file.original_name }}</a>
              <small>{{ formatSize(file.size) }}</small>
              <span></span>
            </article>
          </div>
          <div v-if="assignment.attachments.some((file) => file.is_image)" class="attachment-preview-grid" style="margin-top: 12px">
            <figure v-for="file in assignment.attachments.filter((item) => item.is_image)" :key="`image-${file.id}`">
              <img :src="file.url" :alt="file.original_name" />
            </figure>
          </div>
        </template>
      </section>
    </div>

    <section v-if="submission" class="panel" style="margin-top: 18px">
      <h3>我的提交</h3>
      <p style="white-space: pre-wrap; line-height: 1.8">{{ submission.content }}</p>
      <template v-if="submission.attachments.length">
        <el-divider />
        <h3>提交附件</h3>
        <div class="attachment-files">
          <article v-for="file in submission.attachments" :key="file.id" class="attachment-file-row">
            <span class="attachment-file-kind" :class="{ image: file.is_image }">
              <el-icon><Picture v-if="file.is_image" /><Document v-else /></el-icon>
            </span>
            <a :href="file.url" target="_blank" rel="noreferrer">{{ file.original_name }}</a>
            <small>{{ formatSize(file.size) }}</small>
            <span></span>
          </article>
        </div>
        <div v-if="submission.attachments.some((file) => file.is_image)" class="attachment-preview-grid" style="margin-top: 12px">
          <figure v-for="file in submission.attachments.filter((item) => item.is_image)" :key="`submission-image-${file.id}`">
            <img :src="file.url" :alt="file.original_name" />
          </figure>
        </div>
      </template>
      <el-divider />
      <p>提交时间：{{ formatDateTime(submission.submit_time) }}</p>
      <p v-if="submission.feedback">教师评语：{{ submission.feedback }}</p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Document, EditPen, Picture } from '@element-plus/icons-vue'
import { getAssignment } from '../../api/assignments'
import { getSubmissions } from '../../api/submissions'
import type { Assignment, Submission } from '../../api/types'
import { useAuthStore } from '../../stores/auth'
import { formatDateTime } from '../../utils/time'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const assignment = ref<Assignment | null>(null)
const submission = ref<Submission | null>(null)

const assignmentId = computed(() => Number(route.params.id))

const stateText = computed(() => {
  if (!assignment.value) return ''
  if (assignment.value.submission_status === 'graded') return `已批改 ${assignment.value.grade ?? ''}`
  if (assignment.value.submission_status === 'submitted') return '待批改'
  if (assignment.value.status === 'closed') return '已截止'
  return '未提交'
})

const stateTagType = computed(() => {
  if (assignment.value?.submission_status === 'graded') return 'success'
  if (assignment.value?.submission_status === 'submitted') return 'warning'
  if (assignment.value?.status === 'closed') return 'danger'
  return 'info'
})

const canSubmit = computed(() => auth.user?.role === 'student' && assignment.value?.status === 'open' && assignment.value?.submission_status !== 'graded')
const submitButtonText = computed(() => (assignment.value?.submitted ? '修改提交' : '开始提交'))

async function loadData() {
  assignment.value = null
  submission.value = null
  assignment.value = await getAssignment(assignmentId.value)
  if (auth.user?.role === 'student') {
    const list = await getSubmissions({ assignment_id: assignmentId.value })
    submission.value = list[0] || null
  }
}

function goSubmit() {
  router.push(`/assignments/${assignmentId.value}/submit`)
}

function formatSize(size: number) {
  if (!size) return '0 KB'
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(2)} MB`
  return `${Math.ceil(size / 1024)} KB`
}

onMounted(loadData)

watch(
  () => [assignmentId.value, route.query.notice, route.query.refresh],
  () => {
    loadData()
  }
)
</script>
