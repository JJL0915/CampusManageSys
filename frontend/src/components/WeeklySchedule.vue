<template>
  <section class="schedule-card">
    <header class="schedule-head">
      <div>
        <h3>{{ title }}</h3>
        <p>{{ subtitle }}</p>
      </div>
      <div v-if="showControls" class="schedule-controls">
        <el-button :icon="ArrowLeft" @click="$emit('prev')"></el-button>
        <strong>第 {{ week }} 周</strong>
        <el-button :icon="ArrowRight" @click="$emit('next')"></el-button>
        <el-button :icon="Calendar" @click="$emit('today')">回到本周</el-button>
      </div>
    </header>

    <div class="schedule-table">
      <div class="schedule-cell schedule-header">时间</div>
      <div v-for="day in days" :key="day.value" class="schedule-cell schedule-header">{{ day.label }}</div>
      <template v-for="slot in slots" :key="slot.key">
        <div class="schedule-cell schedule-time">{{ variant === 'section' ? slot.sectionLabel : slot.timeLabel }}</div>
        <div v-for="day in days" :key="`${slot.key}-${day.value}`" class="schedule-cell">
          <article
            v-for="item in cellItems(day.value, slot.start)"
            :key="`${item.course_id}-${item.weekday}-${item.start_section}-${item.classroom}`"
            class="course-chip"
            :class="`tone-${item.course_id % 5}`"
          >
            <strong>{{ item.course_name }}</strong>
            <span>{{ item.classroom }}</span>
            <small v-if="showTeacher">{{ item.teacher_name }}</small>
          </article>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ArrowLeft, ArrowRight, Calendar } from '@element-plus/icons-vue'
import type { WeeklyScheduleItem } from '../api/types'

const props = withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    entries: WeeklyScheduleItem[]
    week?: number
    variant?: 'section' | 'time'
    showControls?: boolean
    showTeacher?: boolean
  }>(),
  {
    subtitle: '',
    week: 12,
    variant: 'time',
    showControls: false,
    showTeacher: false
  }
)

defineEmits<{
  prev: []
  next: []
  today: []
}>()

const days = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 }
]

const slots = [
  { key: '1-2', start: 1, sectionLabel: '1-2节', timeLabel: '08:00-09:35' },
  { key: '3-4', start: 3, sectionLabel: '3-4节', timeLabel: '10:00-11:35' },
  { key: '5-6', start: 5, sectionLabel: '5-6节', timeLabel: '14:00-15:35' },
  { key: '7-8', start: 7, sectionLabel: '7-8节', timeLabel: '16:00-17:35' },
  { key: '9-10', start: 9, sectionLabel: '9-10节', timeLabel: '19:00-20:35' }
]

function cellItems(weekday: number, startSection: number) {
  return props.entries.filter((item) => item.weekday === weekday && item.start_section === startSection)
}
</script>

