<template>
  <section class="dashboard-view" :class="{ 'admin-dashboard': isAdmin }">
    <template v-if="isAdmin">
      <div class="page-head">
        <div>
          <h2>运行概览</h2>
          <p>汇总系统用户、课程状态与最近操作记录。</p>
        </div>
        <el-button :icon="Refresh" class="refresh-button" @click="loadData">刷新</el-button>
      </div>

      <div class="stat-grid admin-stat-grid">
        <StatCard
          v-for="(card, index) in stats?.cards || []"
          :key="card.label"
          :label="card.label"
          :value="card.value"
          :trend="card.trend"
          :icon="adminCardIcons[index % adminCardIcons.length]"
        />
      </div>

      <div class="admin-chart-grid">
        <ChartPanel title="用户角色分布" subtitle="按学生、教师、管理员统计" :option="roleOption" />
        <ChartPanel title="课程状态统计" subtitle="按排课状态与作业覆盖统计" :option="courseStatusOption" />
      </div>

      <section class="admin-log-panel">
        <header>
          <div>
            <h3>最近操作日志</h3>
            <p>记录课程、用户、作业、提交与系统配置的最近变更。</p>
          </div>
          <span>{{ stats?.operation_logs.length || 0 }} 条</span>
        </header>
        <div class="admin-log-table">
          <div class="admin-log-header">
            <span>时间</span>
            <span>操作人</span>
            <span>操作内容</span>
            <span>所属模块</span>
          </div>
          <article v-for="log in stats?.operation_logs || []" :key="log.id" class="admin-log-row">
            <time>{{ formatDateTime(log.created_at) }}</time>
            <div class="admin-log-operator">
              <span>{{ log.operator.slice(0, 1) }}</span>
              <div>
                <strong>{{ log.operator }}</strong>
                <small>{{ log.operator_role }}</small>
              </div>
            </div>
            <div class="admin-log-action">
              <span class="admin-log-marker" :class="`tone-${log.tone}`"></span>
              <div>
                <strong>{{ log.action }}</strong>
                <small>{{ log.detail || '暂无详情' }}</small>
              </div>
            </div>
            <el-tag class="admin-module-tag" :class="`tone-${log.tone}`">{{ log.module }}</el-tag>
          </article>
          <div v-if="!stats?.operation_logs.length" class="admin-log-empty">暂无操作日志</div>
        </div>
      </section>
    </template>

    <template v-else>
      <div class="page-head">
        <div>
          <h2>运行概览</h2>
          <p>汇总课程、作业、提交、批改和课程成绩分布。</p>
        </div>
        <el-button :icon="Refresh" class="refresh-button" @click="loadData">刷新</el-button>
      </div>

      <div class="stat-grid">
        <StatCard
          v-for="(card, index) in stats?.cards || []"
          :key="card.label"
          :label="card.label"
          :value="card.value"
          :trend="card.trend"
          :icon="courseCardIcons[index % courseCardIcons.length]"
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
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { DataAnalysis, DocumentChecked, Notebook, Refresh, School, User } from '@element-plus/icons-vue'
import type { EChartsOption } from 'echarts'
import { getOverviewStats } from '../../api/statistics'
import type { OverviewStats } from '../../api/types'
import ChartPanel from '../../components/ChartPanel.vue'
import StatCard from '../../components/StatCard.vue'
import WeeklySchedule from '../../components/WeeklySchedule.vue'
import { useAuthStore } from '../../stores/auth'
import { formatDateTime } from '../../utils/time'

const auth = useAuthStore()
const stats = ref<OverviewStats | null>(null)
const isAdmin = computed(() => auth.user?.role === 'admin')
const courseCardIcons = [School, Notebook, DocumentChecked, DataAnalysis]
const adminCardIcons = [User, School, DataAnalysis, Notebook]

