<template>
  <section>
    <div class="page-head">
      <div>
        <h2>提交与批改</h2>
        <p>{{ hintText }}</p>
      </div>
      <div class="toolbar">
        <el-select v-model="statusFilter" clearable placeholder="批改状态" style="width: 160px" @change="loadData">
          <el-option label="待批改" value="submitted" />
          <el-option label="已批改" value="graded" />
        </el-select>
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="submissions" v-loading="loading" :row-class-name="getRowClassName">
        <el-table-column prop="assignment_title" label="作业" min-width="160" />
        <el-table-column prop="course_name" label="课程" width="140" />
        <el-table-column v-if="auth.user?.role !== 'student'" prop="student_name" label="学生" width="120" />
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">{{ formatDateTime(row.submit_time) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'graded' ? 'success' : 'warning'">
              {{ row.status === 'graded' ? '已批改' : '待批改' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成绩" width="100">
          <template #default="{ row }">{{ row.grade ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="content" label="提交内容" min-width="220" show-overflow-tooltip />
        <el-table-column label="附件" width="90">
          <template #default="{ row }">{{ row.attachments.length || '-' }}</template>
        </el-table-column>
        <el-table-column prop="feedback" label="评语" min-width="180" show-overflow-tooltip />
        <el-table-column v-if="auth.user?.role === 'teacher'" label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" :icon="EditPen" @click="openGrade(row)">批改</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="gradeDialog" title="批改作业" width="620px">
      <el-descriptions v-if="gradeTarget" :column="2" border>
        <el-descriptions-item label="学生">{{ gradeTarget.student_name }}</el-descriptions-item>
        <el-descriptions-item label="课程">{{ gradeTarget.course_name }}</el-descriptions-item>
        <el-descriptions-item label="作业" :span="2">{{ gradeTarget.assignment_title }}</el-descriptions-item>
        <el-descriptions-item label="提交内容" :span="2">{{ gradeTarget.content }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="gradeTarget?.attachments.length" style="margin-top: 16px">
        <h3>提交附件</h3>
        <div class="attachment-files">
          <article v-for="file in gradeTarget.attachments" :key="file.id" class="attachment-file-row">
            <span class="attachment-file-kind" :class="{ image: file.is_image }">
              <el-icon><Picture v-if="file.is_image" /><Document v-else /></el-icon>
            </span>
            <a :href="file.url" target="_blank" rel="noreferrer">{{ file.original_name }}</a>
            <small>{{ formatSize(file.size) }}</small>
            <span></span>
          </article>
        </div>
        <div v-if="gradeTarget.attachments.some((file) => file.is_image)" class="attachment-preview-grid" style="margin-top: 12px">
          <figure v-for="file in gradeTarget.attachments.filter((item) => item.is_image)" :key="`grade-image-${file.id}`">
            <img :src="file.url" :alt="file.original_name" />
          </figure>
        </div>
      </div>
      <el-form label-position="top" style="margin-top: 16px">
        <el-form-item label="成绩">
          <el-input-number v-model="gradeForm.grade" :min="0" :max="100" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="gradeForm.feedback" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gradeDialog = false">取消</el-button>
        <el-button type="primary" @click="handleGrade">保存成绩</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Document, EditPen, Picture, Refresh } from '@element-plus/icons-vue'
import { gradeSubmission, getSubmissions } from '../../api/submissions'
import type { Submission } from '../../api/types'
import { useAuthStore } from '../../stores/auth'
import { formatDateTime } from '../../utils/time'

const auth = useAuthStore()
const route = useRoute()
const submissions = ref<Submission[]>([])
const statusFilter = ref<string | undefined>(typeof route.query.status === 'string' ? route.query.status : undefined)
const selectedSubmissionId = ref<number | null>(parseSubmissionId(route.query.submission_id))
const loading = ref(false)
const gradeDialog = ref(false)
const gradeTarget = ref<Submission | null>(null)
const gradeForm = reactive({ grade: 0, feedback: '' })

const hintText = computed(() => {
  if (auth.user?.role === 'student') return '查看自己的提交状态、成绩和教师评语。'
  if (auth.user?.role === 'teacher') return '查看本人课程下的提交记录并录入成绩。'
  return '管理员查看全局提交和批改状态。'
})

async function loadData() {
  loading.value = true
  try {
    submissions.value = await getSubmissions({ status: statusFilter.value })
  } finally {
    loading.value = false
  }
}

function parseSubmissionId(value: unknown) {
  const rawValue = Array.isArray(value) ? value[0] : value
  const id = Number(rawValue)
  return Number.isFinite(id) && id > 0 ? id : null
}

function syncRouteQuery() {
  statusFilter.value = typeof route.query.status === 'string' ? route.query.status : undefined
  selectedSubmissionId.value = parseSubmissionId(route.query.submission_id)
}

function getRowClassName({ row }: { row: Submission }) {
  return selectedSubmissionId.value === row.id ? 'submission-row-highlight' : ''
}

function openGrade(row: Submission) {
  gradeTarget.value = row
  gradeForm.grade = row.grade ?? 0
  gradeForm.feedback = row.feedback || ''
  gradeDialog.value = true
}

async function handleGrade() {
  if (!gradeTarget.value) return
  await gradeSubmission(gradeTarget.value.id, { grade: gradeForm.grade, feedback: gradeForm.feedback })
  gradeDialog.value = false
  await loadData()
}

function formatSize(size: number) {
  if (!size) return '0 KB'
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(2)} MB`
  return `${Math.ceil(size / 1024)} KB`
}

onMounted(() => {
  syncRouteQuery()
  loadData()
})

watch(
  () => [route.query.status, route.query.submission_id, route.query.notice, route.query.refresh],
  () => {
    syncRouteQuery()
    loadData()
  }
)
</script>
