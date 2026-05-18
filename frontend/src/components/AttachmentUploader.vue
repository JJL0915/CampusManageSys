<template>
  <div class="attachment-uploader">
    <el-upload
      v-model:file-list="fileList"
      drag
      multiple
      :auto-upload="false"
      :show-file-list="false"
      :accept="accept"
      :limit="limit"
      :on-change="handleChange"
      :on-exceed="handleExceed"
    >
      <el-icon class="attachment-upload-icon"><UploadFilled /></el-icon>
      <div class="attachment-upload-title">{{ title }}</div>
      <div class="attachment-upload-hint">{{ hint }}</div>
    </el-upload>

    <div v-if="existing.length || fileList.length" class="attachment-files">
      <p class="attachment-section-title">已上传文件</p>
      <article v-for="file in existing" :key="`existing-${file.id}`" class="attachment-file-row">
        <span class="attachment-file-kind" :class="{ image: file.is_image }">
          <el-icon><Picture v-if="file.is_image" /><Document v-else /></el-icon>
        </span>
        <a :href="file.url" target="_blank" rel="noreferrer">{{ file.original_name }}</a>
        <small>{{ formatSize(file.size) }}</small>
        <el-button text :icon="Close" @click="removeExisting(file.id)" />
      </article>

      <article v-for="file in fileList" :key="file.uid" class="attachment-file-row">
        <span class="attachment-file-kind" :class="{ image: isImageFile(file) }">
          <el-icon><Picture v-if="isImageFile(file)" /><Document v-else /></el-icon>
        </span>
        <span>{{ file.name }}</span>
        <small>{{ formatSize(file.size || file.raw?.size || 0) }}</small>
        <el-button text :icon="Close" @click="removeNew(file.uid)" />
      </article>
    </div>

    <div v-if="imagePreviews.length" class="attachment-preview-grid">
      <figure v-for="image in imagePreviews" :key="image.key">
        <img :src="image.url" :alt="image.name" />
      </figure>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Close, Document, Picture, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadFiles, UploadUserFile } from 'element-plus'
import type { Attachment } from '../api/types'

const props = withDefaults(
  defineProps<{
    existing?: Attachment[]
    title?: string
    hint?: string
    limit?: number
  }>(),
  {
    existing: () => [],
    title: '点击上传或拖拽文件到此处',
    hint: '支持 PDF、Word、PPT、Excel、ZIP 和图片，单个文件不超过20MB',
    limit: 8
  }
)

const emit = defineEmits<{
  'update:existing': [value: Attachment[]]
}>()

const accept =
  '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.rar,.7z,.txt,.md,.jpg,.jpeg,.png,.gif,.webp'
const maxSize = 20 * 1024 * 1024
const fileList = ref<UploadUserFile[]>([])

const imagePreviews = computed(() => {
  const existingImages = props.existing
    .filter((file) => file.is_image)
    .map((file) => ({ key: `existing-${file.id}`, name: file.original_name, url: file.url }))
  const newImages = fileList.value
    .filter((file) => isImageFile(file) && file.url)
    .map((file) => ({ key: `new-${file.uid}`, name: file.name, url: file.url || '' }))
  return [...existingImages, ...newImages]
})

function isImageFile(file: UploadUserFile) {
  const rawType = file.raw?.type || ''
  return rawType.startsWith('image/') || /\.(jpg|jpeg|png|gif|webp)$/i.test(file.name)
}

function handleChange(uploadFile: UploadFile, uploadFiles: UploadFiles) {
  if (uploadFile.size && uploadFile.size > maxSize) {
    fileList.value = uploadFiles.filter((file) => file.uid !== uploadFile.uid)
    ElMessage.warning('单个附件不能超过20MB')
  }
}

function handleExceed() {
  ElMessage.warning(`最多上传 ${props.limit} 个附件`)
}

function removeExisting(id: number) {
  emit(
    'update:existing',
    props.existing.filter((file) => file.id !== id)
  )
}

function removeNew(uid?: number) {
  if (uid === undefined) return
  fileList.value = fileList.value.filter((file) => file.uid !== uid)
}

function formatSize(size: number) {
  if (!size) return '0 KB'
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(2)} MB`
  return `${Math.ceil(size / 1024)} KB`
}

function getFiles() {
  return fileList.value.map((file) => file.raw).filter(Boolean) as File[]
}

function reset() {
  fileList.value = []
}

defineExpose({ getFiles, reset })
</script>