const glassText = '#10284a'
const glassMuted = 'rgba(16, 40, 74, 0.62)'
const glassGrid = 'rgba(255, 255, 255, 0.58)'
const glassAxis = 'rgba(62, 115, 178, 0.32)'
const roleTotal = computed(() => stats.value?.role_distribution.reduce((total, item) => total + item.value, 0) || 0)
const tooltipStyle = {
  backgroundColor: 'rgba(238, 248, 255, 0.78)',
  borderColor: 'rgba(255, 255, 255, 0.86)',
  borderWidth: 1,
  textStyle: { color: glassText },
  extraCssText:
    'border-radius:14px;box-shadow:0 16px 38px rgba(54,108,174,.22),inset 0 1px 0 rgba(255,255,255,.78);backdrop-filter:blur(18px) saturate(170%);'
}

const blueBar = {
  type: 'linear' as const,
  x: 0,
  y: 0,
  x2: 0,
  y2: 1,
  colorStops: [
    { offset: 0, color: '#62c7ff' },
    { offset: 0.34, color: '#128cff' },
    { offset: 1, color: '#0864f7' }
  ]
}

const coralBar = {
  type: 'linear' as const,
  x: 0,
  y: 0,
  x2: 0,
  y2: 1,
  colorStops: [
    { offset: 0, color: '#ff9d7f' },
    { offset: 0.44, color: '#ff5d48' },
    { offset: 1, color: '#ee321f' }
  ]
}

const greenBar = {
  type: 'linear' as const,
  x: 0,
  y: 0,
  x2: 0,
  y2: 1,
  colorStops: [
    { offset: 0, color: '#67f2b0' },
    { offset: 0.42, color: '#2bd878' },
    { offset: 1, color: '#16a85a' }
  ]
}

const orangeBar = {
  type: 'linear' as const,
  x: 0,
  y: 0,
  x2: 0,
  y2: 1,
  colorStops: [
    { offset: 0, color: '#ffc46d' },
    { offset: 0.45, color: '#ff9f3d' },
    { offset: 1, color: '#f07425' }
  ]
}

const violetBar = {
  type: 'linear' as const,
  x: 0,
  y: 0,
  x2: 0,
  y2: 1,
  colorStops: [
    { offset: 0, color: '#c6a7ff' },
    { offset: 0.42, color: '#936dff' },
    { offset: 1, color: '#6747e8' }
  ]
}

const chartAxis = {
  axisLine: { lineStyle: { color: glassAxis } },
  axisTick: { lineStyle: { color: glassAxis } },
  axisLabel: { color: glassText, fontWeight: 600 }
}

const valueAxis = {
  ...chartAxis,
  splitLine: { lineStyle: { color: glassGrid } }
}

const roleOption = computed<EChartsOption>(() => ({
  color: ['#1b8cff', '#ffad4b', '#976cff'],
  tooltip: { trigger: 'item', ...tooltipStyle },
  title: {
    text: String(roleTotal.value),
    subtext: '总用户数',
    left: '32%',
    top: '39%',
    textAlign: 'center',
    textStyle: { color: glassText, fontSize: 28, fontWeight: 850 },
    subtextStyle: { color: glassMuted, fontSize: 12, fontWeight: 650 }
  },
  legend: {
    orient: 'vertical',
    right: 18,
    top: 'middle',
    icon: 'circle',
    itemWidth: 10,
    itemHeight: 10,
    textStyle: { color: glassText, fontWeight: 650 }
  },
  series: [
    {
      name: '用户角色',
      type: 'pie',
      radius: ['46%', '72%'],
      center: ['33%', '50%'],
      data: stats.value?.role_distribution || [],
      label: { formatter: '{d}%', color: '#ffffff', fontWeight: 850 },
      labelLine: { show: false },
      itemStyle: {
        borderColor: 'rgba(236, 250, 255, 0.95)',
        borderWidth: 2,
        shadowBlur: 18,
        shadowColor: 'rgba(0, 122, 255, 0.28)'
      }
    }
  ]
}))

