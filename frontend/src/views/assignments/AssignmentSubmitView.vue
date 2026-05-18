<template>
  <section>
    <div class="page-head">
      <div>
        <el-button text :icon="ArrowLeft" @click="$router.push(`/assignments/${assignmentId}`)">返回作业详情</el-button>
        <h2>{{ assignment?.title || '提交作业' }}</h2>
        <p>{{ assignment?.course_name }}</p>
      </div>
      <el-button type="primary" :icon="Upload" @click="saveSubmit">提交</el-button>
    </div>

    <div class="assignment-detail-grid">
      <section class="panel">
        <h3>题目要求</h3>
        <p style="white-space: pre-wrap; line-height: 1.8">{{ assignment?.description || '暂无说明' }}</p>
        <template v-if="assignment?.attachments.length">
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
        </template>
      </section>
      <section class="panel">
        <h3>提交说明</h3>
        <el-input v-model="content" type="textarea" :rows="7" maxlength="500" show-word-limit placeholder="填写作业说明、附件说明或提交链接" />
        <el-divider />
        <h3>提交附件</h3>
        <AttachmentUploader
          ref="submissionUploader"
          v-model:existing="existingAttachments"
          title="点击上传或拖拽提交文件到此处"
          hint="支持 PDF、Word、PPT、ZIP、图片等附件；提交后仍可在截止前修改"
        />
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Document, Picture, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getAssignment } from '../../api/assignments'
import { getSubmissions, submitAssignmentWithFiles, updateSubmissionWithFiles } from '../../api/submissions'
import type { Assignment, Attachment, Submission } from '../../api/types'
import AttachmentUploader from '../../components/AttachmentUploader.vue'

const route = useRoute()
const router = useRouter()
const assignment = ref<Assignment | null>(null)
const submission = ref<Submission | null>(null)
const content = ref('')
const existingAttachments = ref<Attachment[]>([])
const submissionUploader = ref<InstanceType<typeof AttachmentUploader> | null>(null)
const assignmentId = computed(() => Number(route.params.id))

async function loadData() {
  assignment.value = await getAssignment(assignmentId.value)
  const list = await getSubmissions({ assignment_id: assignmentId.value })
  submission.value = list[0] || null
  content.value = submission.value?.content || ''
  existingAttachments.value = submission.value?.attachments ? [...submission.value.attachments] : []
  submissionUploader.value?.reset()
}

async function saveSubmit() {
  const files = submissionUploader.value?.getFiles() || []
  if (!content.value.trim() && !files.length && !existingAttachments.value.length) {
    ElMessage.warning('请填写提交说明或上传附件')
    return
  }
  if (submission.value) {
    await updateSubmissionWithFiles(submission.value.id, {
      content: content.value,
      files,
      keep_attachment_ids: existingAttachments.value.map((file) => file.id)
    })
  } else {
    await submitAssignmentWithFiles({ assignment_id: assignmentId.value, content: content.value, files })
  }
  router.push(`/assignments/${assignmentId.value}`)
}

function formatSize(size: number) {
  if (!size) return '0 KB'
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(2)} MB`
  return `${Math.ceil(size / 1024)} KB`
}

onMounted(loadData)
</script>
