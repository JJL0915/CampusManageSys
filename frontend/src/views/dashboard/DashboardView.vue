<template>
  <section>
    <div class="page-head">
      <div>
        <h2>运行概览</h2>
        <p>汇总课程、作业、提交、批改和课程成绩分布。</p>
      </div>
      <el-button :icon="Refresh" @click="loadData">刷新</el-button>
    </div>

    <div class="stat-grid">
      <StatCard
        v-for="(card, index) in stats?.cards || []"
        :key="card.label"
        :label="card.label"
        :value="card.value"
        :trend="card.trend"
        :icon="cardIcons[index % cardIcons.length]"
      />
    </div>

    <div class="chart-grid">
      <ChartPanel title="提交状态" subtitle="待批改与已批改比例" :option="statusOption" />
      <ChartPanel title="课程作业统计" subtitle="课程维度作业与提交量" :option="courseOption" />
    </div>

    <div class="chart-grid" style="margin-top: 18px">
      <ChartPanel title="课程成绩统计" subtitle="按课程统计平均分" :option="courseGradeOption" />
      <WeeklySchedule
        title="本周课表"
        subtitle="按已选课程和当前周次展示"
        :entries="stats?.weekly_schedule || []"
        :week="12"
        variant="section"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { DataAnalysis, DocumentChecked, Notebook, Refresh, School } from '@element-plus/icons-vue'
import type { EChartsOption } from 'echarts'
import { getOverviewStats } from '../../api/statistics'
import type { OverviewStats } from '../../api/types'
import ChartPanel from '../../components/ChartPanel.vue'
import StatCard from '../../components/StatCard.vue'
import WeeklySchedule from '../../components/WeeklySchedule.vue'

const stats = ref<OverviewStats | null>(null)
const cardIcons = [School, Notebook, DocumentChecked, DataAnalysis]

const statusOption = computed<EChartsOption>(() => ({
  color: ['#c48a2b', '#1f6b55'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '45%'],
      data: stats.value?.submission_status || [],
      label: { formatter: '{b}: {c}' }
    }
  ]
}))

const courseGradeOption = computed<EChartsOption>(() => ({
  color: ['#1f6b55'],
  tooltip: { trigger: 'axis' },
  grid: { top: 36, right: 18, bottom: 34, left: 42 },
  xAxis: { type: 'category', data: stats.value?.grade_by_course.map((item) => item.course) || [] },
  yAxis: { type: 'value', min: 0, max: 100 },
  series: [{ name: '平均分', type: 'bar', data: stats.value?.grade_by_course.map((item) => item.average) || [], barWidth: 34 }]
}))

const courseOption = computed<EChartsOption>(() => ({
  color: ['#1f6b55', '#ce6d55'],
  tooltip: { trigger: 'axis' },
  legend: { top: 0 },
  grid: { top: 42, right: 18, bottom: 30, left: 42 },
  xAxis: { type: 'category', data: stats.value?.course_assignment_counts.map((item) => item.course) || [] },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    { name: '作业数', type: 'bar', data: stats.value?.course_assignment_counts.map((item) => item.assignments) || [] },
    { name: '提交数', type: 'bar', data: stats.value?.course_assignment_counts.map((item) => item.submissions) || [] }
  ]
}))

async function loadData() {
  stats.value = await getOverviewStats()
}

onMounted(loadData)
</script>