const courseStatusOption = computed<EChartsOption>(() => {
  const colors = [blueBar, greenBar, orangeBar, violetBar]
  return {
    tooltip: { trigger: 'axis', ...tooltipStyle },
    grid: { top: 28, right: 18, bottom: 34, left: 42, containLabel: true },
    xAxis: { type: 'category', data: stats.value?.course_status.map((item) => item.name) || [], ...chartAxis },
    yAxis: { type: 'value', minInterval: 1, ...valueAxis },
    series: [
      {
        name: '课程数',
        type: 'bar',
        data:
          stats.value?.course_status.map((item, index) => ({
            value: item.value,
            itemStyle: { color: colors[index % colors.length] }
          })) || [],
        barWidth: 48,
        label: { show: true, position: 'top', color: glassText, fontWeight: 850 },
        itemStyle: {
          borderRadius: [9, 9, 3, 3],
          borderColor: 'rgba(232, 249, 255, 0.9)',
          borderWidth: 1,
          shadowBlur: 18,
          shadowColor: 'rgba(0, 122, 255, 0.22)'
        }
      }
    ]
  }
})

const statusOption = computed<EChartsOption>(() => ({
  color: ['#ffaf20', '#34d878'],
  tooltip: { trigger: 'item', ...tooltipStyle },
  legend: {
    bottom: 0,
    icon: 'circle',
    itemWidth: 10,
    itemHeight: 10,
    textStyle: { color: glassText, fontWeight: 600 }
  },
  series: [
    {
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '45%'],
      data: stats.value?.submission_status || [],
      label: { formatter: '{b}: {c}', color: glassText, fontWeight: 650 },
      labelLine: { lineStyle: { color: 'rgba(36, 82, 137, 0.42)' } },
      itemStyle: {
        borderColor: 'rgba(232, 249, 255, 0.92)',
        borderWidth: 2,
        shadowBlur: 18,
        shadowColor: 'rgba(51, 194, 117, 0.28)'
      }
    }
  ]
}))

const courseGradeOption = computed<EChartsOption>(() => ({
  color: ['#007aff'],
  tooltip: { trigger: 'axis', ...tooltipStyle },
  grid: { top: 36, right: 18, bottom: 34, left: 42, containLabel: true },
  xAxis: { type: 'category', data: stats.value?.grade_by_course.map((item) => item.course) || [], ...chartAxis },
  yAxis: { type: 'value', min: 0, max: 100, ...valueAxis },
  series: [
    {
      name: '平均分',
      type: 'bar',
      data: stats.value?.grade_by_course.map((item) => item.average) || [],
      barWidth: 42,
      itemStyle: {
        color: blueBar,
        borderRadius: [8, 8, 2, 2],
        borderColor: 'rgba(202, 240, 255, 0.86)',
        borderWidth: 1,
        shadowBlur: 18,
        shadowColor: 'rgba(0, 122, 255, 0.34)'
      }
    }
  ]
}))

const courseOption = computed<EChartsOption>(() => ({
  color: ['#007aff', '#ff3b30'],
  tooltip: { trigger: 'axis', ...tooltipStyle },
  legend: {
    top: 0,
    itemWidth: 20,
    itemHeight: 12,
    textStyle: { color: glassText, fontWeight: 600 }
  },
  grid: { top: 42, right: 18, bottom: 30, left: 42, containLabel: true },
  xAxis: { type: 'category', data: stats.value?.course_assignment_counts.map((item) => item.course) || [], ...chartAxis },
  yAxis: { type: 'value', minInterval: 1, ...valueAxis },
  series: [
    {
      name: '作业数',
      type: 'bar',
      data: stats.value?.course_assignment_counts.map((item) => item.assignments) || [],
      barWidth: 42,
      itemStyle: {
        color: blueBar,
        borderRadius: [8, 8, 2, 2],
        borderColor: 'rgba(202, 240, 255, 0.86)',
        borderWidth: 1,
        shadowBlur: 18,
        shadowColor: 'rgba(0, 122, 255, 0.34)'
      }
    },
    {
      name: '提交数',
      type: 'bar',
      data: stats.value?.course_assignment_counts.map((item) => item.submissions) || [],
      barWidth: 42,
      itemStyle: {
        color: coralBar,
        borderRadius: [8, 8, 2, 2],
        borderColor: 'rgba(255, 223, 211, 0.9)',
        borderWidth: 1,
        shadowBlur: 16,
        shadowColor: 'rgba(255, 91, 70, 0.32)'
      }
    }
  ]
}))

async function loadData() {
  stats.value = await getOverviewStats()
}

onMounted(loadData)
</script>
